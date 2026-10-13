/* Optional, browser-local event preferences. No account or server submission. */
window.NousuunInterests = (() => {
  'use strict';
  const KEY = 'nousuun_interests_v1';
  const topics = [
    {id:'starting', label:'Yrittäjyyden aloittaminen', pattern:/yrittäjyyttä harkitse|yrityksen perust|aloittav|liikeidea|idean validointi|testata ideaa/i},
    {id:'growth', label:'Startupit ja yrityksen kasvu', pattern:/startup|kasvu|kasva|growth|skaalau/i},
    {id:'ai', label:'AI ja uudet teknologiat', pattern:/\bai\b|tekoäly|automaatio|uudet teknologiat|koneoppimi|robotii/i},
    {id:'sales', label:'Myynti ja markkinointi', pattern:/myynti|myynn|markkinoin|asiakashank|bränd|tuotteist/i},
    {id:'funding', label:'Rahoitus ja yrittäjän talous', pattern:/rahoit|starttiraha|yrittäjän talous|kannattavu|hinnoittel|cap table|sijoittaj/i},
    {id:'creative', label:'Luovat alat', pattern:/luov|kuvataide|musiik|muotoil|design|kirjallis|kustantami|kuvitu|elokuva|peliala|muoti/i},
    {id:'wellbeing', label:'Hyvinvointiala', pattern:/hyvinvoin|palautumi|työkyky|liikunta|yhteislenkki|jooga|pilates|mielen terveys|mielenterveys|naisten tervey/i},
    {id:'networking', label:'Verkostoituminen ja yhteisöllisyys', pattern:/verkosto|yhteisö|yhteislenkki|tutustumaan toisiinsa|tavataan muita|networking/i},
    {id:'team', label:'Tiimin tai co-founderin löytäminen', pattern:/co[ -]?founder|tiimin rakent|löytää tiimin|tiimikaver|perustajakumppan/i}
  ];
  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const normalize = value => Array.isArray(value)
    ? [...new Set(value.filter(id => topics.some(topic => topic.id === id)))].slice(0,3) : [];
  let selected = [];
  let persistent = true;
  try { selected = normalize(JSON.parse(window.localStorage.getItem(KEY) || '[]')); }
  catch (_) { persistent = false; }
  const matches = (event, preferences = selected) => {
    const text = [event.name, event.description, ...(event.tags || [])].join(' ');
    return topics.filter(topic => normalize(preferences).includes(topic.id) && topic.pattern.test(text));
  };
  const rank = (events, preferences = selected) => events.map(event => ({event, matches:matches(event, preferences)}))
    .sort((a,b) => Number(b.matches.length > 0) - Number(a.matches.length > 0)
      || String(a.event.date).localeCompare(String(b.event.date))
      || String(a.event.name).localeCompare(String(b.event.name), 'fi'));
  function setSelected(value) {
    selected = normalize(value);
    try {
      if (selected.length) window.localStorage.setItem(KEY, JSON.stringify(selected));
      else window.localStorage.removeItem(KEY);
      persistent = true;
    } catch (_) { persistent = false; }
    if (typeof document !== 'undefined') {
      updatePickers();
      window.dispatchEvent(new CustomEvent('nousuun:interests-change'));
    }
    return selected.slice();
  }
  function updatePickers() {
    document.querySelectorAll('[data-interest-picker]').forEach(picker => {
      picker.querySelectorAll('input').forEach(input => {
        input.checked = selected.includes(input.value);
        input.disabled = selected.length === 3 && !input.checked;
      });
      picker.querySelector('[data-interest-count]').textContent = `${selected.length}/3 valittu.${selected.length === 3 ? ' Vaihda aihetta poistamalla ensin yksi valinta.' : ' Voit valita myös yhden tai kaksi aihetta.'}`;
      picker.querySelector('[data-interest-storage]').textContent = persistent
        ? 'Valinnat muistetaan vain tässä selaimessa. Voit vaihtaa tai tyhjentää ne milloin tahansa.'
        : 'Selain ei salli valintojen tallentamista. Ne toimivat tämän sivun ajan.';
      picker.querySelector('button').disabled = selected.length === 0;
    });
  }
  function mount() {
    document.querySelectorAll('[data-interest-picker]').forEach((picker,index) => {
      const help = `interest-help-${index}`;
      picker.innerHTML = `<fieldset class="interest-picker"><legend>Mikä sinua kiinnostaa?</legend><p id="${help}">Valitse enintään kolme. Näet kaikki tapahtumat myös ilman valintoja.</p><div class="interest-options">${topics.map(topic => `<label class="interest-option"><input type="checkbox" value="${topic.id}" aria-describedby="${help}"><span>${esc(topic.label)}</span></label>`).join('')}</div><div class="interest-controls"><p data-interest-count aria-live="polite" role="status"></p><button class="interest-clear" type="button">Tyhjennä valinnat</button></div><p class="interest-storage" data-interest-storage></p></fieldset>`;
      picker.addEventListener('change', event => {
        if (event.target.matches('input[type=checkbox]')) {
          setSelected([...picker.querySelectorAll('input:checked')].map(input => input.value));
        }
      });
      picker.querySelector('button').addEventListener('click', () => setSelected([]));
    });
    updatePickers();
  }
  function render(events, card, gridClass) {
    const ranked = rank(events);
    if (!ranked.length) return '<p class="empty-state">Listalla ei ole tällä hetkellä tulevia tapahtumia.</p>';
    const cards = entries => entries.map(({event,matches:reasons}) => card(event, reasons.length
      ? `<p class="interest-reason">Sopii kiinnostukseesi: ${esc(reasons.map(reason => reason.label).join(' · '))}</p>` : '')).join('');
    if (!selected.length) return cards(ranked);
    const matching = ranked.filter(item => item.matches.length);
    const others = ranked.filter(item => !item.matches.length);
    return `<div class="interest-groups"><section aria-label="Sinulle sopivat tapahtumat"><h3 class="interest-group-title">Sinulle sopivat tapahtumat</h3><p class="interest-result" role="status">${matching.length ? `${matching.length} tapahtumaa sopii vähintään yhteen valitsemaasi kiinnostukseen.` : 'Valintoihisi sopivia tulevia tapahtumia ei juuri nyt ole. Voit vaihtaa kiinnostuksiasi tai tutustua muihin tapahtumiin alla.'}</p>${matching.length ? `<div class="${gridClass}">${cards(matching)}</div>` : ''}</section>${others.length ? `<section aria-label="Muut tulevat tapahtumat"><h3 class="interest-group-title">Muut tulevat tapahtumat</h3><div class="${gridClass}">${cards(others)}</div></section>` : ''}</div>`;
  }
  if (typeof document !== 'undefined') mount();
  return {topics, normalize, matches, rank, render, setSelected, getSelected:() => selected.slice()};
})();
