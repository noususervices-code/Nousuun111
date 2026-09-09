#!/usr/bin/env python3
"""Sync a curated weekly event report into the website JSON contract."""

from __future__ import annotations

import argparse
import json
import re
from urllib.parse import urlparse
from datetime import date
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "events.json"
META = ROOT / "data" / "meta.json"
DEFAULT_REPORT_DIR = ROOT.parent / "Agent_Outputs" / "Agentti_A_Tapahtumat" / "weekly_reports"
LEGACY_REPORT_DIR = ROOT.parent / "04_Community" / "Events" / "weekly_event_reports"


def find_latest_report():
    reports = sorted(
        [
            *DEFAULT_REPORT_DIR.glob("*_events.json"),
            *LEGACY_REPORT_DIR.glob("*_events.json"),
        ],
        key=lambda path: path.name,
    )
    if not reports:
        raise FileNotFoundError(f"No weekly event reports found in {DEFAULT_REPORT_DIR} or {LEGACY_REPORT_DIR}")
    return reports[-1]


def validate_report(data):
    if not isinstance(data, dict) or not re.fullmatch(r"\d{4}-W(?:0[1-9]|[1-4]\d|5[0-3])", str(data.get("viikko", ""))):
        raise ValueError("Invalid or missing report week")
    events = data.get("tapahtumat")
    if not isinstance(events, list) or not events:
        raise ValueError("No curated events: keep existing website data and report the gap")
    seen = set()
    for event in events:
        if not isinstance(event, dict):
            raise ValueError("Event must be an object")
        for key in ("nimi", "pvm", "linkki", "kuvaus"):
            if not isinstance(event.get(key), str) or not event[key].strip():
                raise ValueError(f"Missing event field: {key}")
        date.fromisoformat(event["pvm"])
        if event.get("ilmoittautuminen_paattyy"):
            date.fromisoformat(event["ilmoittautuminen_paattyy"])
        link = urlparse(event["linkki"])
        if link.scheme not in ("https", "http") or not link.netloc:
            raise ValueError("Invalid event source URL")
        key = (event["nimi"].casefold(), event["pvm"], event["linkki"])
        if key in seen:
            raise ValueError("Duplicate event")
        seen.add(key)
    if data.get("events") is not None and data["events"] != events:
        raise ValueError("Legacy events mirror differs from curated events")


def normalize_time(value):
    return str(value or "").replace("–", "-").strip()


def normalize_event(event):
    return {
        "name": event.get("nimi", "").strip(),
        "date": event.get("pvm", "").strip(),
        "time": normalize_time(event.get("aika")),
        "location": event.get("paikka", "").strip(),
        "description": (event.get("kuvaus") or event.get("miksi_suositeltu") or "").strip(),
        "url": event.get("linkki", "#").strip(),
        "image": "",
        "source": (event.get("jarjestaja") or "Nousuun.fi").strip(),
        "tags": event.get("tagit", [])[:6],
        "score": event.get("score"),
        "featured": bool(event.get("ennakkonosto", False)),
        "access": event.get("access") or event.get("osallistuminen") or "Tarkista osallistumisehdot järjestäjältä",
        "price": event.get("hinta", "Tarkista järjestäjältä"),
        "registration_deadline": event.get("ilmoittautuminen_paattyy"),
    }


def update_meta(timestamp, week):
    try:
        meta = json.loads(META.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        meta = {"sections": {}}
    meta["updated_at"] = timestamp
    meta.setdefault("sections", {})["events"] = timestamp
    meta.setdefault("weeks", {})["events"] = week
    META.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", help="Path to weekly_event_reports/YYYY-Www_events.json. Defaults to the latest local report.")
    parser.add_argument("--limit", type=int, default=12)
    args = parser.parse_args()

    if args.limit < 1:
        parser.error("--limit must be positive")

    source = Path(args.source).resolve() if args.source else find_latest_report().resolve()
    data = json.loads(source.read_text(encoding="utf-8"))
    validate_report(data)
    timestamp = datetime.now(timezone.utc).isoformat()
    events = [
        normalize_event(event)
        for event in data.get("tapahtumat", [])
        if event.get("sopii_nousuunille", True) and event.get("nimi") and event.get("pvm")
    ]
    if not events:
        raise ValueError("No publishable events; existing website data preserved")
    events.sort(key=lambda item: (item.get("date", ""), -(item.get("score") or 0)))

    payload = {
        "agent": "Agentti A - Tapahtumat",
        "quality": "curated_weekly_report",
        "updated_at": timestamp,
        "week": data.get("viikko"),
        "events": events[: args.limit],
        "source_report": str(source),
    }

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    update_meta(timestamp, data.get("viikko"))
    print(f"Wrote {OUT} from {source} with {len(payload['events'])} events")


if __name__ == "__main__":
    main()
