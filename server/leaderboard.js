async function leaderboard() {
  const res = await fetch('leaderboard_rank');
  const data = await res.json();
  const container = document.getElementById('leaderboard');
  let i = 0;
  for (const item of data) {
    const row = document.createElement('div');
    row.className = 'leaderboard_card'
    row.textContent = `${i + 1}. ${item.label} — ${Math.round(item.rating)}`;
    container.append(row);
    i++;
  }
  const res2 = await fetch('num_votes');
  const p = document.getElementById('num_votes');
  const num = await res2.json();
  p.textContent = `${num} votes have decided — these are the best things`;
}
leaderboard();