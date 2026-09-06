#!/usr/bin/env python3
"""X'ten (Twitter) Oxylabs AI Studio ile tweet ceker. Tarayici ve X hesabi kullanmaz.

Akis:  AI-Search ile eksen basina tweet linki bul  ->  her linki AI-Scraper ile ac
       -> metin/yazar/tarih cikar  ->  son N saat penceresine gore ele.

Kullanim:
    python3 scripts/x_oxylabs_cek.py                 # son 168 saat (7 gun)
    python3 scripts/x_oxylabs_cek.py --saat 720      # son 30 gun (tarifte kullanilan)
    python3 scripts/x_oxylabs_cek.py --sinir 15      # eksen basina arama sonucu

Cikti (stdout, JSON):
    {"tweets": [{"metin","yazar","tarih","link"}, ...], "errors": [...], "atlandi": bool}

Kimlik: OXYLABS ortam degiskeni (Oxylabs AI Studio API key). Degisken yoksa ya da
`oxylabs_ai_studio` paketi kurulu degilse hata firlatmaz, {"atlandi": true} doner.
Anahtar hicbir yere yazilmaz.

Not: AI-Search'un zaman ifadesi gercek bir filtre degil; eski/viral tweetler de gelir.
Tarih filtresi bu yuzden burada, scraper'dan gelen tarih alaniyla yapilir.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone

EKSENLER = [
    '"AI agents"',
    "Claude Anthropic",
    "OpenAI GPT",
    "Gemini Google DeepMind",
    "yapay zeka",
]
TWEET_RE = re.compile(r"https?://(?:www\.)?(?:x|twitter)\.com/[^/\s]+/status/(\d+)")
SEMA = {
    "type": "object",
    "properties": {
        "metin": {"type": "string", "description": "tweet metni, oldugu gibi"},
        "yazar": {"type": "string", "description": "@ ile baslayan kullanici adi"},
        "tarih": {"type": "string", "description": "yayin tarihi, ISO 8601 (YYYY-MM-DDTHH:MM:SSZ)"},
    },
    "required": ["metin", "tarih"],
}


def _bas(sonuc: dict) -> None:
    print(json.dumps(sonuc, ensure_ascii=False, indent=1))


def _tarih_coz(metin: str | None) -> datetime | None:
    if not metin:
        return None
    m = metin.strip().replace("Z", "+00:00")
    for aday in (m, m[:19], m[:10]):
        try:
            d = datetime.fromisoformat(aday)
            return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    try:
        from email.utils import parsedate_to_datetime

        d = parsedate_to_datetime(metin)
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return None


def _url_al(oge) -> str | None:
    if isinstance(oge, str):
        return oge
    if isinstance(oge, dict):
        return oge.get("url") or oge.get("link")
    return getattr(oge, "url", None) or getattr(oge, "link", None)


def _veri(sonuc):
    veri = getattr(sonuc, "data", sonuc)
    if isinstance(veri, str):
        try:
            veri = json.loads(veri)
        except ValueError:
            return {}
    return veri or {}


def linkleri_bul(search, sinir: int, hatalar: list[str]) -> list[str]:
    bulunan: list[str] = []
    gorulen: set[str] = set()
    for eksen in EKSENLER:
        try:
            sonuc = search.search(query=f"site:x.com {eksen}", limit=sinir, return_content=False)
        except Exception as e:  # noqa: BLE001 - tek eksen dusunce digerleri devam eder
            hatalar.append(f"arama hatasi [{eksen}]: {type(e).__name__}")
            continue
        veri = _veri(sonuc)
        ogeler = veri if isinstance(veri, list) else veri.get("results") or veri.get("data") or []
        for oge in ogeler:
            url = _url_al(oge)
            if not url:
                continue
            m = TWEET_RE.search(url)
            if not m or m.group(1) in gorulen:
                continue
            gorulen.add(m.group(1))
            bulunan.append(m.group(0))
    return bulunan


def tweeti_cek(scraper, link: str) -> dict | None:
    sonuc = scraper.scrape(url=link, output_format="json", schema=SEMA, render_javascript=True)
    veri = _veri(sonuc)
    if isinstance(veri, list):
        veri = veri[0] if veri else {}
    if not isinstance(veri, dict) or not veri.get("metin"):
        return None
    return {
        "metin": str(veri.get("metin", "")).strip(),
        "yazar": str(veri.get("yazar", "")).strip(),
        "tarih": str(veri.get("tarih", "")).strip(),
        "link": link,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--saat", type=int, default=168, help="kac saat geriye bakilsin (varsayilan 168)")
    p.add_argument("--sinir", type=int, default=15, help="eksen basina arama sonucu (varsayilan 15)")
    args = p.parse_args()

    anahtar = os.environ.get("OXYLABS")
    if not anahtar:
        _bas({"tweets": [], "errors": ["OXYLABS ortam degiskeni yok"], "atlandi": True})
        return 0
    try:
        from oxylabs_ai_studio.apps.ai_scraper import AiScraper
        from oxylabs_ai_studio.apps.ai_search import AiSearch
    except ImportError:
        _bas({"tweets": [], "errors": ["oxylabs_ai_studio paketi kurulu degil (pip install oxylabs-ai-studio)"], "atlandi": True})
        return 0

    hatalar: list[str] = []
    try:
        search = AiSearch(api_key=anahtar)
        scraper = AiScraper(api_key=anahtar)
    except Exception as e:  # noqa: BLE001
        _bas({"tweets": [], "errors": [f"istemci kurulamadi: {type(e).__name__}"], "atlandi": True})
        return 0

    linkler = linkleri_bul(search, args.sinir, hatalar)
    sinir_zaman = datetime.now(timezone.utc) - timedelta(hours=args.saat)
    simdi = datetime.now(timezone.utc) + timedelta(hours=1)
    tweets: list[dict] = []
    for link in linkler:
        try:
            t = tweeti_cek(scraper, link)
        except Exception as e:  # noqa: BLE001
            hatalar.append(f"cekme hatasi [{link}]: {type(e).__name__}")
            continue
        if not t:
            hatalar.append(f"bos icerik [{link}]")
            continue
        d = _tarih_coz(t["tarih"])
        if d is None:
            hatalar.append(f"tarih cozulemedi [{link}]")
            continue
        if d < sinir_zaman or d > simdi:
            continue
        t["tarih"] = d.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        tweets.append(t)

    tweets.sort(key=lambda x: x["tarih"], reverse=True)
    _bas({"tweets": tweets, "errors": hatalar, "atlandi": False})
    return 0


if __name__ == "__main__":
    sys.exit(main())
