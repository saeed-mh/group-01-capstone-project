let adminPassword = "";
const message = document.getElementById("message");
const rulesTable = document.getElementById("rules");

// Send a request with the admin password. Throws an error if the server says no.
async function adminFetch(url, options = {}) {
  options.headers = {
    "Content-Type": "application/json",
    "X-Admin-Password": adminPassword,
  };
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error);
  }
  return data;
}

async function login() {
  adminPassword = document.getElementById("password").value;
  try {
    await adminFetch("/api/admin/login", { method: "POST" });
    document.getElementById("login-section").hidden = true;
    document.getElementById("admin-section").hidden = false;
    message.textContent = "";
    loadRules();
  } catch (error) {
    message.textContent = error.message;
  }
}

async function loadRules() {
  const response = await fetch("/api/rules");
  const rules = await response.json();
  rulesTable.innerHTML = "";

  for (const rule of rules) {
    const row = document.createElement("tr");

    const city = document.createElement("td");
    city.textContent = rule.region;
    row.appendChild(city);

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

    const actions = document.createElement("td");

    const editButton = document.createElement("button");
    editButton.textContent = "Edit";
    editButton.className = "small-button";
    editButton.addEventListener("click", () => editRule(rule));
    actions.appendChild(editButton);

    const deleteButton = document.createElement("button");
    deleteButton.textContent = "Delete";
    deleteButton.className = "small-button danger";
    deleteButton.addEventListener("click", () => deleteRule(rule));
    actions.appendChild(deleteButton);

    row.appendChild(actions);
    rulesTable.appendChild(row);
  }
}

async function deleteRule(rule) {
  if (
    !confirm(`Delete "${rule.bin_name}" (${rule.category}) in ${rule.region}?`)
  ) {
    return;
  }
  try {
    const data = await adminFetch(`/api/rules/${rule.id}`, {
      method: "DELETE",
    });
    message.textContent = data.message;
    loadRules();
  } catch (error) {
    message.textContent = error.message;
  }
}

document.getElementById("login-button").addEventListener("click", login);
document.getElementById("password").addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    login();
  }
});

const form = document.getElementById("rule-form");

function getFormData() {
  return {
    region: document.getElementById("rule-region").value,
    category: document.getElementById("rule-category").value,
    bin_name: document.getElementById("rule-bin-name").value,
    bin_color: document.getElementById("rule-bin-color").value,
    instructions: document.getElementById("rule-instructions").value,
    examples: document.getElementById("rule-examples").value,
  };
}

function resetForm() {
  form.reset();
  document.getElementById("rule-id").value = "";
  document.getElementById("form-title").textContent = "Add a new rule";
}

function editRule(rule) {
  document.getElementById("rule-id").value = rule.id;
  document.getElementById("rule-region").value = rule.region;
  document.getElementById("rule-category").value = rule.category;
  document.getElementById("rule-bin-name").value = rule.bin_name;
  document.getElementById("rule-bin-color").value = rule.bin_color;
  document.getElementById("rule-instructions").value = rule.instructions;
  document.getElementById("rule-examples").value = rule.examples;
  document.getElementById("form-title").textContent = `Edit rule #${rule.id}`;
  form.scrollIntoView({ behavior: "smooth" });
}

async function saveRule(event) {
  event.preventDefault();

  const id = document.getElementById("rule-id").value;
  const url = id ? `/api/rules/${id}` : "/api/rules";
  const method = id ? "PUT" : "POST";

  try {
    const data = await adminFetch(url, {
      method: method,
      body: JSON.stringify(getFormData()),
    });
    message.textContent = data.message;
    resetForm();
    loadRules();
  } catch (error) {
    message.textContent = error.message;
  }
}

form.addEventListener("submit", saveRule);
document.getElementById("cancel-button").addEventListener("click", () => {
  resetForm();
  message.textContent = "";
});
