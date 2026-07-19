#!/usr/bin/env python3
"""Agentti B - Viikon yritykset.

Fetches public for-sale company listings and ranks them for a modern solo or
small-business entrepreneur. The output schema is consumed directly by
assets/js/main.js on the Nousuun.fi front page.
"""

from __future__ import annotations

import html
import json
import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlencode
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

DIGITAL_KEYWORDS = [
    "verkkokauppa",
    "ohjelm",
    "ict",
    "tekn",
    "maahantuonti",
    "b2b",
    "markkinointi",
    "koulutus",
    "konsult",
    "palvelu",
    "huolto",
]

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


def fetch_source_rows():
    body = urlencode({"action": "ms_selling", "filters": urlencode(FILTERS)})
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
    score += min(2.0, sum(0.35 for keyword in DIGITAL_KEYWORDS if keyword in text))
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
    text = f"{item['name']} {item['industry']}".lower()
    if any(keyword in text for keyword in ["verkkokauppa", "ict", "ohjelm"]):
        angle = "Valmis digitaalinen myyntikanava sopii ostajalle, joka haluaa kehittää verkkokauppaa, asiakaspitoa ja toistuvaa myyntiä."
    elif any(keyword in text for keyword in ["maahantuonti", "tekn", "kauppa"]):
        angle = "Vakiintuneet toimittaja- ja asiakassuhteet voivat tarjota valmiin pohjan B2B-myynnin ja verkkokaupan kehittämiselle."
    elif any(keyword in text for keyword in ["palvelu", "huolto", "konsult", "koulutus"]):
        angle = "Valmis asiakaskunta ja palveluprosessi sopivat ostajalle, joka haluaa kasvattaa kapasiteettia ilman nollasta aloittamista."
    else:
        angle = "Kohteen arvo riippuu valmiista asiakaskunnasta, toistuvasta kassavirrasta ja siitä, kuinka hyvin toiminta siirtyy uudelle omistajalle."
    detail = f"Sijainti: {item['location']}. Hintatieto: {item['price']}."
    return f"{angle} {detail}"


def update_meta(timestamp):
    try:
        meta = json.loads(META.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        meta = {"sections": {}}
    meta["updated_at"] = timestamp
    meta.setdefault("sections", {})["companies"] = timestamp
    META.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    OUT.parent.mkdir(exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat()
    listings = []
    for row in fetch_source_rows():
        item = normalize_listing(row)
        if not item["name"]:
            continue
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
        "agent": "Agentti B - Viikon yritykset",
        "updated_at": timestamp,
        "week": datetime.now(timezone.utc).strftime("%G-W%V"),
        "companies": listings[:10],
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    update_meta(timestamp)
    print(f"Wrote {OUT} with {len(payload['companies'])} companies")


if __name__ == "__main__":
    main()
