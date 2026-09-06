---
name: analizci
description: Yeni brifingi son 14 günle karşılaştırır, sonucu sessizce data/analiz.md'ye ekler.
---

# Brifing Analizi

Yeni bir brifing kaydedildikten sonra çalışan sessiz analiz tarifi.
Çıktısı kullanıcıya gönderilmez; data/analiz.md'de birikir.

Proje kökü: /opt/data/sabah-brifingi

## Ne zaman çalışır

- skills/toplayici.md'nin son adımı olarak, her yeni brifing kaydından sonra
- Kullanıcı geçmişe dönük bir analiz tazelemesi istediğinde

Ne zaman çalışmaz: kendi başına, brifing olmadan.

## Sessizlik kuralı (kesin)

Bu analizin çıktısı kullanıcıya GÖNDERİLMEZ.
- Sohbete analiz özeti yazma
- "Şu konu yükseliyor, içerik çıkaralım mı" deme
- Brifing mesajına ek yapma

Analiz sadece dosyaya yazılır. Tek istisna: kullanıcı açıkça "analizi göster"
derse dosyayı okuyup sunarsın.

## Adımlar

### 1. Yeni brifingi oku

`read_file` ile data/briefings/<bugün>.md.
Tamamlanma ölçütü: bugünün maddeleri elde edildi.

### 2. Önceki günleri oku

`search_files(pattern='*.md', target='files', path='data/briefings')` ile
dosyaları listele, tarihe göre sırala, bugünden önceki son 14 günü oku.
14'ten az varsa hepsini oku.

- Önceki brifing yoksa: bu ilk gündür. data/analiz.md'ye "ilk brifing,
  karşılaştırma yok, temel çizgi kuruldu" notunu düş ve bitir.

Tamamlanma ölçütü: karşılaştırma penceresi (kaç gün okunduğu) belli.

### 3. Karşılaştır

Üç soruya cevap ver, her biri için somut kanıt (hangi gün, hangi madde):

- **Tekrar edenler:** birden fazla günde geçen konu/aktör/ürün hangileri
- **Yükselenler:** son 2-3 günde geçiş sıklığı ya da önem sırası artanlar
- **Sönenler:** önceki günlerde vardı, bugün ve dünde yok olanlar

Ek olarak varsa not et:
- **Yeni giriş:** bugün ilk kez görünen ve dikkat çeken konu
- **Çelişki:** kaynakların birbirini tutmadığı nokta

Konuları kaba anahtar kelimeyle değil anlamla eşleştir ("Claude 4.5 çıktı" ve
"Anthropic yeni model duyurdu" aynı konudur).

Tamamlanma ölçütü: üç sorunun üçü de yanıtlı; her bulgu en az bir tarihe
dayanıyor.

### 4. data/analiz.md'ye EKLE

Dosyanın sonuna ekle — üzerine YAZMA. Dosya yoksa başlıkla oluştur.

Ekleme biçimi:

```markdown
## YYYY-MM-DD

Pencere: son N gün (YYYY-MM-DD → YYYY-MM-DD)

**Tekrar edenler**
- <konu> — geçtiği günler: YYYY-MM-DD, YYYY-MM-DD

**Yükselenler**
- <konu> — <neden yükseliyor, hangi güne göre>

**Sönenler**
- <konu> — son görüldüğü gün: YYYY-MM-DD

**Yeni giriş**
- <konu>

**Not**
- <varsa çelişki ya da izlenmesi gereken şey>

---
```

Ekleme yöntemi: `read_file` ile mevcut içeriği al, sonuna yeni bölümü
ekleyip `write_file` ile tam dosyayı yaz. Ya da `patch` ile dosya sonundaki
son satırı hedefleyip ekle. Aynı tarih için ikinci bir bölüm oluşturma —
o tarih zaten varsa o bölümü güncelle.

Tamamlanma ölçütü: data/analiz.md'nin önceki tüm bölümleri duruyor ve
sonuna bugünün bölümü eklenmiş.

## Tuzaklar

- data/analiz.md'yi üzerine yazmak birikimi yok eder — hep ekle.
- Aynı gün iki kez çalışırsa tarih bölümünü çoğaltma, güncelle.
- Analizi sohbete sızdırma. Bu tarifin değeri sessiz birikmesinde.
- API key'leri asla analiz dosyasına yazma; yalnızca .env'den okunur.

## Doğrulama

- data/analiz.md'de bugünün tarihli tam olarak bir bölümü var
- Önceki bölümler bozulmamış (dosya kısalmamış)
- Sohbete hiçbir analiz metni yazılmadı
