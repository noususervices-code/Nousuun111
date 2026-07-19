#!/usr/bin/env python3
"""Reject common Finnish-copy regressions before agent data is committed."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

BANNED_ASCII = re.compile(
    r"\b(yrittaja|yrittajan|paatoiminen|tyotapa|tasta|kaytannon|kansainvalinen|yrityksia|pienia|testeja)\b",
    re.IGNORECASE,
)


def text_fields(path: Path, payload: dict):
    name = path.name
    if name == "events.json":
        for item in payload.get("events", []):
            yield "event.name", item.get("name", "")
            yield "event.description", item.get("description", "")
    elif name == "funding.json":
        for item in payload.get("funding", []):
            for key in ("name", "type", "deadline", "summary"):
                yield f"funding.{key}", item.get(key, "")
    elif name == "companies.json":
        for item in payload.get("companies", []):
            for key in ("name", "industry", "location", "insight"):
                yield f"company.{key}", item.get(key, "")
    elif name == "news.json":
        for item in payload.get("articles", []):
            for key in ("title", "source", "summary"):
                yield f"news.{key}", item.get(key, "")


def validate(path: Path):
    payload = json.loads(path.read_text(encoding="utf-8"))
    errors = []
    for label, value in text_fields(path, payload):
        text = str(value or "").strip()
        if "Ã" in text or "Â" in text:
            errors.append(f"{label}: mahdollinen UTF-8-merkistövirhe")
        if BANNED_ASCII.search(text):
            errors.append(f"{label}: ääkkösetön suomen sana: {text}")
        if "…" in text or "..." in text:
            errors.append(f"{label}: katkaistu korttiteksti")

    if path.name == "companies.json":
        companies = payload.get("companies", [])
        insights = [str(item.get("insight", "")).casefold().strip() for item in companies]
        if len(insights) != len(set(insights)):
            errors.append("company.insight: sama kommentti toistuu kahdessa kortissa")
        for item in companies:
            title = str(item.get("name", "")).strip()
            letters = "".join(char for char in title if char.isalpha())
            if letters and letters == letters.upper():
                errors.append(f"company.name: versaaliotsikko: {title}")

    return errors


def main():
    paths = [Path(value) for value in sys.argv[1:]]
    if not paths:
        raise SystemExit("Anna vähintään yksi validoitava JSON-tiedosto.")
    errors = []
    for path in paths:
        errors.extend(f"{path}: {message}" for message in validate(path))
    if errors:
        print("\n".join(errors), file=sys.stderr)
        raise SystemExit(1)
    print(f"Sisältölaatu OK: {len(paths)} tiedostoa")


if __name__ == "__main__":
    main()
