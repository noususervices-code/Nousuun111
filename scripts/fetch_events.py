#!/usr/bin/env python3
"""Fallback fetch for Agentti A.

The curated weekly report is the source of truth for Nousuun.fi events. This
script exists only as a manual safety net if no curated report is available.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "events.json"
META = ROOT / "data" / "meta.json"

KEYWORDS = [
    "yrittaj",
    "yrittäj",
    "yrity",
    "startup",
    "tekoaly",
    "tekoäly",
    "liiketoiminta",
    "kasvu",
    "verkosto",
    "rahoitus",
    "omistajanvaihdos",
    "pitch",
]

EXCLUDE_KEYWORDS = ["tyonhaku", "työnhaku", "tyonantajatreffit", "työnantajatreffit"]


def pick_lang(value):
    if isinstance(value, dict):
        return value.get("fi") or value.get("en") or value.get("sv") or ""
    return value or ""


def event_matches(event):
    text = " ".join(
        [
            pick_lang(event.get("name")),
            pick_lang(event.get("short_description")),
            pick_lang(event.get("description")),
        ]
    ).lower()
    if any(keyword in text for keyword in EXCLUDE_KEYWORDS):
        return False
    return any(keyword in text for keyword in KEYWORDS)


def is_future_event(event):
    start = event.get("start_time") or ""
    if len(start) < 10:
        return False
    return start[:10] >= datetime.now(timezone.utc).date().isoformat()


def normalize_event(event):
    start = event.get("start_time") or ""
    date = start[:10] if start else ""
    time = start[11:16] if len(start) >= 16 else ""
    location = event.get("location") or {}
    images = event.get("images") or []
    return {
        "name": pick_lang(event.get("name")),
        "date": date,
        "time": time,
        "location": pick_lang(location.get("name")),
        "description": pick_lang(event.get("short_description"))[:280],
        "url": pick_lang(event.get("info_url")) or event.get("@id", "#"),
        "image": images[0].get("url") if images else "",
        "source": "Linked Events",
        "tags": [keyword for keyword in KEYWORDS if keyword in json.dumps(event).lower()][:3],
    }


def fetch_linked_events():
    now = datetime.now(timezone.utc)
    search_terms = ["yrittäjyys", "yritys", "startup", "tekoäly", "rahoitus", "pitch"]
    seen = set()
    events = []
    for term in search_terms:
        params = {
            "q": term,
            "type": "event",
            "start": now.date().isoformat(),
            "end": (now + timedelta(days=21)).date().isoformat(),
            "page_size": 20,
        }
        url = "https://api.hel.fi/linkedevents/v1/search/?" + urlencode(params)
        request = Request(url, headers={"User-Agent": "Nousuun.fi events-agent/0.1"})
        with urlopen(request, timeout=30) as response:
            for event in json.loads(response.read().decode("utf-8")).get("data", []):
                event_id = event.get("@id") or event.get("id") or json.dumps(event, sort_keys=True)
                if event_id not in seen:
                    seen.add(event_id)
                    events.append(event)
    return events


def update_meta(timestamp):
    try:
        meta = json.loads(META.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        meta = {"sections": {}}
    meta["updated_at"] = timestamp
    meta.setdefault("sections", {})["events"] = timestamp
    META.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    OUT.parent.mkdir(exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat()
    events = [
        normalize_event(event)
        for event in fetch_linked_events()
        if is_future_event(event) and event_matches(event)
    ]
    events.sort(key=lambda event: (event.get("date", ""), event.get("time", "")))
    payload = {
        "agent": "Agentti A - Tapahtumat",
        "quality": "fallback_linked_events",
        "updated_at": timestamp,
        "events": events[:12],
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    update_meta(timestamp)
    print(f"Wrote {OUT} with {len(payload['events'])} events")


if __name__ == "__main__":
    main()
