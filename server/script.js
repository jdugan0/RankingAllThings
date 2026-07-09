let item1;
let item2;
let pair_token;
let nextPair = null;
let busy = false;
let ts_token;

function imgUrl(item) {
  if (!item.img) return null;
  return item.img.replace(/^http:\/\//, 'https://') + '?width=300';
}

function preload(data) {
  for (const item of data.pair) {
    const u = imgUrl(item);
    if (u) {
      const im = new Image();
      im.src = u;
    }
  }
  return data;
}

async function fetchPair() {
  const res = await fetch('pair');
  return preload(await res.json());
}

function setPair(data) {
  item1 = data['pair'][0];
  item2 = data['pair'][1];
  pair_token = data['token'];
  render();
}

async function onTurnstileSuccess(token) {
  const res = await fetch('validate', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({turnstile: token})
  });
  const data = await res.json();
  ts_token = data.token;
  sessionStorage.setItem('ts', ts_token);
  if (ts_token) {
    document.getElementById("turnstile-container").style.display = "none";
    init();
  }
}
async function vote(winnerId, loserId) {
  if (busy) return;
  busy = true;
  try {
    const res = await fetch('vote', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        winner_id: winnerId,
        loser_id: loserId,
        token: pair_token,
        turnstile: ts_token
      })
    });
    if (res.status == 403) {
      choices.style.display = 'none';
      pair_token = null;
      ts_token = null;
      item1 = null;
      item2 = null;
      busy = false;
      nextPair = null;
      sessionStorage.removeItem('ts');
      document.getElementById("turnstile-container").style.display = "block";
      turnstile.render("#turnstile-container");
      turnstile.reset();
      return;
    }
    setPair(nextPair || await fetchPair());
    nextPair = await fetchPair();
  } finally {
    busy = false;
  }
}

function makeCard(onClick) {
  const card = document.createElement('div');
  card.className = 'card';
  const img = document.createElement('img');
  img.decoding = 'async';
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
choices.style.display = 'none';
function render() {
  c1.label.textContent = item1.label;
  c1.desc.textContent = item1.descr;
  c1.img.alt = item1.label;
  const u1 = imgUrl(item1);
  if (u1) {
    c1.img.src = u1;
    c1.img.style.display = 'block';
  } else {
    c1.img.removeAttribute('src');
    c1.img.style.display = 'none';
  }


  c2.label.textContent = item2.label;
  c2.desc.textContent = item2.descr;
  c2.img.alt = item2.label;
  const u2 = imgUrl(item2);
  if (u2) {
    c2.img.src = u2;
    c2.img.style.display = 'block';
  }

  else {
    c2.img.removeAttribute('src');
    c2.img.style.display = 'none';
  }
}

async function init() {
  choices.style.display = 'flex';
  setPair(await fetchPair());
  nextPair = await fetchPair();
}



// init process:
const stored = sessionStorage.getItem('ts');
ts_token = stored;
if (stored){
  init();
}
else{
  turnstile.render("#turnstile-container");
}