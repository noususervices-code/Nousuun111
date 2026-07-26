const page = document.querySelector("[data-content-page]");
const target = document.getElementById("content-list");
const statusLine = document.getElementById("content-status");

const escapeText = value => String(value ?? "")
  .replaceAll("&", "&amp;")
  .replaceAll("<", "&lt;")
  .replaceAll(">", "&gt;")
  .replaceAll('"', "&quot;")
  .replaceAll("'", "&#039;");

const safeLink = value => {
  const url = String(value || "");
  return /^(https?:\/\/|\/)/.test(url) ? escapeText(url) : "#";
};

const fiDate = value => {
  const date = new Date(`${value}T12:00:00`);
  return Number.isNaN(date.getTime())
    ? escapeText(value)
    : date.toLocaleDateString("fi-FI", { day: "numeric", month: "long", year: "numeric" });
};

const renderEvent = item => `
  <article class="archive-card">
    <div class="archive-card-top">
      <span class="archive-score">${escapeText(item.score || "–")}/10</span>
      <span>${fiDate(item.date)}</span>
    </div>
    <h2>${escapeText(item.name)}</h2>
    <p>${escapeText(item.description || "")}</p>
    <dl class="archive-facts">
      <div><dt>Aika</dt><dd>${escapeText(item.time || "Tarkista järjestäjältä")}</dd></div>
      <div><dt>Paikka</dt><dd>${escapeText(item.location || "Tarkista järjestäjältä")}</dd></div>
      <div><dt>Järjestäjä</dt><dd>${escapeText(item.source || "–")}</dd></div>
    </dl>
    <a class="text-link" href="${safeLink(item.url)}" target="_blank" rel="noopener">Avaa tapahtumasivu →</a>
  </article>`;

const renderCompany = item => `
  <article class="archive-card">
    <div class="archive-card-top">
      <span class="archive-score">${escapeText(item.score || "–")}/10</span>
      <span>${escapeText(item.location || "Suomi")}</span>
    </div>
    <h2>${escapeText(item.name)}</h2>
    <p>${escapeText(item.insight || "")}</p>
    <dl class="archive-facts">
      <div><dt>Toimiala</dt><dd>${escapeText(item.industry || "–")}</dd></div>
      <div><dt>Hintapyyntö</dt><dd>${escapeText(item.price || "Ei ilmoitettu")}</dd></div>
      <div><dt>Lähde</dt><dd>${escapeText(item.source || "–")}</dd></div>
    </dl>
    <a class="text-link" href="${safeLink(item.url)}" target="_blank" rel="noopener">Katso alkuperäinen ilmoitus →</a>
  </article>`;

const renderArticle = item => `
  <article class="archive-card">
    <div class="archive-card-top">
      <span class="archive-score">${escapeText(item.relevance_score || "–")}/10</span>
      <span>${escapeText(item.source || "")}</span>
    </div>
    <h2>${escapeText(item.title)}</h2>
    <p>${escapeText(item.summary || "")}</p>
    <a class="text-link" href="${safeLink(item.url)}" target="_blank" rel="noopener">Lue alkuperäinen lähde →</a>
  </article>`;

const configs = {
  events: { file: "../data/events.json", key: "events", render: renderEvent },
  companies: { file: "../data/companies.json", key: "companies", render: renderCompany },
  news: { file: "../data/news.json", key: "articles", render: renderArticle }
};

async function loadContent() {
  const type = page?.dataset.contentPage;
  const config = configs[type];
  if (!config || !target) return;
  try {
    const response = await fetch(config.file, { cache: "no-store" });
    if (!response.ok) throw new Error("Sisältöä ei voitu ladata");
    const data = await response.json();
    let items = Array.isArray(data[config.key]) ? data[config.key] : [];
    if (type === "events") {
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      items = items
        .filter(item => !item.date || new Date(`${item.date}T23:59:59`) >= today)
        .sort((a, b) => String(a.date).localeCompare(String(b.date)));
    }
    if (!items.length) {
      target.innerHTML = '<p class="empty-state">Uusia nostoja valmistellaan parhaillaan.</p>';
      return;
    }
    target.innerHTML = items.map(config.render).join("");
    const updated = data.updated_at ? new Date(data.updated_at).toLocaleDateString("fi-FI") : "";
    if (statusLine) statusLine.textContent = [data.week, updated && `päivitetty ${updated}`].filter(Boolean).join(" · ");
  } catch (error) {
    target.innerHTML = '<p class="empty-state">Sisällön lataaminen ei juuri nyt onnistunut. Kokeile hetken kuluttua uudelleen.</p>';
  }
}

loadContent();
