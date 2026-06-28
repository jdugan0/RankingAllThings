let item1;
let item2;
let token;
let button1;
let button2;
async function loadPair() {
  const res = await fetch("/pair");
  const data = await res.json();
  item1 = data["pair"][0];
  item2 = data["pair"][1];
  token = data["token"];
  render();
}
async function vote(winnerId, loserId) {
  const res = await fetch("/vote", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ winner_id: winnerId, loser_id: loserId, token })
  });
  loadPair();
}
button1 = document.createElement("button");
button2 = document.createElement("button");
button1.addEventListener("click", ()=>vote(item1.id, item2.id));
button2.addEventListener("click", ()=>vote(item2.id, item1.id));
const choices = document.getElementById("choices");
choices.appendChild(button1);
choices.appendChild(button2);
function render(){
    button1.textContent = item1.label;
    button2.textContent = item2.label;
}
loadPair();