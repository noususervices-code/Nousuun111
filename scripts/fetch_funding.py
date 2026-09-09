#!/usr/bin/env python3
"""Retired seed writer. Publish verified Agentti D output with sync_section.py."""
import sys

if __name__ == "__main__":
    print("Seed writer retired: use sync_section.py --section funding --source /absolute/path/to/verified.json", file=sys.stderr)
    raise SystemExit(1)
