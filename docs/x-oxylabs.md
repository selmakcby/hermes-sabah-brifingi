# X'ten (Twitter) veri çekme: Oxylabs AI Studio ile

## Sorun

Lokalde ajan X'i tarayıcıdan, benim açık oturumumla tarıyordu. Bu iki
sebeple sunucuya taşınamaz:

1. Sunucuda açık bir tarayıcı oturumu yok.
2. 7/24 çalışan bir ajana kişisel hesabın oturumunu vermek hesabın
   askıya alınmasıyla biter. X'in resmî API'sinin okuma katmanı da pahalı.

İlk denemede ajan "X'te son 24 saatin önemli tweetlerini getir" yaklaşımıyla
hiçbir şey bulamadı: arama sayfası giriş istiyor, arama motoru da zaman
filtresi uygulamıyor.

## Çözüm (videodaki)

Oxylabs AI Studio'nun iki aracı birlikte:

1. **AI-Search**: arama motoruna `site:x.com` + konu anahtar kelimeleri
   gönderilir, gerçek tweet linkleri (`x.com/.../status/...`) toplanır.
   Tekil tweet sayfaları giriş istemez; giriş isteyen tek şey X'in kendi
   arama sayfasıdır, o yüzden arama bu adımda dışarıdan yapılır.
2. **AI-Scraper**: her tweet linki tek tek açılır, metin / yazar / tarih çıkarılır.
3. Tarih filtresi script içinde uygulanır. Arama motoru eski ve viral
   tweetleri de getirdiği için pencere geniş tutulur (30 gün) ve brifingde
   her X maddesinin yanına tarihi yazılır. Bölümün adı bu yüzden "X'te
   konuşulanlar", "bugün X'te ne oldu" değil.

Bu akış `scripts/x_oxylabs_cek.py` içinde; tarif (`skills/toplayici.md`)
onu çağırır ve ham çıktıyı `data/x_ham/YYYY-MM-DD.json` olarak arşivler.

## 1. API anahtarını al

1. https://aistudio.oxylabs.io adresine gir, hesap aç. Hostinger'ın Hermes
   planında AI Studio kredisi tanımlı geliyor; ayrıca ücretsiz deneme kredisi var.
2. API key sayfası: https://aistudio.oxylabs.io/api-key
3. Anahtarı kopyala. Bu anahtar AI Studio'ya aittir; Oxylabs'ın klasik Web
   Scraper API'si (kullanıcı adı + şifre) ayrı bir üründür, karıştırma.

## 2. Anahtarı Hermes'e ver

Hermes paneli → **Keys** → custom key ekle:

```
OXYLABS = <anahtar>
```

Anahtar `/opt/data/.env` dosyasına yazılır, sohbete yapıştırılmaz.
Değişkenin adı `OXYLABS`; script bu ismi arar.

## 3. Paketi kur

Sunucuda proje kökünde bir sanal ortam ve SDK gerekiyor. Hermes Chat'e
yazdırabilirsin ya da terminalden:

```bash
cd /opt/data/sabah-brifingi
python3 -m venv .venv
source .venv/bin/activate
pip install oxylabs-ai-studio
```

Deneme:

```bash
source .venv/bin/activate && python3 scripts/x_oxylabs_cek.py --saat 720
```

Çıktı JSON: `{"tweets": [...], "errors": [...], "atlandi": false}`.
Anahtar yoksa ya da paket kurulu değilse script hata fırlatmaz,
`"atlandi": true` döner; tarif o durumda X bölümünü atlar ve bunu açıkça yazar.

## 4. Ajana söyle

prompts/PROMPTLAR.md, prompt 6. Ajan tarifin X adımını bu script'e göre
güncelledi; repodaki `skills/toplayici.md` VPS'teki son hâli.

## 5. Kredi

- Her arama ve her sayfa çekimi kredi harcar. Script 5 eksen × 15 sonuç
  arar, sonra sadece tweet linklerini açar. Günlük maliyet küçük.
- Kurulum sırasında deneme yaparken normalden fazla kredi gider; normal.
- Kullanımı aistudio.oxylabs.io panelinden takip et: hangi istek ne harcadı görünür.

## Alternatif: Oxylabs'ın resmî Hermes eklentisi

Script yerine Hermes'in web araçlarını Oxylabs'a bağlamak da mümkün.
Bu yolda değişken adı `OXYLABS_API_KEY`:

```bash
hermes plugins install oxylabs/hermes-web-oxylabs --enable
hermes config set web.search_backend oxylabs
hermes config set web.extract_backend oxylabs
hermes restart
```

Belgeler: https://developers.oxylabs.io/products/ai-studio ·
https://developers.oxylabs.io/integrations/ai-studio-integrations/hermes-agent
