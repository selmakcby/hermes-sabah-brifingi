---
name: uretici
description: Sadece açıkça istendiğinde brifing birikiminden içerik üretir.
---

# Birikimden İçerik Üret

Biriken brifing ve analizlerden istenen formatta içerik çıkaran tarif.

Proje kökü: /opt/data/sabah-brifingi

## Ne zaman çalışır

SADECE kullanıcı açıkça istediğinde. Örnek tetikleyiciler:
- "birikimden içerik üret"
- "buradan bir video fikri çıkar"
- "bu haftadan X yazısı yaz"
- "uretici'yi çalıştır"

## Ne zaman ÇALIŞMAZ (kesin)

- Sabah brifinginin ardından kendiliğinden
- Analizde ilginç bir örüntü çıktığı için
- "İstersen şuna content çıkarayım" diye teklif ederek

Teklif edilmez, önerilmez, ima edilmez. Kullanıcı istemedikçe bu tarif yoktur.

## Adımlar

### 1. Formatı netleştir

Kullanıcı format belirtmişse (video fikri / X yazısı / başka) onu kullan.
Belirtmemişse tek bir soru sor: hangi format ve hangi tarih aralığı.
Varsayımla üretme.
Tamamlanma ölçütü: format ve zaman aralığı belli.

### 2. Birikimi oku

- `search_files(pattern='*.md', target='files', path='data/briefings')` ile
  tüm brifingleri listele, istenen aralıktakileri `read_file` ile oku
- `read_file` ile data/analiz.md'yi tamamen oku

Analiz dosyası hangi konunun tekrar ettiğini ve yükseldiğini zaten söylüyor;
seçimini buna dayandır, tek bir günün brifingine değil.
Tamamlanma ölçütü: okunan brifing dosyalarının listesi ve analiz.md elde
edildi.

### 3. Üret

Format kalıpları:

**Video fikri**
```markdown
### Başlık
<merak uyandıran, tıklama tuzağı olmayan başlık>

**Tek cümlelik fikir:** <...>

**Neden şimdi:** <analizden gelen yükseliş kanıtı>

**Anlatım iskeleti**
1. Kanca — <...>
2. Bağlam — <...>
3. Ana argüman — <...>
4. Karşı görüş — <...>
5. Kapanış — <...>

**Kaynaklar:** <linkler>
```

**X yazısı**
```markdown
<140-280 karakter, tek fikir, Türkçe, emoji yok, hashtag yok>

(varsa devam tweetleri numaralı)
```

Kurallar:
- Türkçe, sade, kullanıcının sesi: iddialı ama abartısız
- Uydurma yok. Brifingde olmayan bir olayı yazma.
- Reklam dili yok ("devrim niteliğinde", "çığır açan" gibi)

Tamamlanma ölçütü: istenen formatta tam bir çıktı üretildi.

### 4. Kaynak günleri belirt (zorunlu)

Çıktının sonuna hangi brifinglerden yararlanıldığını yaz:

```markdown
---
Kaynak brifingler: 2026-09-01, 2026-09-02, 2026-09-03
Analiz katkısı: <analiz.md'deki hangi bulgu bu fikri seçtirdi>
```

Her madde için hangi günün brifinginden geldiği izlenebilir olmalı.
Tamamlanma ölçütü: kullanılan her brifing tarihi listede.

## Tuzaklar

- İstenmeden çalıştırmak bu sistemin tek kırmızı çizgisi.
- Kaynak gün belirtmeyi atlama; izlenebilirlik çıktının yarısı.
- Tek günün brifinginden üretme; birikim varsa analizden faydalan.
- API key'ler yalnızca .env'den okunur, üretilen içeriğe yazılmaz.

## Doğrulama

- Çıktı istenen formatta
- Kaynak brifing tarihleri listelenmiş
- İçerikteki her olgusal iddia okunan bir brifingde mevcut
