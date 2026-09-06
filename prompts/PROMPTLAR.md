# Videoda kullandığım promptlar

Sırayla: önce lokalde Claude Code ile proje kurulur, sonra proje zip'lenip
Hostinger'daki Hermes Agent'a yüklenir, orada model/Telegram/cron bağlanır.
Promptlar kopyala-yapıştır için düz metin.

---

## 1. Claude Code: projeyi kur (lokal)

Boş bir klasörde `claude` yazıp bunu yapıştır:

```
Sabah brifingi ajanı kuruyoruz. Bu klasörde şu yapıyı oluştur:

1. skills/toplayici.md — "Sabah Brifingi Topla" tarifi:
   - X'te bugün konuşulan AI gündemini topla ("AI agents", "Claude",
     "yapay zeka" eksenlerinde; tarihi doğrula, eski sonucu alma)
   - RSS.txt dosyasındaki RSS adreslerinden bugünün başlıklarını çek
   - Hepsini kısa, okunur bir Türkçe brifinge çevir:
     en fazla 10 madde, her madde tek cümle + link
   - Brifingi data/briefings/YYYY-MM-DD.md dosyasına kaydet
   - Aynı brifingi Telegram mesajı olarak göndermeye uygun biçimde çıktıla
   - Son adımda skills/analizci.md tarifini çalıştır

2. skills/analizci.md — "Brifing Analizi" tarifi:
   - Yeni brifingi son 14 günün brifingleriyle karşılaştır
   - Tekrar edenleri, yükselenleri, sönenleri data/analiz.md'ye EKLE
   - Bu analizi bana ASLA gönderme; sadece dosyaya yaz

3. skills/uretici.md — "Birikimden İçerik Üret" tarifi:
   - SADECE ben açıkça istediğimde çalışır, kendiliğinden teklif etmez
   - data/briefings/ altındaki brifingleri ve data/analiz.md'yi oku
   - İstenen formatta içerik çıkar (video fikri / X yazısı)
   - Hangi günlerin brifinginden yararlandığını belirt

4. RSS.txt — RSS listem için şablon (ben dolduracağım)
5. scripts/rss_cek.py — RSS.txt'deki adreslerden bugünün öğelerini çeken,
   sadece standart kütüphane kullanan küçük bir script
6. data/briefings/ klasörü ve data/analiz.md
7. README.md — sistemin bir paragraflık özeti

Kurallar: API anahtarları sadece .env'den okunur, asla dosyalara yazılmaz.
Her tarif tek başına çalışabilir olmalı. Tarifler düz Türkçe, kod değil.
```

## 2. Claude Code: kuru test

```
Şimdi toplayici tarifini test et: X'te bugün konuşulanları ara,
RSS.txt'deki RSS'leri çek ve bugünün brifinginin önizlemesini bana
burada göster. Henüz hiçbir yere gönderme.
```

Videoda bu adımda X taraması tarayıcı oturumuyla çalıştı (lokalde). Sunucuda
bu mümkün değil; bkz. prompt 6.

## 3. Claude Code: X maddelerini ayır

```
Bundan sonra X'ten çekilen bilgilerden önemli olanları brifing içinde
ayrı bir bölüm açıp "X'te konuşulanlar" diye ayır. Yeteneği de buna
göre güncelle.
```

## 4. Hermes (VPS): projeyi yerleştir

Proje klasörünü zip'le, Hermes panelinde Files → yükle. Sonra Chat'te:

```
Home klasöründe sabah-brifingi.zip var. Aç, yerleştir, kur.
Bu bizim yeni projemiz. skills/ altındaki tarifleri oku ve
ne yaptıklarını bir cümleyle özetle.
```

## 5. Hermes (VPS): X kısmını tek başına test et

```
Sadece X kısmını test etmek istiyorum: toplayici tarifindeki
X adımını çalıştır, bugün X'te konuşulan 5 şeyi linkleriyle getir.
Tarayıcı oturumu isteme; elinde ne varsa onunla dene ve neyin
çalışmadığını açıkça söyle.
```

İlk denemede ajan "tarayıcı oturumu başlatılamadı" diye döndü. Beklenen
sonuç bu; kişisel hesapla giriş istemiyoruz.

## 6. Hermes (VPS): X'i Oxylabs ile çek

Önce Keys sayfasına `OXYLABS` anahtarını ekle (docs/x-oxylabs.md). Sonra:

```
Yeni bir anahtar ekledim: OXYLABS (Oxylabs AI Studio API key).
Artık X'teki bilgileri kişisel hesap ya da tarayıcı yerine bu API
üzerinden çekeceksin: arama motoruyla x.com sayfalarını bul, tweet
metnini ve tarihini çek, bugüne ait olmayanları ele.
skills/toplayici.md tarifinin X adımını buna göre güncelle,
sonra tek bir deneme yap ve sonucu göster.
```

Ajanın bulduğu çözüm: AI-Search ile tweet linklerini bul, AI-Scraper ile tek
tek aç, tarihi script içinde ele ve brifingde her maddenin yanına yaz.
Repodaki `skills/toplayici.md` ve `scripts/x_oxylabs_cek.py` bu çözüm.

## 7. Hermes (VPS): sabah bildirimi cron'u

Cron sayfası → Create. Ad: `Sabah Bildirimi`, zamanlama: her gün 05:30,
teslim kanalı: Telegram. Prompt:

```
Toplayıcı yeteneğini çalıştır (skills/toplayici.md). Bugünün
brifingini hazırla, data/briefings/ altına kaydet ve bana Telegram'dan
sadece brifing metnini gönder. Analizciyi çalıştır ama analizi gönderme.
```

## 8. Telegram'dan istek üzerine içerik (on-demand)

```
Birikmiş brifinglere ve analize bak: bu hafta hangi konular tekrar
etti? Bana bu haftanın trendlerinden bir X yazısı çıkar, kaynak
günleri belirt.
```
