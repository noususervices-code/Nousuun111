#!/usr/bin/env python3
"""Validate and sync Nousuun.fi funding or news JSON into the website data."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
META_PATH = DATA_DIR / "meta.json"
WEEK_RE = re.compile(r"^\d{4}-W(?:0[1-9]|[1-4]\d|5[0-3])$")
REQUIRED_FIELDS = {
    "funding": ("name", "summary", "deadline", "url"),
    "news": ("title", "source", "summary", "url"),
}
ARRAY_KEYS = {"funding": "funding", "news": "articles"}


class ValidationError(ValueError):
    """Raised when a source or metadata file violates the sync contract."""


def load_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValidationError(f"{label} ei löydy: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(
            f"{label} ei ole validia JSONia: {path} (rivi {exc.lineno}, sarake {exc.colno})"
        ) from exc
    if not isinstance(value, dict):
        raise ValidationError(f"{label} ylimmän tason pitää olla JSON-objekti: {path}")
    return value


def is_http_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def validate_source(section: str, source: Path) -> tuple[dict[str, Any], int]:
    payload = load_object(source, "Lähdetiedosto")
    array_key = ARRAY_KEYS[section]
    items = payload.get(array_key)
    if not isinstance(items, list):
        raise ValidationError(f"Lähteestä puuttuu taulukko '{array_key}'.")

    minimum, maximum = (3, None) if section == "funding" else (3, 5)
    if len(items) < minimum or (maximum is not None and len(items) > maximum):
        expected = f"vähintään {minimum}" if maximum is None else f"{minimum}–{maximum}"
        raise ValidationError(
            f"Osion '{section}' taulukossa '{array_key}' pitää olla {expected} alkiota; löytyi {len(items)}."
        )

    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            raise ValidationError(f"{array_key}[{index}] ei ole JSON-objekti.")
        for field in REQUIRED_FIELDS[section]:
            value = item.get(field)
            if not isinstance(value, str) or not value.strip():
                raise ValidationError(f"{array_key}[{index}].{field} puuttuu tai on tyhjä.")
        if not is_http_url(item["url"].strip()):
            raise ValidationError(f"{array_key}[{index}].url ei ole kelvollinen http(s)-URL.")

    return payload, len(items)


def source_week(payload: dict[str, Any]) -> str:
    week = payload.get("week")
    if isinstance(week, str) and WEEK_RE.fullmatch(week):
        return week
    now = datetime.now(ZoneInfo("Europe/Helsinki"))
    iso = now.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", newline="\n", dir=path.parent, delete=False
    ) as handle:
        handle.write(encoded)
        temp_path = Path(handle.name)
    try:
        os.replace(temp_path, path)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise


def sync(section: str, source: Path) -> tuple[Path, Path, int, str]:
    if not source.is_absolute():
        raise ValidationError("--source-polun pitää olla absoluuttinen.")
    payload, item_count = validate_source(section, source)
    meta = load_object(META_PATH, "Metadata")

    target = DATA_DIR / f"{section}.json"
    backup = DATA_DIR / f"{section}.previous.json"
    if target.exists():
        shutil.copy2(target, backup)

    timestamp = datetime.now(ZoneInfo("Europe/Helsinki")).isoformat()
    week = source_week(payload)
    updated_meta = dict(meta)
    updated_meta["updated_at"] = timestamp
    updated_meta["sections"] = dict(meta.get("sections") or {})
    updated_meta["sections"][section] = timestamp
    updated_meta["weeks"] = dict(meta.get("weeks") or {})
    updated_meta["weeks"][section] = week

    # Both payloads have been fully validated before either destination is replaced.
    atomic_write_json(target, payload)
    try:
        atomic_write_json(META_PATH, updated_meta)
    except Exception:
        if backup.exists():
            shutil.copy2(backup, target)
        raise

    return target, backup, item_count, week


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Synkronoi validoitu funding- tai news-JSON Nousuun.fi-sivustolle."
    )
    parser.add_argument("--section", required=True, choices=sorted(ARRAY_KEYS))
    parser.add_argument("--source", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        target, backup, item_count, week = sync(args.section, args.source)
    except (ValidationError, OSError) as exc:
        print(f"VIRHE: {exc}", file=sys.stderr)
        return 1
    print(
        f"OK: {args.section} synkronoitu ({item_count} alkiota, {week}) -> {target}. "
        f"Varmuuskopio: {backup}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
