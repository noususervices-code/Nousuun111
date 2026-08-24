(function () {
  'use strict';

  const STORAGE_KEY = 'nousuun_nl_modal_v1';
  const DISMISS_DAYS = 30;
  const ENDPOINT = 'https://formsubmit.co/ajax/nousu.services@gmail.com';
  const BLOCKED_PATHS = ['/uutiskirje', '/newsletter', '/kiitos', '/thank-you'];

  const copy = {
    fi: {
      kicker: 'Tähtäimessä nousu?',
      title: 'Oletko aloittava yrittäjä?',
      body: 'Rakennat yritystä tyhjästä — älä tee sitä yksin. Liity Nousu-Jaakon yhteisöön ja saat joka viikko konkreettiset vinkit yrityksen käynnistämiseen, rahoitukseen ja asiakashankintaan.',
      bullets: [
        'Starttiraha- ja rahoitusvinkit selkokielellä',
        'Työkalut ja AI-pohjat, joilla säästät tunteja viikossa',
        'Kutsut Nousuun.fi-tapahtumiin ensimmäisenä'
      ],
      email: 'Sähköpostiosoite',
      placeholder: 'sinun@sahkoposti.fi',
      cta: 'Lähden nousuun →',
      privacy: 'Liittymällä hyväksyt, että Nousuun.fi käsittelee sähköpostiosoitettasi viikkokirjeen lähettämiseksi.',
      privacyLink: 'Lue tietosuojaseloste.',
      note: 'Ei roskapostia. Voit peruuttaa yhdellä klikkauksella.',
      dismiss: 'Ei kiitos, en vielä',
      close: 'Sulje',
      success: 'Hyvä! Liittymispyyntösi on vastaanotettu.',
      error: 'Jotain meni pieleen. Yritä uudelleen tai laita viestiä nousu.services@gmail.com.',
      submitting: 'Liitytään…',
      inlineTitle: 'Saat tärkeimmät seuraavat askeleet sähköpostiisi.',
      inlineBody: 'Yksi käytännöllinen kooste viikossa: rahoitus, tapahtumat ja työkalut aloittavalle yrittäjälle.'
    },
    en: {
      kicker: 'Ready for take-off?',
      title: 'Just starting your business?',
      body: 'Building a business from scratch is hard — do not do it alone. Join the Nousu-Jaakko community for practical weekly tips on launching, funding and finding your first customers.',
      bullets: [
        'Plain-language guidance on start-up grants and funding',
        'Tools and AI templates that save hours every week',
        'Early invitations to Nousuun.fi events'
      ],
      email: 'Email address',
      placeholder: 'you@example.com',
      cta: "Let's take off →",
      privacy: 'By joining, you agree that Nousuun.fi may process your email address to send the weekly newsletter.',
      privacyLink: 'Read the privacy notice.',
      note: 'No spam. Unsubscribe with one click.',
      dismiss: 'No thanks, not yet',
      close: 'Close',
      success: 'Great! Your subscription request has been received.',
      error: 'Something went wrong. Try again or email nousu.services@gmail.com.',
      submitting: 'Joining…',
      inlineTitle: 'Get the most useful next steps in your inbox.',
      inlineBody: 'One practical weekly digest: funding, events and tools for new entrepreneurs.'
    }
  };

  const language = (document.documentElement.lang || 'fi').toLowerCase().startsWith('en') ? 'en' : 'fi';
  const text = copy[language];
  let modal;
  let lastFocused;
  let shown = false;
  let timer;

  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, char => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    })[char]);
  }

  function track(name, details) {
    const payload = Object.assign({ event: name }, details || {});
    if (typeof window.gtag === 'function') window.gtag('event', name, details || {});
    else if (Array.isArray(window.dataLayer)) window.dataLayer.push(payload);
  }

  function readPreference() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return null;
      if (raw === 'subscribed') return { state: 'subscribed' };
      if (raw === 'dismissed') return { state: 'dismissed', timestamp: Date.now() };
      return JSON.parse(raw);
    } catch (_) {
      return null;
    }
  }

  function shouldSuppress() {
    const path = window.location.pathname.toLowerCase();
    if (BLOCKED_PATHS.some(blocked => path.includes(blocked))) return true;
    const preference = readPreference();
    if (!preference) return false;
    if (preference.state === 'subscribed') return true;
    if (preference.state === 'dismissed') {
      const elapsed = Date.now() - Number(preference.timestamp || 0);
      return elapsed < DISMISS_DAYS * 24 * 60 * 60 * 1000;
    }
    return false;
  }

  function remember(state) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ state, timestamp: new Date().toISOString() }));
    } catch (_) {
      // The form remains usable when storage is unavailable.
    }
  }

  function formMarkup(source) {
    const id = `newsletter-email-${source}`;
    return `
      <form class="nl-signup-form" data-newsletter-form data-source="${source}" novalidate>
        <label class="nl-label" for="${id}">${escapeHtml(text.email)}</label>
        <div class="nl-field-row">
          <input id="${id}" class="nl-email" name="email" type="email" inputmode="email" autocomplete="email" placeholder="${escapeHtml(text.placeholder)}" required />
          <button class="btn btn-primary nl-submit" type="submit">
            <span class="nl-submit-label">${escapeHtml(text.cta)}</span>
            <span class="nl-spinner" aria-hidden="true"></span>
          </button>
        </div>
        <input class="nl-honeypot" type="text" name="_honey" tabindex="-1" autocomplete="off" aria-hidden="true" />
        <p class="nl-consent">${escapeHtml(text.privacy)} <a href="/tietosuoja/">${escapeHtml(text.privacyLink)}</a></p>
        <p class="nl-note">${escapeHtml(text.note)}</p>
        <p class="nl-status" role="status" aria-live="polite"></p>
      </form>`;
  }

  function inlineMarkup() {
    return `
      <div class="nl-inline-copy">
        <p class="eyebrow">${escapeHtml(text.kicker)}</p>
        <h2>${escapeHtml(text.inlineTitle)}</h2>
        <p>${escapeHtml(text.inlineBody)}</p>
      </div>
      <div class="nl-inline-form">${formMarkup('inline')}</div>`;
  }

  function modalMarkup() {
    return `
      <div class="nl-modal-backdrop" data-newsletter-backdrop>
        <section class="nl-modal" role="dialog" aria-modal="true" aria-labelledby="newsletter-modal-title" tabindex="-1">
          <button class="nl-modal-close" type="button" aria-label="${escapeHtml(text.close)}" data-newsletter-close>×</button>
          <div class="nl-modal-grid">
            <div class="nl-modal-art" aria-hidden="true">
              <svg viewBox="0 0 360 440" role="img">
                <path class="nl-route" d="M42 362 C90 350 110 303 158 285 S230 202 315 105" />
                <path class="nl-route-arrow" d="M285 109 L319 101 L314 136" />
                <g class="nl-checkpoint" transform="translate(66 315)"><circle r="29"/><path d="M-12 1l9 9 17-22"/></g>
                <g class="nl-checkpoint" transform="translate(166 252)"><circle r="29"/><path d="M-12 1l9 9 17-22"/></g>
                <g class="nl-checkpoint" transform="translate(273 150)"><circle r="29"/><path d="M-12 1l9 9 17-22"/></g>
                <path class="nl-runway" d="M32 392h286M62 410h226" />
              </svg>
            </div>
            <div class="nl-modal-content">
              <p class="eyebrow">${escapeHtml(text.kicker)}</p>
              <h2 id="newsletter-modal-title">${escapeHtml(text.title)}</h2>
              <p class="nl-modal-body">${escapeHtml(text.body)}</p>
              <ul class="nl-benefits">${text.bullets.map(item => `<li><span aria-hidden="true">↗</span>${escapeHtml(item)}</li>`).join('')}</ul>
              ${formMarkup('modal')}
              <button class="nl-dismiss-link" type="button" data-newsletter-close>${escapeHtml(text.dismiss)}</button>
            </div>
          </div>
        </section>
      </div>`;
  }

  async function submitNewsletter(form) {
    const input = form.querySelector('input[type="email"]');
    const status = form.querySelector('.nl-status');
    const button = form.querySelector('.nl-submit');
    const label = form.querySelector('.nl-submit-label');
    const source = form.dataset.source || 'unknown';

    if (!input.checkValidity()) {
      input.reportValidity();
      return;
    }

    button.disabled = true;
    form.classList.add('is-loading');
    status.textContent = '';
    label.textContent = text.submitting;
    track('newsletter_submit', { source });

    try {
      const response = await fetch(ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({
          email: input.value.trim(),
          consent: true,
          consent_timestamp: new Date().toISOString(),
          source,
          page: window.location.href,
          _subject: `Nousuun.fi uutiskirjetilaus (${source})`,
          _template: 'table',
          _captcha: 'false'
        })
      });
      if (!response.ok) throw new Error('Newsletter request failed');

      remember('subscribed');
      form.classList.remove('is-loading');
      form.classList.add('is-success');
      form.innerHTML = `<p class="nl-success" role="status">${escapeHtml(text.success)}</p>`;
      track('newsletter_success', { source });
      if (source === 'modal') window.setTimeout(closeModal, 2400);
    } catch (_) {
      form.classList.remove('is-loading');
      button.disabled = false;
      label.textContent = text.cta;
      status.textContent = text.error;
      status.classList.add('is-error');
    }
  }

  function bindForm(form) {
    form.addEventListener('submit', event => {
      event.preventDefault();
      submitNewsletter(form);
    });
  }

  function focusableElements() {
    if (!modal) return [];
    return Array.from(modal.querySelectorAll('button:not([disabled]), input:not([disabled]), a[href]'));
  }

  function handleModalKeydown(event) {
    if (event.key === 'Escape') {
      closeModal(true);
      return;
    }
    if (event.key !== 'Tab') return;
    const items = focusableElements();
    if (!items.length) return;
    const first = items[0];
    const last = items[items.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  }

  function closeModal(dismissed) {
    if (!modal) return;
    if (dismissed) {
      remember('dismissed');
      track('newsletter_modal_dismissed');
    }
    modal.classList.remove('is-visible');
    document.removeEventListener('keydown', handleModalKeydown);
    document.body.classList.remove('nl-modal-open');
    window.setTimeout(() => {
      if (modal) modal.remove();
      modal = null;
      if (lastFocused && typeof lastFocused.focus === 'function') lastFocused.focus();
    }, 220);
  }

  function showModal(trigger) {
    if (shown || shouldSuppress()) return;
    shown = true;
    window.clearTimeout(timer);
    lastFocused = document.activeElement;
    const host = document.createElement('div');
    host.id = 'newsletter-modal-root';
    host.innerHTML = modalMarkup();
    document.body.appendChild(host);
    modal = host;
    bindForm(modal.querySelector('[data-newsletter-form]'));
    modal.querySelectorAll('[data-newsletter-close]').forEach(button => button.addEventListener('click', () => closeModal(true)));
    modal.querySelector('[data-newsletter-backdrop]').addEventListener('mousedown', event => {
      if (event.target === event.currentTarget) closeModal(true);
    });
    document.addEventListener('keydown', handleModalKeydown);
    document.body.classList.add('nl-modal-open');
    requestAnimationFrame(() => {
      modal.classList.add('is-visible');
      modal.querySelector('.nl-modal').focus();
    });
    track('newsletter_modal_shown', { trigger });
  }

  function installTriggers() {
    if (shouldSuppress()) return;
    timer = window.setTimeout(() => showModal('time_25s'), 25000);

    const onScroll = () => {
      const scrollable = document.documentElement.scrollHeight - window.innerHeight;
      if (scrollable > 0 && window.scrollY / scrollable >= 0.5) {
        window.removeEventListener('scroll', onScroll);
        showModal('scroll_50');
      }
    };
    window.addEventListener('scroll', onScroll, { passive: true });

    if (window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
      const onExitIntent = event => {
        if (event.clientY <= 0 && !event.relatedTarget) {
          document.removeEventListener('mouseout', onExitIntent);
          showModal('exit_intent');
        }
      };
      document.addEventListener('mouseout', onExitIntent);
    }
  }

  function init() {
    document.querySelectorAll('[data-newsletter-inline]').forEach(host => {
      host.classList.add('nl-inline');
      host.innerHTML = inlineMarkup();
      bindForm(host.querySelector('[data-newsletter-form]'));
    });
    installTriggers();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
