# Nousuun.fi — Jaakko Kalke

> "Autetaan toinen toisiamme nousuun."

## Rakenne

```
nousuun-fi/
├── index.html                    # Etusivu
├── css/style.css                 # Kaikki tyylit
├── js/main.js                    # Scroll reveal
├── blog/
│   ├── index.html                # Blogilistasivu
│   ├── posts.json                # Kaikkien postausten metadata
│   ├── tags/
│   │   ├── yrittajyyskasvatus.html
│   │   ├── tekoaly-pk-yrityksille.html
│   │   ├── startup-rahoitus.html
│   │   ├── henkilobrandays.html
│   │   └── nuorisoyrittajyys.html
│   └── [slug].html               # Yksittäiset blogikirjoitukset
├── scripts/
│   └── generate_post.py          # Automaattinen blogigeneraattori
└── .github/workflows/
    └── daily-blog.yml            # GitHub Actions: ajaa joka päivä klo 7
```

---

## 🤖 Automaattinen päivittäinen blogi

Sivusto generoi automaattisesti yhden blogikirjoituksen päivässä Claude AI:n avulla.

### Miten se toimii

1. **GitHub Actions** käynnistää skriptin joka päivä klo 07:00 (Helsinki)
2. **`generate_post.py`** hakee tuoreimmat otsikot 12 RSS-syötteestä (Kauppalehti, TechCrunch AI, Sifted, jne.)
3. **Claude API** kirjoittaa suomenkielisen blogikirjoituksen sinun äänelläsi inspiraationa RSS-uutiset
4. Tägit **rotatoivat automaattisesti** tasaisesti kaikkien 5 tägikategorian välillä
5. Uusi HTML-tiedosto + `posts.json`-päivitys **commitataan GitHubiin** automaattisesti

### Käyttöönotto (kerran)

#### 1. Aseta ANTHROPIC_API_KEY

GitHub repo → Settings → Secrets and variables → Actions → New repository secret:
- Name: `ANTHROPIC_API_KEY`
- Value: sinun Anthropic API -avaimesi (https://console.anthropic.com)

#### 2. Aktivoi GitHub Pages

Settings → Pages → Source: `main` / `root`

#### 3. Valmis! 🎉

Joka aamu klo 07:00 ilmestyy uusi kirjoitus.

### Manuaalinen trigger

GitHub → Actions → "Daily Blog Post Generator" → "Run workflow"
Voit valita tägikategorian pakotetusti.

---

## Uuden blogikirjoituksen lisääminen käsin

1. Kopioi `blog/frontier-work-tekoaly-rajapinta.html` → nimeä uudella slugilla
2. Muokkaa sisältö
3. Lisää `blog/posts.json` alkuun:

```json
{
  "slug": "oma-slug",
  "title": "Otsikko",
  "category": "Startup-rahoitus",
  "tags": ["Startup-rahoitus"],
  "date": "2026-03-10",
  "dateLabel": "10. maaliskuuta 2026",
  "excerpt": "Lyhyt kuvaus.",
  "readTime": "5 min",
  "source": "Alkuperäinen",
  "featured": false
}
```

---

## Tägikategoriat

| Tägisivu | URL |
|---|---|
| Yrittäjyyskasvatus | /blog/tags/yrittajyyskasvatus.html |
| Tekoäly pk-yrityksille | /blog/tags/tekoaly-pk-yrityksille.html |
| Startup-rahoitus | /blog/tags/startup-rahoitus.html |
| Henkilöbrändäys | /blog/tags/henkilobrandays.html |
| Nuorisoyrittäjyys | /blog/tags/nuorisoyrittajyys.html |

---

## GitHub Pages + Custom domain

1. Luo repo: `nousuun-fi`
2. Push `main`-haaraan
3. Settings → Pages → Source: main / root
4. DNS: CNAME `nousuun.fi` → `[käyttäjänimi].github.io`
