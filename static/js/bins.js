const regionSelect = document.getElementById("region");

const rulesTable = document.getElementById("rules");
const message = document.getElementById("message");

function showRules(rules) {
  rulesTable.innerHTML = "";

  for (const rule of rules) {
    const row = document.createElement("tr");

    const bin = document.createElement("td");
    bin.textContent = rule.bin_name;
    bin.style.background = rule.bin_color;
    bin.style.color = "white";
    row.appendChild(bin);

    for (const value of [rule.category, rule.instructions, rule.examples]) {
      const cell = document.createElement("td");
      cell.textContent = value;
      row.appendChild(cell);
    }

    rulesTable.appendChild(row);
  }
}

async function loadRules(region) {
  const response = await fetch(
    `/api/bins?region=${encodeURIComponent(region)}`,
  );
  const data = await response.json();

  if (!response.ok) {
    rulesTable.innerHTML = "";
    message.textContent = data.error;
    return;
  }
  message.textContent = "";
  showRules(data);
}

const searchInput = document.getElementById("search");

async function searchRules() {
  const text = searchInput.value.trim();
  const region = regionSelect.value;

  const response = await fetch(
    `/api/search?q=${encodeURIComponent(text)}&region=${encodeURIComponent(region)}`,
  );
  const data = await response.json();

  if (!response.ok) {
    message.textContent = data.error;
    return;
  }
  showRules(data);
  message.textContent = data.length === 0 ? `No bin found for "${text}".` : "";
}

regionSelect.addEventListener("change", () => {
  if (searchInput.value.trim()) {
    searchRules();
  } else {
    loadRules(regionSelect.value);
  }
});

document.getElementById("search-button").addEventListener("click", searchRules);

searchInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    searchRules();
  }
});

document.getElementById("clear-button").addEventListener("click", () => {
  searchInput.value = "";
  loadRules(regionSelect.value);
});

async function loadRegions() {
  const response = await fetch("/api/regions");
  const regions = await response.json();

  for (const region of regions) {
    const option = document.createElement("option");
    option.value = region;
    option.textContent = region;
    regionSelect.appendChild(option);
  }

  loadRules(regionSelect.value);
}

loadRegions();
