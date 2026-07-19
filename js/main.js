const FALLBACKS = {
  "events.json": {
    updated_at: "2026-05-17T09:00:00+03:00",
    events: [
      {
        name: "Yritystä Stadiin",
        date: "2026-05-26",
        time: "16:00",
        location: "Helsinki",
        description: "Tapahtuma aloittaville ja kasvua hakeville yrittäjille. Hyvä paikka tavata muita tekijöitä ja kerätä konkreettisia neuvoja.",
        url: "https://www.hel.fi/",
        source: "manual seed",
        tags: ["verkosto", "startup"]
      },
      {
        name: "AI ja arjen automaatio yrittäjälle",
        date: "2026-05-28",
        time: "09:00",
        location: "Online",
        description: "Käytännön sessio siitä, miten yksinyrittäjä voi vapauttaa aikaa tekoälyn, no-code-työkalujen ja selkeiden prosessien avulla.",
        url: "#",
        source: "manual seed",
        tags: ["AI", "automaatio"]
      },
      {
        name: "Kasvuyrittäjän aamukahvit",
        date: "2026-06-02",
        time: "08:30",
        location: "Uusimaa",
        description: "Matala kynnys, korkea hyöty. Keskustelua rahoituksesta, asiakkaista ja yrittäjän seuraavasta askeleesta.",
        url: "#",
        source: "manual seed",
        tags: ["kasvu", "yhteiso"]
      }
    ]
  },
  "companies.json": {
    updated_at: "2026-05-17T09:00:00+03:00",
    week: "2026-W20",
    companies: [
      {
        name: "Paikallinen palveluyritys",
        industry: "Palvelut",
        price: "Alle 150 000 euroa",
        location: "Etelä-Suomi",
        score: 8.2,
        insight: "Kassavirtaa tuottava palveluyritys, jossa AI voi auttaa myynnissä, asiakaspalvelussa ja raportoinnissa. Sopii tekijälle, joka haluaa ostaa valmiin pohjan eikä aloittaa tyhjästä.",
        url: "#",
        source: "manual seed"
      },
      {
        name: "Verkkokauppa niche-markkinassa",
        industry: "Kauppa",
        price: "Neuvoteltavissa",
        location: "Suomi",
        score: 7.7,
        insight: "Pieni mutta selkeä kohderyhmä. Kasvua voisi hakea sisältömarkkinoinnilla, automaatiolla ja eurooppalaisella jakelulla.",
        url: "#",
        source: "manual seed"
      },
      {
        name: "B2B-koulutuskonsepti",
        industry: "Koulutus",
        price: "Ei julkinen",
        location: "Helsinki",
        score: 7.4,
        insight: "Asiantuntijapalvelu, jonka voi tuotteistaa kurssiksi, yhteisöksi tai lisensoitavaksi malliksi. Hyvä esimerkki osaamisen skaalaamisesta.",
        url: "#",
        source: "manual seed"
      }
    ]
  },
  "funding.json": {
    updated_at: "2026-05-17T09:00:00+03:00",
    funding: [
      {
        name: "Starttiraha",
        type: "Alkuvaiheen tuki",
        deadline: "Jatkuva haku",
        region: "Suomi",
        summary: "Aloittavan päätoimisen yrittäjän henkilökohtainen tuki yritystoiminnan ensimmäisiin kuukausiin. Tarkista ehdot oman alueesi työllisyyspalveluista.",
        url: "https://www.suomi.fi/palvelut/starttiraha-tyollisyyspalvelut/55b76e7f-e4f6-4b9f-b2f1-b0ce7791e214",
        source: "manual seed"
      },
      {
        name: "Business Finland Sprint",
        type: "Kansainvälinen kasvu",
        deadline: "Jatkuva haku 1.9.2026 alkaen",
        region: "Suomi",
        summary: "Rahoitus pienille innovatiivisille yrityksille, jotka kehittävät uutta ratkaisua ja tavoittelevat nopeaa kansainvälistä kasvua.",
        url: "https://www.businessfinland.fi/palvelut/rahoitus/haut/2026/sprint-rahoitushaku/",
        source: "manual seed"
      },
      {
        name: "EU-ohjelmat pk-yrityksille",
        type: "Eurooppa",
        deadline: "Vaihtelee",
        region: "EU",
        summary: "EU-hakuja kannattaa seurata erityisesti digitalisaation, vastuullisuuden ja kasvun teemoissa. Nousuun voi tiivistää haun yrittäjän kielelle.",
        url: "https://commission.europa.eu/funding-tenders_en",
        source: "manual seed"
      }
    ]
  },
  "news.json": {
    updated_at: "2026-05-17T09:00:00+03:00",
    articles: [
      {
        title: "AI ei ole osasto. Se on työtapa.",
        source: "Nousuun.fi",
        relevance_score: 9,
        summary: "Pienyrittäjän kannattaa aloittaa yhdestä arjen prosessista: myyntiviestit, tarjoukset, asiakaspalvelu tai raportointi. Vasta sen jälkeen rakennetaan automaatio.",
        url: "blog/"
      },
      {
        title: "Eurooppa etsii uusia kasvuyrittäjiä",
        source: "Nousuun.fi",
        relevance_score: 8,
        summary: "Uusi markkina ei tarkoita vain vientiä. Se voi tarkoittaa kumppaneita, ostettavia yrityksiä, EU-rahoitusta ja pieniä testejä rajojen yli.",
        url: "blog/"
      },
      {
        title: "Yrityksen ostaminen voi olla nopeampi alku kuin perustaminen",
        source: "Nousuun.fi",
        relevance_score: 8,
        summary: "Omistajanvaihdokset ovat usein alihyödynnetty polku yrittäjyyteen. AI voi parantaa due diligencea, markkinointia ja operointia.",
        url: "blog/"
      }
    ]
  }
};

