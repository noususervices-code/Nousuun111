/* Shared publication boundary for the homepage and archive pages. */
window.NousuunScope = (() => {
  const excluded = /kaune|kosmet|beauty|cosmet|esteti|esteetti|aesthetic|plastic.surg|plastiikkakirurg|botox|botuliini|täyteaine|tayteaine|filler|parturi|kampaamo|hiushoit|kynsihoit|ripsihoit/i;
  const searchable = item => [item.name, item.description, item.industry, item.insight, item.creative_sector, ...(item.tags || [])].join(' ');
  const allowed = item => !excluded.test(searchable(item));
  const company = item => allowed(item) && item.creative_sector_verified === true && Boolean(item.creative_sector);
  const upcoming = item => {
    const today = new Date().toLocaleDateString('sv-SE', { timeZone: 'Europe/Helsinki' });
    return allowed(item) && item.date && (item.end_date || item.date) >= today && (!item.registration_deadline || item.registration_deadline >= today);
  };
  return { allowed, company, upcoming };
})();
