let data;
let selectedCard = null;
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
    if (item.sfw == 0){
      row.style.color = "red";
    }
    // create card content:

    const content = document.createElement('div');
    content.className = `leaderboard_card_content`
    const inner = document.createElement('div');
    inner.className = 'inner';
    if (item.img) {
      const img = document.createElement('img');
      img.decoding = 'async';
      img.loading = 'lazy';
      img.src = item.img;
      inner.append(img);
    }

    const text = document.createElement('p');
    text.textContent = `${item.descr}`;
    inner.append(text);
    row.append(content);
    row.addEventListener('click', () => selectCard(content))
    content.append(inner);

    container.append(row);
    i++;
  }
  const res2 = await fetch('num_votes');
  const p = document.getElementById('num_votes');
  const num = await res2.json();
  p.textContent = `${num} votes have decided — these are the best things`;
}
leaderboard();

function selectCard(content) {
  if (selectedCard && selectedCard != content) {
    selectedCard.classList.remove('open');
  }
  content.classList.toggle('open');
  selectedCard = content.classList.contains('open') ? content : null;
}

async function reverse() {
  const container = document.getElementById('leaderboard');
  const children = Array.from(container.children);
  children.reverse().forEach(child => container.appendChild(child));
}