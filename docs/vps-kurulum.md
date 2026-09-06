# Hostinger VPS'te Hermes Agent kurulumu (videodaki sıra)

## 1. VPS'i aç

1. https://hostinger.com/SELMA → Hermes Agent VPS sayfası.
2. Plan: **KVM 2** (2 vCPU, 8 GB RAM). Model sunucuda çalışmıyor, API ile
   çağrılıyor; bu yüzden büyük işlemci gerekmiyor ama 7/24 çalışacağı için
   darlık da istemiyoruz.
3. Süre: 12 ya da 24 ay. Aylık fiyat uzun dönemde düşüyor; ben 24 ay seçtim.
4. Ödeme sayfasında kupon alanına **SELMA** → ek %10 indirim.
   30 gün para iade garantisi var.

## 2. Hermes şablonunu kur

1. hPanel → VPS → sunucun → **Applications** → Hermes Agent → kur.
2. Kurulum sonunda panel bir kullanıcı adı ve tek seferlik şifre verir.
   Bunları kaydet; Hermes paneline bununla gireceksin.
3. Nexos ya da Oxylabs anahtarı istiyorsa boş bırakabilirsin; sonradan
   panelden eklenir.
4. **Open app** ile Hermes paneline gir.

Sunucu yeniden başlasa da ajanın hafızası ve yetenekleri `/opt/data`
altındaki kalıcı diskte durur.

## 3. Modeli bağla

1. Hermes paneli → **Keys**. 16 sağlayıcı var; ben Anthropic kullanıyorum.
2. console.anthropic.com → Settings → API keys → **Create key**.
   Bu ajan için ayrı bir anahtar aç (örnek: `hermes-vps`) ve harcama
   limiti koy.
3. Anahtarı Keys sayfasına yapıştır.
4. **Models** → refresh → main model: `claude-sonnet-5` (maliyet için).

ChatGPT/Codex, Grok, MiniMax hesabın varsa Keys sayfasından doğrudan
hesap bağlamak da mümkün.

## 4. Telegram'ı bağla

docs/telegram-kurulum.md. Bitince Channels → Restart gateway.

## 5. Projeyi yükle

1. Lokaldeki `sabah-brifingi/` klasörünü zip'le.
2. Hermes paneli → **Files** → home klasörüne yükle.
3. Chat → New chat → prompts/PROMPTLAR.md'deki 4. prompt
   ("Home klasöründe … aç, yerleştir, kur").
4. Ajan zip'i açar, tarifleri okur. **Skills** sayfasında yeteneklerin
   geldiğini gör.

## 6. X için Oxylabs

docs/x-oxylabs.md.

## 7. Sabah bildirimi cron'u

1. **Cron** → Create.
2. Name: `Sabah Bildirimi`. Schedule: daily, 05:30. Deliver to: Telegram.
3. Prompt: prompts/PROMPTLAR.md, 7. prompt.
4. Kaydet. İlk çalışmayı beklemeden test etmek için Chat'te aynı promptu
   yazabilirsin.

## 8. Kontrol listesi

- Keys: Anthropic ✓, OXYLABS ✓
- Channels: Telegram Connected ✓ (Test düğmesi)
- Skills: toplayici, analizci, uretici görünüyor ✓
- Cron: Sabah Bildirimi, 05:30, Telegram ✓
- Restart gateway yapıldı ✓
