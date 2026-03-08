# Nousuun.fi

Jaakko Kalken henkilökohtainen sivusto — yrittäjyys, AI ja kasvu.

## Rakenne

```
nousuun-fi/
├── index.html          # Etusivu (hero, about, blog-preview, contact)
├── css/
│   └── style.css       # Kaikki tyylit
├── js/
│   └── main.js         # Scroll reveal, mobiilinavigaatio, blog loader
├── blog/
│   ├── index.html      # Blogilistasivu
│   ├── posts.json      # Blogijulkaisujen metadata
│   ├── frontier-work.html   # Esimerkkikirjoitus
│   └── [slug].html     # Uudet kirjoitukset tähän
└── images/             # Kuvat tähän
```

## Uuden blogikirjoituksen lisääminen

1. Kopioi `blog/frontier-work.html` uudeksi tiedostoksi, esim. `blog/oma-aihe.html`
2. Muokkaa sisältö
3. Lisää merkintä `blog/posts.json` -tiedostoon:

```json
{
  "slug": "oma-aihe",
  "title": "Otsikko tähän",
  "category": "Kategoria",
  "date": "Huhtikuu 2026",
  "excerpt": "Lyhyt kuvaus kirjoituksesta."
}
```

## GitHub Pages -käyttöönotto

1. Luo uusi GitHub-repositorio: `nousuun-fi`
2. Push tiedostot `main`-haaraan
3. GitHub Settings → Pages → Source: `main` / `root`
4. Sivusto näkyy osoitteessa `https://[käyttäjänimi].github.io/nousuun-fi/`
5. Lisää custom domain `nousuun.fi` DNS-asetuksissa (CNAME-tietue)

## Teknologia

- Puhdas HTML/CSS/JS — ei frameworkeja, ei build-prosessia
- Google Fonts: Syne + Instrument Serif + DM Sans
- GitHub Pages yhteensopiva suoraan
