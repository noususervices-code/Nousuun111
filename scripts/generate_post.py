#!/usr/bin/env python3
"""
Nousuun.fi — Daily Blog Post Generator
Fetches top RSS stories, picks a topic, generates a Finnish blog post via Claude API,
saves the HTML post and updates posts.json.
"""

import os, json, re, random, hashlib, feedparser, requests
from datetime import datetime, timezone
from anthropic import Anthropic

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

# ── RSS FEEDS (verified from Nousuun.fi source report) ──────────────────────
RSS_SOURCES = [
    # Finnish media
    {"url": "https://feeds.kauppalehti.fi/rss/topic/startup",       "tag": "Startup-rahoitus"},
    {"url": "https://feeds.kauppalehti.fi/rss/topic/yrittaminen",   "tag": "Yrittäjyyskasvatus"},
    {"url": "https://www.talouselama.fi/rss.xml",                    "tag": "Startup-rahoitus"},
    {"url": "https://yle.fi/rss/t/18-19274/fi",                     "tag": "Yrittäjyyskasvatus"},
    {"url": "https://arcticstartup.com/feed",                       "tag": "Startup-rahoitus"},
    # Global tech & AI
    {"url": "https://techcrunch.com/category/artificial-intelligence/feed/", "tag": "Tekoäly pk-yrityksille"},
    {"url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", "tag": "Tekoäly pk-yrityksille"},
    {"url": "https://sifted.eu/feed",                               "tag": "Startup-rahoitus"},
    # Solopreneur / growth
    {"url": "https://fortelabs.com/feed/",                          "tag": "Henkilöbrändäys"},
    {"url": "https://sahilbloom.substack.com/feed",                 "tag": "Yrittäjyyskasvatus"},
    {"url": "https://dickiebush.substack.com/feed",                 "tag": "Henkilöbrändäys"},
    {"url": "https://ducttapemarketing.com/feed/",                  "tag": "Henkilöbrändäys"},
]

TAGS = [
    "Yrittäjyyskasvatus",
    "Tekoäly pk-yrityksille",
    "Startup-rahoitus",
    "Henkilöbrändäys",
    "Nuorisoyrittäjyys",
]

TAG_SLUGS = {
    "Yrittäjyyskasvatus":    "yrittajyyskasvatus",
    "Tekoäly pk-yrityksille": "tekoaly-pk-yrityksille",
    "Startup-rahoitus":      "startup-rahoitus",
    "Henkilöbrändäys":       "henkilobrandays",
    "Nuorisoyrittäjyys":     "nuorisoyrittajyys",
}

POSTS_JSON = "blog/posts.json"


def fetch_rss_headlines(tag_filter=None):
    """Fetch latest headlines from RSS feeds, optionally filtered by tag."""
    headlines = []
    sources = [s for s in RSS_SOURCES if tag_filter is None or s["tag"] == tag_filter]
    for source in sources[:6]:  # max 6 feeds per run
        try:
            feed = feedparser.parse(source["url"])
            for entry in feed.entries[:3]:
                title = entry.get("title", "")
                summary = entry.get("summary", "")[:300]
                if title:
                    headlines.append({
                        "title": title,
                        "summary": summary,
                        "source_tag": source["tag"],
                        "feed_url": source["url"],
                    })
        except Exception as e:
            print(f"RSS error {source['url']}: {e}")
    return headlines


def pick_tag():
    """Rotate through tags so each gets roughly equal coverage."""
    force = os.environ.get("FORCE_TAG", "auto")
    if force and force != "auto" and force in TAGS:
        return force
    try:
        with open(POSTS_JSON) as f:
            posts = json.load(f)
        # Count occurrences per tag
        counts = {t: 0 for t in TAGS}
        for p in posts:
            for t in p.get("tags", []):
                if t in counts:
                    counts[t] += 1
        # Pick the least-used tag
        return min(counts, key=counts.get)
    except Exception:
        return random.choice(TAGS)


def generate_slug(title):
    """Create a URL-safe slug from a Finnish title."""
    slug = title.lower()
    replacements = {"ä": "a", "ö": "o", "å": "a", "é": "e", "ü": "u"}
    for a, b in replacements.items():
        slug = slug.replace(a, b)
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = re.sub(r'-+', '-', slug)
    return slug[:60]


def generate_post(tag, headlines):
    """Call Claude API to generate a Finnish blog post."""
    headlines_text = "\n".join(
        f"- [{h['source_tag']}] {h['title']}: {h['summary']}"
        for h in headlines[:8]
    )

    prompt = f"""Olet Jaakko Kalke — suomalainen yrittäjä, startup-rahoituksen asiantuntija ja fasilitaattori. 
Kirjoitat blogikirjoituksia sivustolle nousuun.fi, jonka teema on "Autetaan toinen toisiamme nousuun".

Tänään kirjoitat aiheesta: **{tag}**

Tässä tämän päivän tuoreimmat uutisotsikot inspiraatioksi (älä kopioi suoraan, käytä inspiraationa):
{headlines_text}

Kirjoita yksi laadukas, käytännönläheinen blogikirjoitus suomeksi. Muista:
- Sävy: lämmin, suora, fasilitaattori — ei guru
- Et anna valmiita vastauksia, autat lukijaa ajattelemaan
- Käytännön esimerkit ja konkreettiset vinkit
- Suomalainen konteksti (startup-ekosysteemi, pk-yritykset, Helsinki)
- Pituus: 500-800 sanaa
- Rakenne: johdanto + 2-3 väliotsikkoa (##) + lopetus

Palauta VAIN JSON seuraavassa muodossa, ei muuta tekstiä:
{{
  "title": "Otsikko tähän",
  "excerpt": "Lyhyt kuvaus max 160 merkkiä",
  "body_html": "<p>Artikkelin sisältö HTML-muodossa. Käytä <p>, <h2>, <blockquote> tageja.</p>",
  "read_time": "5 min"
}}"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text.strip()
    # Strip markdown fences if present
    raw = re.sub(r'^```json\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    return json.loads(raw)


def build_post_html(slug, title, tag, excerpt, body_html, date_label, date_iso, read_time, source_note):
    """Build the complete HTML page for a blog post."""
    tag_slug = TAG_SLUGS.get(tag, "")
    return f"""<!DOCTYPE html>
