# Nousuun.fi v4

Nousuun.fi v4 is a static GitHub Pages site for rising entrepreneurs in Finland
and Europe. The site is designed as an entrepreneur's morning meeting: fresh
events, company opportunities, funding picks and news in one clear place.

## Structure

```text
.
├── index.html
├── tapahtumat/
├── yritykset/
├── rahoitus/
├── uutiset/
├── blog/
├── data/
├── css/style.css
├── js/main.js
├── scripts/
└── .github/workflows/
```

## Design

The visual system is based on the provided DESIGN.md file:

- monochrome core: black ink, white canvas
- oversized pastel color-block sections
- pill CTAs
- Inter + JetBrains Mono as open-source substitutes for Figma Sans/Mono
- flat editorial layout, no heavy shadows or gradients

## Agents

| Agent | Output | Schedule |
| --- | --- | --- |
| `Agentti A` | `data/events.json` | Curated weekly prompt + local sync |
| `scout-agent` | `data/companies.json` | Monday |
| `funding-agent` | `data/funding.json` | Monday |
| `content-agent` | `data/news.json` + later `blog/` | Tuesday + Friday |

## Local Preview

```bash
python -m http.server 8000
```

Then open `http://localhost:8000`.

## Agentti A Route

Agentti A is not the raw Linked Events fallback. The source of truth is the
weekly curated event report under the memory center:

```text
../04_Community/Events/weekly_event_reports/YYYY-Www_events.json
```

Sync the latest report into the website contract:

```bash
python scripts/sync_weekly_events.py
```

The GitHub workflow `Agentti A - Tapahtumat fallback` is manual-only and should
be used only when there is no curated weekly report.
