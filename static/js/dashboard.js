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

async function loadStatistics() {
    const message = document.getElementById("message");
    message.textContent = "Loading statistics...";

    try {
        const response = await fetch("/api/stats");
        if (!response.ok) {
            throw new Error("Failed to load statistics");
        }
        const stats = await response.json();

        document.getElementById("total").textContent = stats.total;
        document.getElementById("recycling-rate").textContent =
            stats.recycling_rate + "%";
        document.getElementById("accuracy").textContent =
            stats.reviewed === 0 ? "No feedback yet" : stats.accuracy + "%";

        fillTable("categories", Object.entries(stats.by_category));
        fillTable("daily-counts", Object.entries(stats.per_day));
        fillTable("top-items", stats.top_items.map(item => [item.item_name, item.count]));

        message.textContent = stats.total === 0 ? "No data yet" : "";
    } catch (error) {
        message.textContent = "Error loading statistics.";
        console.error(error);
    }
}

loadStatistics();
