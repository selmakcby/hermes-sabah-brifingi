---
name: toplayici
description: Sabah brifingi topla dendiginde AI gundemini derler.
---

# Sabah Brifingi Topla

Sabah brifingini toplayan, yazan ve kaydeden tarif. "Sabah brifingi topla",
"bugünün brifingi", "günaydın brifing" dendiğinde bu tarif uygulanır.

Proje kökü: /opt/data/sabah-brifingi
Tüm göreli yollar bu köke göredir.

## Ne zaman çalışır

- Kullanıcı açıkça istediğinde ("sabah brifingi topla")
- Zamanlanmış sabah işi tetiklediğinde

## Çıktı sözleşmesi (kesin)

- Dosya: data/briefings/YYYY-MM-DD.md (bugünün yerel tarihi)
- Türkçe, en fazla 10 madde TOPLAM, iki bölüme ayrılır:
  - "## Gündem" — RSS ve web_search kaynaklı maddeler
  - "## X'te konuşulanlar" — X taramasından (adım 1) gelen maddeler.
    NOT: bu bölüm "bugün X'te ne oldu" DEĞİL, "X'te konuyla ilgili güncel
    olmayabilecek öne çıkanlar" anlamına gelir (Oxylabs zaman filtresi
    yapmıyor). Her madde MUTLAKA kendi tarihini parantez içinde gösterir.
- Her madde: TEK cümle + sonunda kaynak linki
- X bölümündeki her madde X'ten gelmelidir (tweet linki `x.com/.../status/...`
  ya da o tweet'in atıfta bulunduğu haber linki). RSS/web maddesini X
  bölümüne koyma, X maddesini Gündem'e koyma — kaynak karışmaz.
- X'ten hiçbir madde seçilmediyse bölüm başlığı yine de kalır, altına
  tek satır: "(bugün X'te öne çıkan yeni bir şey bulunamadı)"
- Kullanıcıya gönderilen mesaj SADECE bu brifingdir
- Brifing dışında hiçbir şey eklenmez: içerik önerisi yok, "istersen
  şundan video çıkaralım" yok, analiz özeti yok. Bu bir kural, tercih değil.

## Adımlar

### 0. Tekrar üretim kontrolü (idempotans)

`read_file` ile data/briefings/<bugün>.md var mı bak.
- Varsa: yeniden üretme. Mevcut dosyayı oku ve onu sun. Burada dur.
- Yoksa: devam et.
Tamamlanma ölçütü: bugünün dosyasının var/yok durumu kesin biliniyor.

### 1. X / AI gündemini topla (Oxylabs AI Studio, tarayıcı YOK)

X taraması artık tarayıcı oturumu (`browser_exec`/x.com login) kullanmaz.
Bunun yerine Oxylabs AI Studio API'si kullanılır: önce `AI-Search` ile
ilgili eksenlerde gerçek tweet linkleri (`x.com/.../status/...`) bulunur,
sonra her link `AI-Scraper` ile tek tek açılıp metin/yazar/tarih çıkarılır
(tekil tweet sayfaları genelde login duvarına takılmaz; login gerektiren
tek şey arama sayfasıdır, o yüzden arama adımı için AI-Search kullanılır).

```
terminal(command="source .venv/bin/activate && python3 scripts/x_oxylabs_cek.py --saat 720", workdir="/opt/data/sabah-brifingi")
```

Önemli: Oxylabs AI-Search'ün zaman ifadesi gerçek bir filtre değil (arama
motoru konuyla alakalı ama eski/viral tweetleri de döndürüyor — test
edildi, haftalar/aylar önceki tweetler "trend" diye geldi). Bu yüzden
pencere çok geniş tutulur (30 gün = 720 saat) ve `tarih` alanı her X
maddesinin YANINA parantez içinde MUTLAKA eklenir (örnek: "... (12 Ağu
2026)"). Bu bölüm "bugünün X gündemi" değil, "X'te konuyla ilgili
öne çıkanlar" olarak sunulur.

