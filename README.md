# Nousuun.fi — event platform

Static GitHub Pages platform for people interested in entrepreneurship, creative industries and wellbeing. Acquisitions are limited to verified creative industries. Beauty, cosmetology and cosmetic surgery are excluded.

Public routes: `/`, `/tapahtumat/`, `/yritykset/`, `/tietosuoja/`. Former media pages redirect to the homepage and carry noindex. Historical content stays in Git history.

Canonical policy: `../MISSION_STATEMENT.md` and `../Agentit/RAJAUS_2026-10-12.md`.

Curated event input: `../Agent_Outputs/Agentti_A_Tapahtumat/weekly_reports/YYYY-Www_events.json`.

Run `python scripts/sync_weekly_events.py --source <report>` to prepare event data. `scout_companies.py` accepts only verified creative-sector listings. Frontend and deployment enforce the same exclusions.

Checks: `python -m unittest discover -s scripts -p "test_*.py"`, `python scripts/validate_content_quality.py data/events.json data/companies.json`, and `python scripts/validate_platform_scope.py`.

`python scripts/build_static_site.py` creates `_site` with public HTML, required CSS/JS and current event/company data only. Backups, scripts, old media data and downloads are not deployed. For preview: `python -m http.server 8765 --directory _site`.
