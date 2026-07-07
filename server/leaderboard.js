let data;
let selectedCard = null;
let cardContent = null;
async function leaderboard() {
  const res = await fetch('leaderboard_rank');
  data = await res.json();
  const container = document.getElementById('leaderboard');
  let i = 0;
  for (const item of data) {
    const row = document.createElement('div');
    row.className = 'leaderboard_card'
    row.textContent = `${i + 1}. ${item.label} — ${
        Math.round(item.rating)} — won ${item.wins} / ${item.total} matches`;
    row.addEventListener('click', () => selectCard(row, item))
    container.append(row);
    i++;
  }
  const res2 = await fetch('num_votes');
  const p = document.getElementById('num_votes');
  const num = await res2.json();
  p.textContent = `${num} votes have decided — these are the best things`;
}
leaderboard();

function selectCard(card, item) {
  if (selectedCard != null && selectedCard == card) {
    cardContent.remove();
    selectedCard = null;
    return;
  }
  const row = document.createElement('div');
  if (selectedCard != null) {
    cardContent.remove();
  }
  if (item.img) {
    const img = document.createElement('img');
    img.decoding = 'async';
    img.src = item.img;
    row.append(img);
  }

  const text = document.createElement('p');
  text.textContent = `${item.descr}`;
  row.append(text);
  row.className = `leaderboard_card_content`
  card.append(row);
  selectedCard = card;
  cardContent = row;
}

async function reverse() {
  const container = document.getElementById('leaderboard');
  const children = Array.from(container.children);
  children.reverse().forEach(child => container.appendChild(child));
}