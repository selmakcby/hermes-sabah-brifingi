#!/usr/bin/env python3
"""RSS.txt icindeki RSS/Atom adreslerinden bugunun ogelerini ceker.

Kullanim:
    python3 scripts/rss_cek.py            # bugun
    python3 scripts/rss_cek.py --gun 2    # son 2 gun

Cikti: stdout'a JSON {"items": [...], "errors": [...]}
Sadece Python standart kutuphanesi kullanir. Ag disinda hicbir sey yazmaz.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
KAYNAKLAR = KOK / "RSS.txt"
UA = "sabah-brifingi/1.0 (+local)"
ZAMAN_ASIMI = 20


def feed_adresleri() -> list[str]:
    if not KAYNAKLAR.exists():
        return []
    adresler: list[str] = []
    for ham in KAYNAKLAR.read_text(encoding="utf-8").splitlines():
        satir = ham.strip()
        if not satir or satir.startswith("#"):
            continue
        adres = satir.split("#", 1)[0].strip()
        if adres.startswith(("http://", "https://")):
            adresler.append(adres)
    return adresler


def tarih_coz(metin: str | None) -> datetime | None:
    if not metin:
        return None
    metin = metin.strip()
    try:
        d = parsedate_to_datetime(metin)
        if d is not None:
            return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        pass
    kalip = metin.replace("Z", "+00:00")
    for deneme in (kalip, kalip[:19]):
        try:
            d = datetime.fromisoformat(deneme)
            return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def etiket(el: ET.Element) -> str:
    return el.tag.rsplit("}", 1)[-1]


def alt_metin(oge: ET.Element, adlar: tuple[str, ...]) -> str | None:
    for cocuk in oge:
        if etiket(cocuk) in adlar and (cocuk.text or "").strip():
            return cocuk.text.strip()
    return None


def link_bul(oge: ET.Element) -> str | None:
    for cocuk in oge:
        if etiket(cocuk) != "link":
            continue
        if (cocuk.text or "").strip():
            return cocuk.text.strip()
        href = cocuk.attrib.get("href")
        rel = cocuk.attrib.get("rel", "alternate")
        if href and rel == "alternate":
            return href.strip()
    return None


def feed_isle(adres: str, sinir: datetime) -> tuple[list[dict], str | None]:
    istek = urllib.request.Request(adres, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(istek, timeout=ZAMAN_ASIMI) as yanit:
            ham = yanit.read()
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
        return [], f"{adres} -> baglanti hatasi: {e}"

    try:
        kok = ET.fromstring(ham)
    except ET.ParseError as e:
        return [], f"{adres} -> ayristirma hatasi: {e}"

    kaynak_adi = None
    for yol in ("./channel/title", "./{*}title"):
        bulunan = kok.find(yol)
        if bulunan is not None and (bulunan.text or "").strip():
            kaynak_adi = bulunan.text.strip()
            break

    ogeler = [el for el in kok.iter() if etiket(el) in ("item", "entry")]
    sonuc = []
    for oge in ogeler:
        tarih = tarih_coz(
            alt_metin(oge, ("pubDate", "published", "updated", "date"))
        )
        if tarih is None or tarih < sinir:
            continue
        baslik = alt_metin(oge, ("title",))
        if not baslik:
            continue
        sonuc.append(
            {
                "kaynak": kaynak_adi or adres,
                "baslik": baslik,
                "link": link_bul(oge),
                "tarih": tarih.isoformat(),
            }
        )
    return sonuc, None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gun", type=int, default=1, help="kac gun geriye bakilsin")
    args = ap.parse_args()

    simdi = datetime.now(timezone.utc)
    sinir = simdi - timedelta(days=args.gun)

    adresler = feed_adresleri()
    items: list[dict] = []
    errors: list[str] = []

    if not adresler:
        errors.append("RSS.txt bos ya da hic gecerli adres yok")

    for adres in adresler:
        bulunan, hata = feed_isle(adres, sinir)
        items.extend(bulunan)
        if hata:
            errors.append(hata)

    items.sort(key=lambda x: x["tarih"], reverse=True)
    json.dump(
        {"feed_sayisi": len(adresler), "items": items, "errors": errors},
        sys.stdout,
        ensure_ascii=False,
        indent=2,
    )
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
