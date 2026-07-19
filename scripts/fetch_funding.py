#!/usr/bin/env python3
"""Update funding opportunities for Nousuun.fi."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "funding.json"


def main():
    OUT.parent.mkdir(exist_ok=True)
    payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "funding": [
            {
                "name": "Starttiraha",
                "type": "Alkuvaiheen tuki",
                "deadline": "Jatkuva haku",
                "region": "Suomi",
                "summary": "Aloittavan päätoimisen yrittäjän henkilökohtainen tuki yritystoiminnan ensimmäisiin kuukausiin.",
                "url": "https://www.suomi.fi/palvelut/starttiraha-tyollisyyspalvelut/55b76e7f-e4f6-4b9f-b2f1-b0ce7791e214",
                "source": "manual seed",
            },
            {
                "name": "Business Finland Sprint",
                "type": "Kansainvälinen kasvu",
                "deadline": "Jatkuva haku 1.9.2026 alkaen",
                "region": "Suomi",
                "summary": "Rahoitus pienille innovatiivisille yrityksille, jotka kehittävät uutta ratkaisua ja tavoittelevat nopeaa kansainvälistä kasvua.",
                "url": "https://www.businessfinland.fi/palvelut/rahoitus/haut/2026/sprint-rahoitushaku/",
                "source": "Business Finland",
            },
        ],
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
