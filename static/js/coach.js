async function loadRegions() {
  const response = await fetch("/api/regions");
  const regions = await response.json();

  const select = document.getElementById("region");
  for (const region of regions) {
    const option = document.createElement("option");
    option.value = region;
    option.textContent = region;
    select.appendChild(option);
  }
}

async function loadTip() {
  const region = document.getElementById("region").value;
  const tip = document.getElementById("tip");

  tip.textContent = "Loading tip...";
  const response = await fetch(`/api/tip?region=${encodeURIComponent(region)}`);
  const data = await response.json();

  tip.textContent = response.ok ? data.tip : data.error;
}

async function askCoach() {
  const question = document.getElementById("question").value;
  const region = document.getElementById("region").value;
  const answer = document.getElementById("answer");

  answer.textContent = "Thinking...";

  const response = await fetch("/api/coach", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question: question, region: region }),
  });
  const data = await response.json();

  if (!response.ok) {
    answer.textContent = data.error;
    return;
  }
  answer.textContent = data.answer;
}

document.getElementById("ask-button").addEventListener("click", askCoach);

loadRegions().then(loadTip);
document.getElementById("region").addEventListener("change", loadTip);
