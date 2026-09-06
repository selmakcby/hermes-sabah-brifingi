# Sabah Brifingi — Hermes Agent + Hostinger VPS

Her sabah 05:30'da uyanan, X'i ve RSS kaynaklarını tarayıp tek bir Türkçe
brifinge indiren, bunu Telegram'a gönderen ve arkada sessizce birikim
yapan bir ajan. Laptop kapalıyken de çalışır, çünkü Hostinger'daki bir
VPS'te yaşıyor.

Video: [Sıfırdan 7/24 Çalışan Yapay Zeka Sistemi Kurdum (Hermes Agent)](https://www.youtube.com/@selma.builds)

VPS: https://hostinger.com/SELMA — kupon **SELMA** ile ek %10 indirim.

## Nasıl çalışıyor

```
05:30  cron uyanır
  │
  ├─ skills/toplayici.md   X (Oxylabs) + RSS → data/briefings/2026-09-06.md → Telegram
  │        └─ son adım: skills/analizci.md  → data/analiz.md'ye sessizce ekler
  │
  └─ (sen istediğinde) skills/uretici.md → birikimden video fikri / X yazısı
```

Üç "yetenek" var, üçü de düz Türkçe tarif, kod değil:

| Yetenek | Ne zaman | Ne yapar |
|---|---|---|
| `skills/toplayici.md` | her sabah (cron) | X (Oxylabs) + RSS'ten en fazla 10 maddelik brifing, Telegram'a gönderir |
| `skills/analizci.md` | her brifingden sonra | son 14 günle karşılaştırır: tekrar eden, yükselen, sönen konular. Sana göndermez, dosyaya yazar |
| `skills/uretici.md` | sadece sen istediğinde | brifing + analiz birikiminden içerik üretir, kaynak günleri belirtir |

Kural: sabahları gelen tek şey brifingdir. Sistem kendiliğinden içerik
önermez. API anahtarları yalnızca `.env`'den okunur, hiçbir dosyaya yazılmaz.

## Klasör yapısı

```
skills/toplayici.md                VPS'teki tarif (X araması Oxylabs ile)
skills/toplayici.lokal-browser.md  lokal sürüm (X araması tarayıcı oturumuyla)
skills/analizci.md
skills/uretici.md
scripts/rss_cek.py                 RSS.txt'den bugünün başlıkları (sadece stdlib)
scripts/x_oxylabs_cek.py           X'ten tweet çekme: Oxylabs AI-Search + AI-Scraper
data/x_ham/                        X taramasının ham JSON arşivi
RSS.txt                            kaynak listesi, elle doldurulur
data/briefings/                    günlük brifingler (örnek: 2026-09-03.ornek.md)
data/analiz.md                     birikimli analiz günlüğü
prompts/PROMPTLAR.md               videoda kullandığım tüm promptlar
docs/vps-kurulum.md                Hostinger'da kurulum, sırasıyla
docs/telegram-kurulum.md           BotFather, kullanıcı ID, Hermes Channels
docs/x-oxylabs.md                  X'ten veri çekme sorunu ve çözümü
.env.example                       beklenen anahtar adları
```

Tarifler proje kökü olarak `/opt/data/sabah-brifingi` yazar (Hostinger Hermes
şablonunun kalıcı diski). Başka bir yere kurarsan üç tarifteki bu satırı değiştir.

## Kurulum (kısa)

1. **Lokalde**: bu repoyu klonla, `RSS.txt`'yi kendi kaynaklarınla doldur.
   Tarifleri değiştirmek istersen Claude Code ile: `prompts/PROMPTLAR.md`.
2. **VPS**: `docs/vps-kurulum.md`. Sıra: VPS aç → Hermes şablonu → model
   anahtarı → Telegram → projeyi zip olarak yükle → Oxylabs anahtarı → cron.
3. **Test**: Hermes Chat'te "sabah brifingi topla" yaz. Brifing gelirse cron
   da çalışır.

## Kendi nişine uyarla

Kaynakları sen seçiyorsun. `RSS.txt`'deki adresleri ve `toplayici.md`'deki
arama eksenlerini ("AI agents", "Claude Anthropic", "yapay zeka") kendi
alanınla değiştir; gerisi aynı.

## Kullanılanlar

Hermes Agent (Nous Research) · Hostinger VPS KVM 2, Hermes Agent şablonu ·
Claude Code + Claude Sonnet 5 · Telegram (BotFather) · Oxylabs AI Studio

Sorun olursa videonun yorumlarına yazın.
