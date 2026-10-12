"""Reject excluded sectors and unverified creative acquisitions before publication."""
import json
from pathlib import Path
from scout_companies import EXCLUDED_SECTORS, creative_sector

ROOT = Path(__file__).resolve().parents[1]

def validate():
    errors = []
    for filename, key in [('events.json', 'events'), ('companies.json', 'companies')]:
        payload = json.loads((ROOT / 'data' / filename).read_text(encoding='utf-8'))
        for item in payload.get(key, []):
            text = json.dumps(item, ensure_ascii=False)
            if EXCLUDED_SECTORS.search(text):
                errors.append(f'{filename}: excluded sector: {item.get("name")}')
            if key == 'companies' and (item.get('creative_sector_verified') is not True or not item.get('creative_sector') or not creative_sector(item)):
                errors.append(f'{filename}: creative sector not verified: {item.get("name")}')
    return errors

if __name__ == '__main__':
    errors = validate()
    if errors:
        raise SystemExit('\n'.join(errors))
    print('Platform scope OK: events and creative acquisitions')