const sectionConfig = [
  ["events.json", "events-section", renderEvents],
  ["companies.json", "companies-section", renderCompanies],
  ["funding.json", "funding-section", renderFunding],
  ["news.json", "news-section", renderNews]
];

async function loadSection(dataFile, containerId, renderFn) {
  const container = document.getElementById(containerId);
  if (!container) return;

  try {
    const response = await fetch(`data/${dataFile}`, { cache: "no-store" });
    const data = response.ok ? await response.json() : FALLBACKS[dataFile];
    container.innerHTML = renderFn(data || FALLBACKS[dataFile]);
    container.dataset.state = "loaded";
  } catch (error) {
    container.innerHTML = renderFn(FALLBACKS[dataFile]);
    container.dataset.state = "fallback";
  }
}

function renderEvents(data) {
  const events = Array.isArray(data.events) ? data.events : [];
  return renderCollection(events, (event) => `
    <article class="data-card">
      <p class="eyebrow">${escapeHtml(formatEventEyebrow(event))}</p>
      <h3>${escapeHtml(event.name)}</h3>
      <p>${escapeHtml(event.description || "")}</p>
      <a class="card-link" href="${safeUrl(event.url)}" target="_blank" rel="noopener">Lisatiedot</a>
      <div class="meta-line">${escapeHtml([event.date, event.time, event.location].filter(Boolean).join(" / "))}</div>
    </article>
  `);
}

function formatEventEyebrow(event) {
  const tags = (event.tags || ["tapahtuma"]).slice(0, 3).join(" / ");
  const score = event.score ? `Score ${event.score}/10` : "";
  const featured = event.featured ? "Ennakkonosto" : "";
  return [score, featured, tags].filter(Boolean).join(" / ");
}

function renderCompanies(data) {
  const companies = Array.isArray(data.companies) ? data.companies : [];
  return renderCollection(companies, (company) => `
    <article class="data-card">
      <p class="eyebrow">Score ${escapeHtml(company.score || "-")}/10 / ${escapeHtml(company.industry || "yritys")}</p>
      <h3>${escapeHtml(company.name)}</h3>
      <p>${escapeHtml(company.insight || "")}</p>
      <a class="card-link" href="${safeUrl(company.url)}" target="_blank" rel="noopener">Katso ilmoitus</a>
      <div class="meta-line">${escapeHtml([company.location, company.price].filter(Boolean).join(" / "))}</div>
    </article>
  `);
}

function renderFunding(data) {
  const funding = Array.isArray(data.funding) ? data.funding : [];
  return renderCollection(funding, (item) => `
    <article class="data-card">
      <p class="eyebrow">${escapeHtml([item.type, item.region].filter(Boolean).join(" / "))}</p>
      <h3>${escapeHtml(item.name)}</h3>
      <p>${escapeHtml(item.summary || "")}</p>
      <a class="card-link" href="${safeUrl(item.url)}" target="_blank" rel="noopener">Avaa lahde</a>
      <div class="meta-line">${escapeHtml(item.deadline || "Seurannassa")}</div>
    </article>
  `);
}

function renderNews(data) {
  const articles = Array.isArray(data.articles) ? data.articles : [];
  return renderCollection(articles, (article) => `
    <article class="data-card">
      <p class="eyebrow">${escapeHtml(article.source || "Nousuun.fi")} / ${escapeHtml(article.relevance_score || "-")}/10</p>
      <h3>${escapeHtml(article.title)}</h3>
      <p>${escapeHtml(article.summary || "")}</p>
      <a class="card-link" href="${safeUrl(article.url)}" target="_blank" rel="noopener">Lue lisaa</a>
      <div class="meta-line">Paivitetty ${formatDate(data.updated_at)}</div>
    </article>
  `);
}

function renderCollection(items, template) {
  if (!items.length) {
    return '<p class="empty-state">Ei nostoja viela. Agentti paivittaa taman osion seuraavassa ajossa.</p>';
  }
  return items.slice(0, 6).map(template).join("");
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function safeUrl(value) {
  const url = String(value || "#");
  if (url.startsWith("http://") || url.startsWith("https://") || url.startsWith("/") || url.startsWith("#") || url.startsWith("blog/")) {
    return escapeHtml(url);
  }
  return "#";
}

function formatDate(value) {
  if (!value) return "pian";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "pian";
  return date.toLocaleDateString("fi-FI");
}

document.addEventListener("DOMContentLoaded", () => {
  sectionConfig.forEach(([file, container, renderer]) => loadSection(file, container, renderer));
});
