// ── SCROLL REVEAL ──
const observer = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) e.target.classList.add('visible');
  });
}, { threshold: 0.12 });

document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

// ── MOBILE NAV ──
const burger = document.querySelector('.nav-burger');
const navLinks = document.querySelector('.nav-links');
if (burger && navLinks) {
  burger.addEventListener('click', () => {
    const open = navLinks.style.display === 'flex';
    navLinks.style.display = open ? 'none' : 'flex';
    navLinks.style.flexDirection = 'column';
    navLinks.style.position = 'absolute';
    navLinks.style.top = '100%';
    navLinks.style.left = '0';
    navLinks.style.right = '0';
    navLinks.style.background = 'rgba(245,242,235,0.98)';
    navLinks.style.padding = '1.5rem';
    navLinks.style.gap = '1rem';
    navLinks.style.borderBottom = '1px solid #d5d0c5';
    if (open) navLinks.style.display = 'none';
  });
}

// ── BLOG PREVIEW LOADER ──
// Loads latest 3 posts from blog/posts.json and renders them on homepage
async function loadBlogPreview() {
  const container = document.getElementById('blog-preview');
  if (!container) return;

  try {
    const res = await fetch('blog/posts.json');
    const posts = await res.json();
    const latest = posts.slice(0, 3);

    container.innerHTML = latest.map((post, i) => `
      <a href="blog/${post.slug}.html" class="blog-card ${i === 0 ? 'featured' : ''} reveal">
        <span class="blog-card-cat">${post.category}</span>
        <h3>${post.title}</h3>
        <p>${post.excerpt}</p>
        <div class="blog-card-meta">
          <span>${post.date}</span>
          <span class="read-more">Lue →</span>
        </div>
      </a>
    `).join('');

    // Re-observe new elements
    container.querySelectorAll('.reveal').forEach(el => observer.observe(el));
  } catch (e) {
    // Fallback static posts if JSON not available
    container.innerHTML = `
      <a href="blog/" class="blog-card featured reveal">
        <span class="blog-card-cat">Frontier Work</span>
        <h3>Ihminen–AI-rajapinnalla: uusi taito, jota kukaan ei opeta</h3>
        <p>Tehokkain taito 2020-luvulla ei ole koodaaminen eikä prompting — se on kyky toimia juuri siinä pisteessä, missä ihminen ja tekoäly kohtaavat.</p>
        <div class="blog-card-meta">
          <span>Maaliskuu 2026</span>
          <span class="read-more">Lue →</span>
        </div>
      </a>
      <a href="blog/" class="blog-card reveal">
        <span class="blog-card-cat">Yrittäjyys</span>
        <h3>Mitä pandemia opetti minulle yrittäjyydestä</h3>
        <p>Menin alas. Nousin uudelleen. Tässä on mitä opin — ja mitä en oppinut mistään kurssista.</p>
        <div class="blog-card-meta">
          <span>Helmikuu 2026</span>
          <span class="read-more">Lue →</span>
        </div>
      </a>
      <a href="blog/" class="blog-card reveal">
        <span class="blog-card-cat">Nuorisoyrittäjyys</span>
        <h3>Miksi nuoret eivät ryhdy yrittäjiksi</h3>
        <p>Kolme vuotta työtä nuorten kanssa paljasti yhden ison syyn. Se ei ole raha.</p>
        <div class="blog-card-meta">
          <span>Tammikuu 2026</span>
          <span class="read-more">Lue →</span>
        </div>
      </a>
    `;
    container.querySelectorAll('.reveal').forEach(el => observer.observe(el));
  }
}

loadBlogPreview();
