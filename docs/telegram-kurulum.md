# Hermes Agent'ı Telegram'a bağlama (adım adım)

Videoda bu kısmı iPad'den yaptığım için ekranda tam görünmedi. Burada
baştan sona sırasıyla var. Süre: 5 dakika. Gereken: Telegram hesabı ve
Hostinger'daki Hermes paneli.

Hermes Telegram'a iki bilgiyle bağlanır:

1. **Bot token** — botun kimliği. @BotFather verir.
2. **Senin kullanıcı ID'n** — botla sadece senin konuşabilmen için.
   Kullanıcı adın değil, sayı (örnek: 123456789). @userinfobot verir.

## 1. Botu oluştur (Telegram'da)

1. Telegram'da **@BotFather**'ı aç (t.me/BotFather).
2. `/newbot` yaz.
3. Görünen ad sor: istediğin bir şey (örnek: Hermes Sabah).
4. Kullanıcı adı sor: benzersiz olmalı ve `bot` ile bitmeli
   (örnek: `sabah_hermes_bot`).
5. BotFather sana token verir. Şöyle görünür:

```
123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
```

Token'ı kopyala. Bu token'ı bilen herkes botu yönetebilir; ekranda
paylaşma, sızarsa BotFather'da `/revoke` ile iptal et.

## 2. Kullanıcı ID'ni öğren (Telegram'da)

1. **@userinfobot**'u aç (t.me/userinfobot) ve herhangi bir mesaj gönder.
2. Cevapta `Id: 123456789` gibi bir sayı var. Onu kopyala.

Hermes panelindeki "Allowed users" alanı sadece sayı kabul eder;
`@kullaniciadi` yazarsan "must be numeric" hatası alırsın (videoda ben aldım).

## 3. Hermes panelinde bağla

1. Hermes paneli → sol menü **Channels**.
2. Telegram satırında iki seçenek var: **Create with QR** ve **Manual setup**.
   QR yolu bende çalışmadı; manuel yol daha güvenilir.
3. **Manual setup** → açılan pencerede:
   - **Telegram bot token**: 1. adımdaki token
   - **Allowed Telegram user IDs**: 2. adımdaki sayı
     (birden fazla kişi olacaksa virgülle ayır)
4. **Save & Enable**.
5. Üstte "Changes are saved. Restart the gateway" uyarısı çıkar →
   **Restart now** (ya da sağ üstteki **Restart gateway**). Ayarlar ancak
   yeniden başlatınca devreye girer.
6. Telegram satırındaki **Test** düğmesine bas: "Telegram connected" görmelisin.

Bu bilgiler sunucuda `/opt/data/.env` dosyasına
`TELEGRAM_BOT_TOKEN` ve `TELEGRAM_ALLOWED_USERS` olarak yazılır; elle
düzenlemene gerek yok.

## 4. İlk mesaj

Telegram'da botunu bul (BotFather'ın verdiği linkten ya da kullanıcı
adını aratarak), **Start**'a bas ve "merhaba" yaz. Hermes cevap verir.
Panelde **Sessions** sayfasında Telegram oturumunu görürsün.

## Sabah bildirimi Telegram'a nasıl düşüyor?

Cron sayfasında iş oluştururken teslim kanalı olarak Telegram seçilir
(docs/vps-kurulum.md, adım 7). Cron çalışınca sonuç doğrudan bota mesaj
olarak gelir; sen bir şey yazmana gerek yok.

## Sorun çıkarsa

- **Bot cevap vermiyor**: gateway'i yeniden başlattın mı? Channels → Restart.
- **"Unauthorized" / bot seni görmezden geliyor**: Allowed users'a yazdığın ID
  yanlış. @userinfobot'tan tekrar al.
- **"Gateway" hataları**: Channels → Restart gateway; düzelmezse Chat'te
  Hermes'e hatayı yapıştırıp sor, kendi loglarını okuyabiliyor (videoda ben öyle çözdüm).
- **Bir gruba eklemek istiyorsan**: BotFather → `/mybots` → bot → Bot Settings →
  Group Privacy → Turn off; sonra botu gruptan çıkarıp yeniden ekle.
