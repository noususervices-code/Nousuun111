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
    if (!response.ok) throw new Error("Sisällön lataaminen epäonnistui");
    const data = await response.json();
    container.innerHTML = renderFn(data);
    container.dataset.state = "loaded";
  } catch (error) {
    container.innerHTML = '<p class="empty-state">Sisältöä ei saatu ladattua. Kokeile uudelleen.</p>';
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
      <a class="card-link" href="${safeUrl(event.url)}" target="_blank" rel="noopener">Lisätiedot</a>
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
      <a class="card-link" href="${safeUrl(item.url)}" target="_blank" rel="noopener">Avaa lähde</a>
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
      <a class="card-link" href="${safeUrl(article.url)}" target="_blank" rel="noopener">Lue lisää</a>
      <div class="meta-line">Päivitetty ${formatDate(data.updated_at)}</div>
    </article>
  `);
}

function renderCollection(items, template) {
  if (!items.length) {
    return '<p class="empty-state">Tässä osiossa ei ole tällä hetkellä nostoja.</p>';
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
