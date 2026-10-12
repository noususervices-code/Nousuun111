(() => {
  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const link = value => /^https?:\/\//i.test(String(value)) ? esc(value) : '#';
  const date = value => new Date(`${value}T12:00:00`).toLocaleDateString('fi-FI', {day:'numeric',month:'long'});
  async function load(file, id, render, empty) {
    const target = document.getElementById(id);
    try {
      const response = await fetch(`/data/${file}.json`, {cache:'no-store'});
      if (!response.ok) throw new Error('fetch');
      const data = await response.json();
      target.innerHTML = render(data) || `<p class="empty-state">${empty}</p>`;
      target.dataset.state = 'loaded';
    } catch (_) {
      target.innerHTML = '<p class="empty-state">Sisällön lataaminen ei juuri nyt onnistunut. Kokeile hetken kuluttua uudelleen.</p>';
      target.dataset.state = 'error';
    }
  }
  load('events', 'events-container', data => {
    const status = document.getElementById('events-updated');
    if (data.updated_at) status.textContent = `Aineisto päivitetty ${new Date(data.updated_at).toLocaleDateString('fi-FI', {timeZone:'Europe/Helsinki'})}. Varmista vapaat paikat järjestäjän sivulta.`;
    return (data.events || []).filter(NousuunScope.upcoming).sort((a,b) => a.date.localeCompare(b.date)).slice(0,6).map(item => `
      <article class="event-card"><div class="event-card-top"><span class="event-badge">${esc(item.tags?.[0] || 'Tapahtuma')}</span><span class="event-date">${date(item.date)}${item.end_date ? '–' + date(item.end_date) : ''}</span></div>
      <h3 class="event-title">${esc(item.name)}</h3><p class="event-location">${esc([item.time,item.location].filter(Boolean).join(' · '))}</p><p class="event-desc">${esc(item.description)}</p><p class="event-access">${esc([item.access,item.price].filter(Boolean).join(' · '))}</p><a class="btn btn-sm btn-outline event-link" href="${link(item.url)}" target="_blank" rel="noopener">Avaa tapahtumasivu →</a></article>`).join('');
  }, 'Listalla ei ole tällä hetkellä tulevia tapahtumia.');
  load('companies', 'companies-container', data => (data.companies || []).filter(NousuunScope.company).slice(0,3).map(item => `
    <a class="list-item" href="${link(item.url)}" target="_blank" rel="noopener"><h3>${esc(item.name)}</h3><p>${esc(item.insight)}</p><span class="list-meta">${esc([item.creative_sector,item.location,item.source].filter(Boolean).join(' · '))}</span></a>`).join(''), 'Tällä hetkellä ei ole varmennettuja luovien alojen yritysostokohteita.');
})();
