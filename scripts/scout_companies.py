#!/usr/bin/env python3
"""Agentti B - Luovien alojen yritysostokohteet.

Fetches public for-sale creative-sector listings, excluding beauty services
even when combined with a creative business. The output schema is consumed by
assets/js/main.js on the Nousuun.fi front page.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlencode, unquote, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "companies.json"
META = ROOT / "data" / "meta.json"

SOURCE_URL = "https://www.yrityskaupat.net/wp-admin/admin-ajax.php"
LISTING_URL = "https://www.yrityskaupat.net/fi/myytavat-yritykset/"

FILTERS = {
    "industry": "",
    "location": "",
    "search": "",
    "not_bound": "",
    "item_funding": "",
    "orderby": "date",
    "order": "DESC",
    "perpage": "25",
    "page": "1",
}

CREATIVE_SECTORS = {
    "Valokuvaus": r"\bvalokuva\w*|\bphotograph\w*",
    "Viestintä": r"\bviestint\w*|\bviestinn\w*|\bcommunications?\b",
    "Mainostoimisto": r"\bmainostoimist\w*|\bmainosalan yrity\w*|\badvertising agency\b",
    "Musiikki": r"\bmusiik\w*|\bmusic\w*|\bäänitysstudio\w*",
    "Audiovisuaalinen tuotanto": r"\baudiovisuaal\w*|\bav-tuot\w*|\bvideo(?:tuotanto|tuotann)\w*|\belokuv\w*",
    "Muotoilu": r"\bmuotoil\w*|\bdesign(?:-?studio|toimisto| agency)\w*",
    "Pelit": r"\bpelistudio\w*|\bpelikehit\w*|\bpelinkehit\w*|\bgame (?:studio|development)\b",
    "Taide": r"\btaide(?:galleria|tuotanto|ala)\w*|\btaiteen\b",
    "Kustantaminen": r"\bkustanta\w*|\bkustannustoimin\w*|\bpublishing\b",
    "Media": r"\bmediatuotan\w*|\bmediayhti\w*|\bmediatoimist\w*|\bmedia-al\w*",
}
# Hard exclusion always takes precedence, including a mixed creative/beauty business.
EXCLUDED_SECTORS = re.compile(
    r"kaune|kosmet|cosmet|beauty|esteti|esteett|aesthetic|esthetic|"
    r"plastiikk|plastic surgery|botox|botuliini|täyteaine|filler|"
    r"meikk|make-?up|kynsi|nail salon|ripsi|lash salon|parturi|kampaamo",
    re.IGNORECASE,
)


def creative_sector(item, detail_text=""):
    """Fail closed unless a named creative business is clear in source metadata.

    Details are checked for excluded activities too; general IT, trade, retail,
    maintenance or marketing keywords alone never establish a creative sector.
    """
    all_text = unquote(" ".join(str(value) for value in item.values()) + " " + detail_text)
    if EXCLUDED_SECTORS.search(all_text):
        return None
    identity = item.get("name", "").casefold()
    for sector, pattern in CREATIVE_SECTORS.items():
        if re.search(pattern, identity):
            return sector
    # Broad mixed categories can hide a generic manufacturer, retailer or IT site.
    # A creative category alone qualifies only when it describes the whole industry.
    industry = item.get("industry", "").casefold().strip()
    exact_industries = {
        "mainostoimisto, markkinointi": "Mainostoimisto",
        "kustannustoiminta": "Kustantaminen",
        "valokuvaus": "Valokuvaus",
        "musiikki": "Musiikki",
        "muotoilu": "Muotoilu",
    }
    if industry in exact_industries:
        return exact_industries[industry]
    return None

SOLO_FRIENDLY_KEYWORDS = [
    "kevyt",
    "pieni",
    "palvelu",
    "verkkokauppa",
    "konsult",
    "koulutus",
    "maahantuonti",
]


class ListingTableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = []
        self.current_row = None
        self.current_cell = None
        self.current_link = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "tr":
            self.current_row = []
        elif tag == "td" and self.current_row is not None:
            self.current_cell = {"text": "", "href": ""}
        elif tag == "a" and self.current_cell is not None:
            self.current_link = attrs.get("href", "")

    def handle_data(self, data):
        if self.current_cell is not None:
            self.current_cell["text"] += data

    def handle_endtag(self, tag):
        if tag == "a" and self.current_cell is not None and self.current_link:
            self.current_cell["href"] = self.current_link
            self.current_link = None
        elif tag == "td" and self.current_row is not None and self.current_cell is not None:
            self.current_row.append(self.current_cell)
            self.current_cell = None
        elif tag == "tr" and self.current_row is not None:
            if len(self.current_row) >= 4:
                self.rows.append(self.current_row)
            self.current_row = None


def clean_text(value):
    return re.sub(r"\s+", " ", html.unescape(value or "")).strip()


def normalize_title(value):
    """Remove listing-site shouting while preserving ordinary proper names."""
    title = re.sub(r"!+", "", clean_text(value)).strip()
    letters = "".join(char for char in title if char.isalpha())
    if letters and letters == letters.upper():
        title = title.capitalize()
    return title


def fetch_source_rows(page=1):
    filters = dict(FILTERS, page=str(page), perpage="50")
    body = urlencode({"action": "ms_selling", "filters": urlencode(filters)})
    request = Request(
        SOURCE_URL,
        data=body.encode("utf-8"),
        headers={
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "User-Agent": "Nousuun.fi Agentti B/0.1",
            "Referer": LISTING_URL,
            "X-Requested-With": "XMLHttpRequest",
        },
    )
    with urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not payload.get("success"):
        return []
    parser = ListingTableParser()
    parser.feed(payload.get("data", {}).get("results", ""))
    return parser.rows


def fetch_listing_details(url):
    # Only follow the source's actual detail pages, never a generic list fallback.
    parsed = urlparse(url)
    if parsed.hostname != "www.yrityskaupat.net" or not parsed.path.startswith("/fi/myytava-yritys/"):
        raise ValueError("Listing has no valid source detail URL")
    request = Request(url, headers={"User-Agent": "Nousuun.fi Agentti B/0.2"})
    with urlopen(request, timeout=30) as response:
        markup = response.read().decode("utf-8")
    markup = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", markup, flags=re.S | re.I)
    text = clean_text(re.sub(r"<[^>]+>", " ", markup))
    if "Myynnin aihe" not in text or "Toimiala" not in text or "Pyydä lisätietoja kohteesta" not in text:
        raise ValueError("Source detail page does not confirm an active listing")
    # Stop before inquiry forms and related listings; those describe other companies.
    return text.split("Myynnin aihe", 1)[1].split("Pyydä lisätietoja kohteesta", 1)[0]


def normalize_listing(row):
    title = normalize_title(row[0]["text"])
    industry = clean_text(row[1]["text"])
    location = clean_text(row[2]["text"])
    price = clean_text(row[3]["text"]) or "Ei julkinen"
    return {
        "name": title,
        "industry": industry,
        "price": price,
        "location": location,
        "url": row[0].get("href") or LISTING_URL,
        "source": "Suomen Yrityskaupat",
    }


def score_listing(item):
    text = f"{item['name']} {item['industry']}".lower()
    score = 5.0
    score += 1.0 if creative_sector(item) else 0.0
    score += min(1.5, sum(0.30 for keyword in SOLO_FRIENDLY_KEYWORDS if keyword in text))
    if any(word in text for word in ["kannattava", "vakaa", "menestyv"]):
        score += 1.0
    if "ei julkinen" not in item["price"].lower():
        score += 0.3
    if "49%" in text or "osakepääomasta" in text.lower():
        score -= 0.8
    price_digits = re.sub(r"\D", "", item["price"])
    if price_digits:
        price_number = int(price_digits[:10])
        if price_number >= 1000000:
            score -= 0.7
        elif price_number <= 250000:
            score += 0.3
    return round(min(score, 9.4), 1)


def build_insight(item, score):
    return (
        f"Luova ala: {item['creative_sector']}. "
        f"Ilmoittajan toimialaluokitus: {item['industry']}. "
        f"Lähde tarkistettu {datetime.now(timezone.utc).date().isoformat()}; "
        "tarkista hinta, saatavuus ja kaupan sisältö ilmoittajalta."
    )


def update_meta(timestamp):
    try:
        meta = json.loads(META.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        meta = {"sections": {}}
    meta["updated_at"] = timestamp
    meta.setdefault("sections", {})["companies"] = timestamp
    meta.setdefault("weeks", {})["companies"] = datetime.now(timezone.utc).strftime("%G-W%V")
    META.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def main(update_metadata=True):
    OUT.parent.mkdir(exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat()
    listings = []
    rows = []
    seen_urls = set()
    for page in range(1, 9):
        page_rows = fetch_source_rows(page)
        fresh = [row for row in page_rows if row[0].get("href") not in seen_urls]
        rows.extend(fresh)
        seen_urls.update(row[0].get("href") for row in fresh)
        if len(page_rows) < 50 or not fresh:
            break
    print(f"Checked {len(rows)} public source rows")
    for row in rows:
        item = normalize_listing(row)
        if not item["name"] or not creative_sector(item):
            continue
        try:
            details = fetch_listing_details(item["url"])
        except (OSError, ValueError) as error:
            print(f"Skipped unverified listing {item['url']}: {error}")
            continue
        sector = creative_sector(item, details)
        if not sector:
            continue
        item["creative_sector"] = sector
        item["creative_sector_verified"] = True
        score = score_listing(item)
        item["score"] = score
        item["insight"] = build_insight(item, score)
        listings.append(item)

    listings.sort(key=lambda item: item["score"], reverse=True)
    seen_insights = set()
    for item in listings:
        normalized = item["insight"].casefold().strip()
        if normalized in seen_insights:
            item["insight"] = f"{item['insight']} Toimiala: {item['industry']}."
            normalized = item["insight"].casefold().strip()
        seen_insights.add(normalized)
    payload = {
        "agent": "Agentti B - Omistajanvaihdokset",
        "updated_at": timestamp,
        "week": datetime.now(timezone.utc).strftime("%G-W%V"),
        "companies": listings[:10],
        "note": "Vain lähteestä tarkistetut luovien alojen yritysostokohteet. Kauneus-, kosmetologi- ja kauneuskirurgiapalvelut rajataan pois myös yhdistelmäyrityksistä."
        if listings else "Tällä tarkistuskerralla ei löytynyt rajaukseen sopivia, lähteestä vahvistettuja luovien alojen yritysostokohteita.",
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    if update_metadata:
        update_meta(timestamp)
    print(f"Wrote {OUT} with {len(payload['companies'])} companies")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-meta", action="store_true", help="Write companies only; leave shared metadata to publisher")
    main(update_metadata=not parser.parse_args().no_meta)
