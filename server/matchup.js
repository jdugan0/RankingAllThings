async function matchups() {
  const label = new URLSearchParams(location.search).get('label');
  const res = await fetch(`get_matchups?label=${label}`);
  const data = await res.json();
  if (data == null){
    document.getElementById('matchups').textContent = "Unknown label! How did you get here?"
    return;
  }
  let total = 0;
  const container = document.getElementById('matchups');
  for (const item of data) {
    const row = document.createElement('div');
    row.className = 'leaderboard_card';
    row.style.cursor = 'default';
    row.innerHTML = `<b>${label}</b> won against <b>${item[0]}</b> ${item[1][0]} / ${item[1][1]} times.`;
    container.append(row);
    total += item[1][1];
  }
  document.getElementById("num_votes").textContent = `${label} has ${total} votes`
}
matchups()