---
name: toplayici-lokal
description: Lokal sürüm — X'i tarayıcı oturumuyla tarar (VPS'te kullanılmaz).
---

# Sabah Brifingi Topla

Sabah brifingini toplayan, yazan ve kaydeden tarif. "Sabah brifingi topla",
"bugünün brifingi", "günaydın brifing" dendiğinde bu tarif uygulanır.

Proje kökü: ~/sabah-brifingi (lokal sürüm)
Tüm göreli yollar bu köke göredir.

## Ne zaman çalışır

- Kullanıcı açıkça istediğinde ("sabah brifingi topla")
- Zamanlanmış sabah işi tetiklediğinde

## Çıktı sözleşmesi (kesin)

- Dosya: data/briefings/YYYY-MM-DD.md (bugünün yerel tarihi)
- Türkçe, en fazla 10 madde TOPLAM, iki bölüme ayrılır:
  - "## Gündem" — RSS ve web_search kaynaklı maddeler
  - "## X'te konuşulanlar" — X taramasından (adım 1) gelen maddeler
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

### 1. X / AI gündemini topla

X'i GERÇEKTEN tara — `mcp__browser_exec` ile x.com/search'e git (mevcut
tarayıcı oturumu zaten giriş yapılmış olmalı; değilse kullanıcıya login
duvarını haber ver, tahmin etme). `web_search` X'i indekslemez / güncel
tweet içeriği getirmez, o yüzden yalnızca destek aracıdır, birincil kaynak
değildir.

X arama adımı (üç eksen, "top" filtresiyle — "live" çok gürültülü):

```python
goto_url("https://x.com/search?q=<url-encoded sorgu>&src=typed_query&f=top")
wait_for_load(); time.sleep(3)
js('''(() => {
  const articles = Array.from(document.querySelectorAll('article'));
  return articles.slice(0, 15).map(a => {
    const timeEl = a.querySelector('time');
    const time = timeEl ? timeEl.getAttribute('datetime') : null;
    const textEl = a.querySelector('div[data-testid="tweetText"]');
    const text = textEl ? textEl.innerText : null;
    const linkEl = a.querySelector('a[href*="/status/"]');
    const link = linkEl ? linkEl.href : null;
    const userEl = a.querySelector('div[data-testid="User-Name"]');
    const user = userEl ? userEl.innerText.split("\\n")[0] : null;
    return {time, text, link, user};
  }).filter(x => x.text);
})()''')
```

En az şu üç eksende ara:
- `"AI agents"` — X'te çok konuşulanlar
- `Claude Anthropic` — yeni sürüm, özellik, tartışma
- `yapay zeka` — Türkçe gündem

Bir sorgu boş dönerse bir kez daha dene (X akışı bazen ilk yüklemede boş
gelir); yine boşsa o eksen için X'i atla, RSS/web_search ile devam et.

Destek olarak `web_search` de kullan (aynı üç eksen, sorgu kalıpları:
`AI agents twitter today trending`, `Claude Anthropic news today`,
`yapay zeka gündem site:x.com`), ama X'ten gelen gerçek tweet'lere öncelik
ver.

Kural: sonucun tarihini doğrula (tweet `datetime` alanı / haber tarihi).
Bugüne veya düne ait değilse alma.
Tamamlanma ölçütü: üç eksenin her biri için hem X taraması hem web_search
denendi ve tarihi doğrulanmış aday başlıklar listesi elde edildi.

Ham X verisini arşivle: her sorgudan dönen ham `{time, text, link, user}`
listesini `data/x_ham/YYYY-MM-DD_<eksen>.json` olarak `write_file` ile
kaydet (ör. `data/x_ham/2026-09-03_ai_agents.json`). Bu, brifinge hangi
tweet'lerin elendiğini sonradan denetleyebilmek içindir; kullanıcıya
gönderilmez, sadece diske yazılır.
Tamamlanma ölçütü: taranan her eksen için bir ham JSON dosyası diskte var.

### 2. RSS başlıklarını çek

RSS.txt içindeki adreslerden bugünün başlıklarını al:

```
terminal(command="python3 scripts/rss_cek.py", workdir="~/sabah-brifingi")
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

1. <Tek cümlelik başlık.> <https://x.com/.../status/...>
2. <Tek cümlelik başlık.> <https://x.com/.../status/...>
...
```

Tamamlanma ölçütü: her madde tek cümle, her maddede tam bir link var,
madde sayısı ≤ 10, iki bölüm başlığı da mevcut, X bölümündeki linkler
gerçekten X kaynaklı.

### 4. Kaydet

`write_file` ile data/briefings/YYYY-MM-DD.md dosyasına yaz.
Tamamlanma ölçütü: dosya diskte var ve içeriği brifingin tamamı.

### 5. Analizciyi çalıştır

Son adım: skills/analizci.md tarifini uygula.
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
- X araması login duvarına takılırsa tahmin etme / uydurma, kullanıcıya
  bildir; oturum yoksa X adımını atla ve bunu brifing sonunda belirt.
- RSS/web maddesini X bölümüne, X maddesini Gündem bölümüne karıştırma —
  kaynağı doğrulamadan bölüm seçme.

## Doğrulama

- data/briefings/<bugün>.md okunabiliyor ve ≤ 10 madde içeriyor
- Brifingde "## Gündem" ve "## X'te konuşulanlar" başlıkları ikisi de var
- X bölümündeki linkler gerçekten X/tweet kaynaklı
- data/analiz.md'de bugünün tarihli bölümü var
- Kullanıcıya giden mesaj sadece brifing metni
