let selectedCard = null;
async function matchups() {
  const label = new URLSearchParams(location.search).get('label');
  const res = await fetch(`get_matchups?label=${label}`);
  const data = await res.json();
  if (data == null) {
    document.getElementById('matchups').textContent =
        'Unknown label! How did you get here?'
    return;
  }
  let total = 0;
  const container = document.getElementById('matchups');
  for (const item of data) {
    const row = document.createElement('div');
    row.className = 'leaderboard_card';
    row.innerHTML = `${label} won against <b>${item[0]}</b> ${
        item[1][0]} / ${item[1][1]} times.`;
    total += item[1][1];


    const content = document.createElement('div');
    content.className = `leaderboard_card_content`
    const inner = document.createElement('div');
    inner.className = 'inner';
    if (item[1][2]) {
      const img = document.createElement('img');
      img.decoding = 'async';
      img.loading = 'lazy';
      img.src = item[1][2];
      inner.append(img);
    }

    const text = document.createElement('p');
    text.textContent = `${item[1][3]}`;
    inner.append(text);
    row.append(content);
    row.addEventListener('click', () => selectCard(content))
    content.append(inner);

    container.append(row);
  }
  document.getElementById('num_votes').textContent =
      `${label} has ${total} votes`
}
function selectCard(content) {
  if (selectedCard && selectedCard != content) {
    selectedCard.classList.remove('open');
  }
  content.classList.toggle('open');
  selectedCard = content.classList.contains('open') ? content : null;
}
matchups()