Kimlik doğrulama `OXYLABS` ortam değişkeninden okunur (Oxylabs AI Studio
API key — klasik Web Scraper API / Realtime API DEĞİL, farklı bir üründür,
basic auth kullanmaz). Script bu değişkeni bulamazsa ya da
`oxylabs_ai_studio` paketi kurulu değilse `atlandi: true` ile sessizce
boş sonuç döner.

Script çıktısı JSON: `{"tweets": [...], "errors": [...], "atlandi": bool}`
Her tweet öğesi: `{"metin", "yazar", "tarih", "link"}`. `tarih` zaten
son N saat (varsayılan 7 gün) penceresine göre script içinde
filtrelenmiştir — ama bu pencere Oxylabs AI-Search'ün GERÇEK bir zaman
filtresi olmamasını telafi etmek için geniş tutulur; script dışında ekstra
tarih kontrolüne gerek yok, sadece şüpheli görünen bir tarihi (ör. gelecek
tarih) yine de brifinge alma.

X bölümündeki her maddenin SONUNDA link yanına parantez içinde tweet
tarihi de yazılır (ör. "... <link> (12 Ağu 2026)") — bu madde "bugün"
olduğu izlenimi vermesin diye zorunludur, tek istisnası tweet gerçekten
son 24 saat içindeyse tarihi eklemek isteğe bağlıdır.

- `atlandi: true` ise ya da `tweets` boşsa: X bölümü atlanır. Brifingde
  "## X'te konuşulanlar" başlığı yine de kalır, altına tek satır:
  "(X bölümü atlandı — Oxylabs API'den bugüne ait doğrulanmış içerik
  gelmedi)". Uydurma yok, tahmini tweet yok.
- `errors` doluysa (bazı linkler hata verdi ama bazı tweetler geldiyse):
  hata veren linkleri sessizce atla, gelen tweetlerle devam et.
- Script tamamen çalışmazsa (exception, kurulum eksik, `OXYLABS` yok):
  aynı şekilde X bölümü atlanır ve neden kısaca not düşülür; kullanıcıya
  "X araması yapılamadı: <kısa sebep>" diye açıkça bildirilir, tahmin
  edilmez.

Tamamlanma ölçütü: script çalıştırıldı, çıktısı JSON olarak alındı
(boş/atlandı da geçerli bir sonuçtur), her tweet'in tarihi ve linki
kontrol edildi.

Ham çıktıyı arşivle: script'in tam JSON çıktısını
`data/x_ham/YYYY-MM-DD.json` olarak `write_file` ile kaydet. Bu,
brifinge hangi tweet'lerin elendiğini sonradan denetleyebilmek içindir;
kullanıcıya gönderilmez, sadece diske yazılır.
Tamamlanma ölçütü: data/x_ham/<bugün>.json diskte var.

### 2. RSS başlıklarını çek

RSS.txt içindeki adreslerden bugünün başlıklarını al:

```
terminal(command="python3 scripts/rss_cek.py", workdir="/opt/data/sabah-brifingi")
```

Script RSS.txt'yi okur, boş satırları ve `#` ile başlayan yorumları
atlar, her feed'den bugünün öğelerini JSON olarak basar.

- RSS.txt boşsa: RSS adımını atla, sadece web aramasıyla devam et ve
  brifingin sonuna tek satır not düş: "(RSS listesi boş — RSS.txt)"
- Bir feed hata verirse: onu atla, diğerlerini işlemeye devam et, hata veren
  feed'i brifingin sonunda tek satırda belirt.

Tamamlanma ölçütü: script çalıştı, çıktısı elde edildi (boş liste de geçerli
bir sonuçtur).

### 3. Brifingi yaz

Adım 1 ve 2'nin çıktısını birleştir, ele:

