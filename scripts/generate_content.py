#!/usr/bin/env python3
"""Generate the weekly news JSON placeholder for Nousuun.fi.

This script is intentionally conservative until the editorial prompt and API
review flow are locked. It updates data/news.json using a stable schema.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "news.json"


def main():
    OUT.parent.mkdir(exist_ok=True)
    payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "articles": [
            {
                "title": "AI ei ole osasto. Se on työtapa.",
                "source": "Nousuun.fi",
                "relevance_score": 9,
                "summary": "Aloita yhdestä arjen prosessista: myyntiviestit, tarjoukset, asiakaspalvelu tai raportointi.",
                "url": "blog/",
            },
            {
                "title": "Eurooppa etsii uusia kasvuyrittäjiä",
                "source": "Nousuun.fi",
                "relevance_score": 8,
                "summary": "Uusi markkina voi tarkoittaa kumppaneita, ostettavia yrityksiä, EU-rahoitusta ja pieniä testejä rajojen yli.",
                "url": "blog/",
            },
        ],
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
