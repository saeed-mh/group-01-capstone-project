const regionSelect = document.getElementById("region");

const rulesTable = document.getElementById("rules");
const message = document.getElementById("message");

async function loadRules(region) {
  const response = await fetch(
    `/api/bins?region=${encodeURIComponent(region)}`,
  );
  const rules = await response.json();

  rulesTable.innerHTML = "";
  message.textContent =
    rules.length === 0 ? `No rules found for ${region}.` : "";

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

regionSelect.addEventListener("change", () => loadRules(regionSelect.value));

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