- Aynı olayın farklı kaynaklardan tekrarını tek maddede birleştir. İstisna:
  konu HEM X'te HEM RSS/web'de çıktıysa ve X tarafında kendine özgü bir
  tepki/tartışma varsa iki ayrı madde olarak (biri Gündem'de, biri X'te)
  kalabilir; salt aynı haberin tekrarıysa tek maddede birleştir ve
  Gündem'e koy.
- Önem sırasına diz: büyük duyuru / model çıkışı > tartışma > söylenti
- X bölümünde en az 4 madde hedeflenir (script 5 eksende ve eksen
  başına 15 arama sonucuyla çalışıyor, bu genelde yeterli). 4'ten az
  geldiyse zorlama, ama gelen maddeleri ÖNEM SIRASINA göre diz: büyük
  model/ürün duyurusu > fiyat/strateji haberi > genel tartışma/görüş >
  kişisel anekdot. Sadece rastgele sırada bırakma.
- En fazla 10 madde TOPLAM (iki bölüm birlikte). 10'dan azsa zorlama, az
  madde uzun brifingden iyidir.
- Her madde tek cümle, Türkçe, sade. Reklam dili yok.
- Her maddenin sonunda kaynak linki

Biçim:

```markdown
# Sabah Brifingi — YYYY-MM-DD

## Gündem

1. <Tek cümlelik başlık.> <https://link>
2. <Tek cümlelik başlık.> <https://link>
...

## X'te konuşulanlar

1. <Tek cümlelik başlık.> <https://x.com/.../status/...> (12 Ağu 2026)
2. <Tek cümlelik başlık.> <https://x.com/.../status/...> (3 Eyl 2026)
...
```

Tamamlanma ölçütü: her madde tek cümle, her maddede tam bir link var,
madde sayısı ≤ 10, iki bölüm başlığı da mevcut, X bölümündeki linkler
gerçekten X kaynaklı.

### 4. Kaydet

`write_file` ile data/briefings/YYYY-MM-DD.md dosyasına yaz.
Tamamlanma ölçütü: dosya diskte var ve içeriği brifingin tamamı.

### 5. Analizciyi çalıştır

Son adım: `analizci` skill'ini uygula (skill_view(name='analizci')).
Analizin çıktısı kullanıcıya GÖNDERİLMEZ — sessizce data/analiz.md'ye eklenir.
Tamamlanma ölçütü: data/analiz.md bugünün tarihli bir bölümüyle güncellendi.

## Tuzaklar

- Analiz sonucunu brifinge iliştirme. Brifing ve analiz ayrı kanallardır.
- Adım 5'i atlama; analiz birikimi üreticinin tek girdisidir.
- Tarihi eski haberi "bugün" diye yazma; kaynak tarihini doğrula.
- API key gerekiyorsa yalnızca .env'den oku. Hiçbir key'i brifing, analiz,
  log ya da başka bir dosyaya yazma.
- RSS.txt'ye yorum eklerken `#` kullan, parantez `( )` kullanma — script
  parantezli satırı geçerli URL sanıp çöker (yaşanmış hata).
- Oxylabs script'i hata verirse ya da `atlandi: true` dönerse tahmin etme /
  uydurma; X bölümünü atla ve bunu brifing sonunda açıkça belirt.
- `OXYLABS` anahtarını asla loglama, brifinge/analize/x_ham dosyasına yazma
  — sadece ortam değişkeninden okunur.
- RSS/web maddesini X bölümüne, X maddesini Gündem bölümüne karıştırma —
  kaynağı doğrulamadan bölüm seçme.

## Doğrulama

- data/briefings/<bugün>.md okunabiliyor ve ≤ 10 madde içeriyor
- Brifingde "## Gündem" ve "## X'te konuşulanlar" başlıkları ikisi de var
- X bölümündeki linkler gerçekten X/tweet kaynaklı
- data/analiz.md'de bugünün tarihli bölümü var
- Kullanıcıya giden mesaj sadece brifing metni
