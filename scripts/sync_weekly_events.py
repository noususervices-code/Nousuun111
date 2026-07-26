#!/usr/bin/env python3
"""Sync a curated weekly event report into the website JSON contract."""

from __future__ import annotations

import argparse
import json
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


def normalize_time(value):
    return str(value or "").replace("–", "-").strip()


def normalize_event(event):
    return {
        "name": event.get("nimi", "").strip(),
        "date": event.get("pvm", "").strip(),
        "time": normalize_time(event.get("aika")),
        "location": event.get("paikka", "").strip(),
        "description": (event.get("miksi_suositeltu") or event.get("kuvaus") or "").strip(),
        "url": event.get("linkki", "#").strip(),
        "image": "",
        "source": (event.get("jarjestaja") or "Nousuun.fi").strip(),
        "tags": event.get("tagit", [])[:6],
        "score": event.get("score"),
        "featured": bool(event.get("ennakkonosto", False)),
        "access": event.get("access", "Avoin ilmoittautuminen"),
        "price": event.get("hinta", "Tarkista järjestäjältä"),
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

    source = Path(args.source).resolve() if args.source else find_latest_report().resolve()
    data = json.loads(source.read_text(encoding="utf-8"))
    timestamp = datetime.now(timezone.utc).isoformat()
    events = [
        normalize_event(event)
        for event in data.get("tapahtumat", [])
        if event.get("sopii_nousuunille", True) and event.get("nimi") and event.get("pvm")
    ]
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
