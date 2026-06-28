let item1;
let item2;
let token;
let button1;
let button2;
let busy = false;
async function loadPair() {
  const res = await fetch('/pair');
  const data = await res.json();
  item1 = data['pair'][0];
  item2 = data['pair'][1];
  token = data['token'];
  render();
}
async function vote(winnerId, loserId) {
  if (busy) return;
  busy = true;
  try {
    await fetch('/vote', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({winner_id: winnerId, loser_id: loserId, token})
    });
    await loadPair();
  } finally {
    busy = false;
  }
}
function makeCard(onClick) {
  const card = document.createElement('div');
  card.className = 'card';
  const img = document.createElement('img');
  const label = document.createElement('h2');
  const desc = document.createElement('p');
  card.append(img, label, desc);
  card.addEventListener('click', onClick);
  return {card, img, label, desc};
}
c1 = makeCard(() => vote(item1.id, item2.id));
c2 = makeCard(() => vote(item2.id, item1.id));
const choices = document.getElementById('choices');
choices.append(c1.card);
choices.append(c2.card);
function render() {
  c1.label.textContent = item1.label;
  c1.desc.textContent = item1.descr;
  c1.img.alt = item1.label;

  c2.label.textContent = item2.label;
  c2.desc.textContent = item2.descr;
  c2.img.alt = item2.label;
}
loadPair();