const {test} = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');
const code = fs.readFileSync(path.join(__dirname,'../js/interests.js'),'utf8');
function boot(saved = '[]', blocked = false) {
  const storage = new Map([['nousuun_interests_v1',saved]]);
  const context = {window:{localStorage:{
    getItem:key => { if (blocked) throw Error('blocked'); return storage.get(key); },
    setItem:(key,value) => { if (blocked) throw Error('blocked'); storage.set(key,value); },
    removeItem:key => { if (blocked) throw Error('blocked'); storage.delete(key); }
  }}};
  vm.createContext(context);
  vm.runInContext(code,context);
  return {api:context.window.NousuunInterests,storage};
}
const plain = value => JSON.parse(JSON.stringify(value));
test('restored preferences ignore unknown IDs, duplicates and selections beyond three', () => {
  const {api} = boot('["ai","ai","unknown","creative","team","sales"]');
  assert.deepEqual(plain(api.getSelected()),['ai','creative','team']);
});
test('changes persist and clear removes the stored preference', () => {
  const {api,storage} = boot();
  api.setSelected(['wellbeing']);
  assert.equal(storage.get('nousuun_interests_v1'),'["wellbeing"]');
  api.setSelected([]);
  assert.equal(storage.has('nousuun_interests_v1'),false);
});
test('malformed and blocked storage leave usable in-memory preferences', () => {
  assert.equal(boot('{bad').api.getSelected().length,0);
  const {api} = boot('[]',true);
  assert.doesNotThrow(() => api.setSelected(['ai']));
  assert.deepEqual(plain(api.getSelected()),['ai']);
});
test('matching ranks first, dates stay chronological within both groups and all events remain', () => {
  const {api} = boot();
  const events = [
    {name:'Other early',date:'2026-10-14',tags:[]},
    {name:'AI late',date:'2026-10-22',tags:['AI']},
    {name:'AI early',date:'2026-10-20',tags:['AI']},
    {name:'Other late',date:'2026-10-25',tags:[]}
  ];
  assert.deepEqual(plain(api.rank(events,['ai']).map(row=>row.event.name)),['AI early','AI late','Other early','Other late']);
  assert.deepEqual(plain(api.rank(events,[]).map(row=>row.event.name)),['Other early','AI early','AI late','Other late']);
});
test('no match is honest and keeps every other event visible', () => {
  const {api} = boot();
  api.setSelected(['team']);
  const html = api.render([{name:'Taideilta',date:'2026-10-14',tags:['kuvataide']}],item=>item.name,'events-grid');
  assert.match(html,/sopivia tulevia tapahtumia ei juuri nyt ole/);
  assert.match(html,/Taideilta/);
  assert.doesNotMatch(html,/Sopii kiinnostukseesi:/);
});
test('generic founders and venue technology do not imply co-founder or AI matches', () => {
  const {api} = boot();
  assert.equal(api.matches({name:'Founders Running Club',tags:['founderit'],location:'Tekniikan museo'},['team','ai']).length,0);
  assert.equal(api.matches({name:'Chair painting',description:'Paint a chair'},['ai']).length,0);
});
test('curated event descriptions give grounded creative, wellbeing, AI and team recommendations', () => {
  const {api} = boot();
  assert.ok(api.matches({name:'Still Life',tags:['kuvataide']},['creative']).length);
  assert.equal(api.matches({name:'Founders Running Club',tags:['hyvinvointi','verkostoituminen']},['wellbeing','networking']).length,2);
  assert.equal(api.matches({name:'100STARTUPS',description:'Yrittäjyyttä harkitseville, jotka haluavat testata ideaa ja löytää tiimin.'},['starting','team']).length,2);
  assert.ok(api.matches({name:'Charlie',description:'Ohjelmassa käsitellään tekoälyn käyttöä.'},['ai']).length);
});