<html lang="fi">
<head>
  <meta charset="UTF-8"/><meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <meta name="description" content="{excerpt}"/>
  <title>{title} — Nousuun.fi</title>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Fraunces:ital,wght@0,300;0,700;1,300;1,700&display=swap" rel="stylesheet"/>
  <link rel="stylesheet" href="../css/style.css"/>
</head>
<body>
<nav>
  <a href="/" class="logo"><div class="logo-mark"><svg viewBox="0 0 20 20"><path d="M3 14 L10 5 L17 14" stroke="white" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/><circle cx="10" cy="5" r="2" fill="white"/></svg></div><span class="logo-text">nousuun<span>.fi</span></span></a>
  <ul class="nav-links"><li><a href="/#about">Minusta</a></li><li><a href="/blog/">Blogi</a></li></ul>
  <a href="/#contact" class="nav-btn">Ota yhteyttä</a>
</nav>

<article class="post-page">
  <a href="/blog/" class="back-link">← Kaikki kirjoitukset</a>
  <header class="post-header">
    <span class="post-cat-badge">{tag}</span>
    <h1>{title}</h1>
    <p class="post-meta">Jaakko Kalke · {date_label} · {read_time} lukuaika</p>
    <span class="ai-badge">🤖 AI-avusteinen · {source_note}</span>
  </header>
  <div class="post-body">
    {body_html}
  </div>
  <div class="post-tags">
    <span style="font-size:0.8rem;color:var(--muted);margin-right:0.5rem;">Tagit:</span>
    <a href="/blog/tags/{tag_slug}.html" class="ptag">{tag}</a>
  </div>
</article>

<section class="contact" id="contact" style="padding:4rem 5vw;">
  <div class="contact-inner">
    <h2 style="font-size:1.8rem;">Noustaan yhdessä.</h2>
    <p>Haluatko sparrata? Kirjoita minulle.</p>
    <a href="mailto:jaakko@nousuun.fi" class="btn-white">jaakko@nousuun.fi →</a>
  </div>
</section>

<footer>
  <a href="/" class="footer-logo">nousuun<span>.fi</span></a>
  <ul class="footer-links"><li><a href="/blog/">Blogi</a></li><li><a href="https://linkedin.com/in/jaakkokalke" target="_blank">LinkedIn</a></li></ul>
  <span>© 2026 Jaakko Kalke</span>
</footer>
<script src="../js/main.js"></script>
</body>
</html>"""


def update_posts_json(new_post_meta):
    """Prepend the new post to posts.json."""
    try:
        with open(POSTS_JSON) as f:
            posts = json.load(f)
    except Exception:
        posts = []

    # Check for duplicate slugs
    existing_slugs = {p["slug"] for p in posts}
    if new_post_meta["slug"] in existing_slugs:
        # Make unique
        new_post_meta["slug"] += f"-{datetime.now().strftime('%H%M')}"

    posts.insert(0, new_post_meta)
    with open(POSTS_JSON, "w") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
    print(f"Updated posts.json — now {len(posts)} posts")


def main():
    print("🚀 Nousuun.fi daily blog generator starting...")

    # 1. Pick tag
    tag = pick_tag()
    print(f"📌 Tag: {tag}")

    # 2. Fetch RSS headlines for context
    headlines = fetch_rss_headlines(tag_filter=tag)
    if not headlines:
        headlines = fetch_rss_headlines()  # fallback: any tag
    print(f"📰 Fetched {len(headlines)} headlines")

    # 3. Generate post via Claude
    print("✍️  Generating post with Claude...")
    result = generate_post(tag, headlines)

    title = result["title"]
    excerpt = result["excerpt"]
    body_html = result["body_html"]
    read_time = result.get("read_time", "5 min")

    # 4. Build metadata
    now = datetime.now(timezone.utc)
    date_iso = now.strftime("%Y-%m-%d")
    months_fi = ["", "tammikuuta", "helmikuuta", "maaliskuuta", "huhtikuuta",
                 "toukokuuta", "kesäkuuta", "heinäkuuta", "elokuuta",
                 "syyskuuta", "lokakuuta", "marraskuuta", "joulukuuta"]
    date_label = f"{now.day}. {months_fi[now.month]} {now.year}"
    slug = generate_slug(title)
    source_note = "Inspiroitu: " + ", ".join(set(h["feed_url"].split("/")[2] for h in headlines[:3]))

    # 5. Save HTML file
    html_path = f"blog/{slug}.html"
    with open(html_path, "w") as f:
        f.write(build_post_html(slug, title, tag, excerpt, body_html,
                                date_label, date_iso, read_time, source_note))
    print(f"✅ Saved: {html_path}")

    # 6. Update posts.json
    post_meta = {
        "slug": slug,
        "title": title,
        "category": tag,
        "tags": [tag],
        "date": date_iso,
        "dateLabel": date_label,
        "excerpt": excerpt,
        "readTime": read_time,
        "source": source_note,
        "featured": False,
        "auto_generated": True,
    }
    update_posts_json(post_meta)
    print(f"🎉 Done! Post: {title}")


if __name__ == "__main__":
    main()
