"""Assemble only platform routes, required styles and public curated data."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '_site'
OUT.mkdir(exist_ok=True)
for page in ROOT.rglob('*.html'):
    if '_site' in page.relative_to(ROOT).parts:
        continue
    target = OUT / page.relative_to(ROOT)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(page, target)
for name in ['CNAME', 'css/style.css', 'js/platform.js', 'js/platform-scope.js', 'js/content-page.js', 'data/events.json', 'data/companies.json', 'data/meta.json']:
    target = OUT / name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / name, target)
print('Built public event platform in _site')
