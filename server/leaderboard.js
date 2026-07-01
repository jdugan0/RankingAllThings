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
  console.log("meow")
}
leaderboard();