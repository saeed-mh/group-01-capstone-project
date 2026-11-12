let categoryChart;
let dailyChart;
let appliedFilters = "";

async function getJson(url, options) {
    const response = await fetch(url, options);
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || "Could not load statistics.");
    }
    return data;
}

function fillTable(id, rows) {
    const tableBody = document.getElementById(id);
    tableBody.innerHTML = "";
    for (const values of rows) {
        const row = document.createElement("tr");
        for (const value of values) {
            const cell = document.createElement("td");
            cell.textContent = value;
            row.appendChild(cell);
        }
        tableBody.appendChild(row);
    }
}

function drawCharts(stats) {
    if (categoryChart) categoryChart.destroy();
    if (dailyChart) dailyChart.destroy();

    const categoryColors = {
        packaging: "#F2C200",
        paper: "#1F5FAD",
        glass: "#2E8B57",
        organic: "#8B5A2B",
        residual: "#6E6E6E",
        hazardous: "#C0392B"
    };

    categoryChart = new Chart(document.getElementById("category-chart"), {
        type: "pie",
        data: {
            labels: Object.keys(stats.by_category),
            datasets: [{
                data: Object.values(stats.by_category),
                backgroundColor: Object.keys(stats.by_category).map(category => categoryColors[category])
            }]
        },
        options: {
            maintainAspectRatio: false,
            plugins: {
                title: { display: true, text: "Share of waste categories" },
                legend: { display: true, position: "bottom" }
            }
        }
    });

    const days = Object.keys(stats.per_day).sort();
    dailyChart = new Chart(document.getElementById("daily-chart"), {
        type: "bar",
        data: {
            labels: days,
            datasets: [{
                label: "Classifications",
                data: days.map(day => stats.per_day[day]),
                backgroundColor: "#2e7d32"
            }]
        },
        options: {
            maintainAspectRatio: false,
            plugins: {
                title: { display: true, text: "Classifications per day" },
                legend: { display: true }
            },
            scales: {
                x: { title: { display: true, text: "Date" } },
                y: {
                    beginAtZero: true,
                    title: { display: true, text: "Number of classifications" },
                    ticks: { precision: 0 }
                }
            }
        }
    });
}

async function loadStatistics() {
    const message = document.getElementById("message");
    const query = new URLSearchParams({
        start: document.getElementById("start").value,
        end: document.getElementById("end").value,
        region: document.getElementById("region").value
    }).toString();
    document.getElementById("apply").disabled = true;
    document.getElementById("export").disabled = true;
    document.getElementById("summarize").disabled = true;
    document.getElementById("summary").textContent = "";
    document.getElementById("summary").hidden = true;
    message.textContent = "Loading statistics...";

    try {
        const stats = await getJson("/api/stats?" + query);
        document.getElementById("total").textContent = stats.total;
        document.getElementById("recycling-rate").textContent = stats.recycling_rate + "%";
        document.getElementById("accuracy").textContent =
            stats.reviewed === 0 ? "No feedback yet" : stats.accuracy + "%";
        drawCharts(stats);
        fillTable("top-items", stats.top_items.map(item => [item.item_name, item.count]));
        fillTable("wrong-results", stats.wrong_results.map(item =>
            [item.item_name, item.category, item.region, item.created_at]));
        appliedFilters = query;
        document.getElementById("export").disabled = false;
        document.getElementById("summarize").disabled = false;
        message.textContent = stats.total === 0 ? "No data yet" : "";
    } catch (error) {
        message.textContent = error.message;
    } finally {
        document.getElementById("apply").disabled = false;
    }
}

document.getElementById("filters").addEventListener("submit", event => {
    event.preventDefault();
    loadStatistics();
});

document.getElementById("export").addEventListener("click", () => {
    window.location.href = "/api/stats/export?" + appliedFilters;
});

document.getElementById("summarize").addEventListener("click", async () => {
    const button = document.getElementById("summarize");
    const summary = document.getElementById("summary");
    const query = appliedFilters;
    button.disabled = true;
    document.getElementById("apply").disabled = true;
    summary.hidden = false;
    summary.textContent = "Generating summary...";
    try {
        const data = await getJson("/api/stats/summary?" + query, { method: "POST" });
        summary.textContent = data.summary;
    } catch (error) {
        summary.textContent = error.message;
    } finally {
        button.disabled = false;
        document.getElementById("apply").disabled = false;
    }
});

async function startDashboard() {
    try {
        const regions = await getJson("/api/regions");
        const select = document.getElementById("region");
        for (const region of regions) {
            const option = document.createElement("option");
            option.value = region;
            option.textContent = region;
            select.appendChild(option);
        }
        await loadStatistics();
    } catch (error) {
        document.getElementById("message").textContent = error.message;
    }
}

startDashboard();
