// Load and display the Statistics Dashboard; calculations come from Python.
let categoryChart;
let dailyChart;
let appliedFilters = "";  // Remember filters from the last successful load for CSV and summary requests.

async function getJson(url, options) {  // Fetch JSON; return a Promise that resolves to the parsed data.
    const response = await fetch(url, options);  // await waits for the response without blocking the whole page.
    const data = await response.json();
    if (!response.ok) {  // HTTP errors such as 400 or 500 must be handled explicitly.
        throw new Error(data.error || "Could not load statistics.");
    }
    return data;
}

function fillTable(id, rows) {  // Fill an HTML table from row arrays; returns undefined.
    const tableBody = document.getElementById(id);
    tableBody.innerHTML = "";
    for (const values of rows) {
        const row = document.createElement("tr");
        for (const value of values) {
            const cell = document.createElement("td");
            cell.textContent = value;  // Insert plain text rather than interpreting values as HTML.
            row.appendChild(cell);
        }
        tableBody.appendChild(row);
    }
}

function drawCharts(stats) {  // Draw both charts from Python results; returns undefined.
    if (categoryChart) categoryChart.destroy();  // Remove old charts before reusing their canvases.
    if (dailyChart) dailyChart.destroy();

    const categoryColors = {  // Keep each category colour fixed even when filters change the order.
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
            labels: Object.keys(stats.by_category),  // Object.keys returns the category names.
            datasets: [{
                data: Object.values(stats.by_category),  // Object.values returns the matching counts.
                backgroundColor: Object.keys(stats.by_category).map(category => categoryColors[category])  // map returns one colour for each category name.
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

    const days = Object.keys(stats.per_day).sort();  // Sort YYYY-MM-DD strings into chronological order.
    dailyChart = new Chart(document.getElementById("daily-chart"), {
        type: "bar",
        data: {
            labels: days,
            datasets: [{
                label: "Classifications",
                data: days.map(day => stats.per_day[day]),  // map returns the count for each displayed day.
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

async function loadStatistics() {  // Load filters and update the page; returned Promise resolves to undefined.
    const message = document.getElementById("message");
    const query = new URLSearchParams({  // Encode the form values into a URL query string.
        start: document.getElementById("start").value,
        end: document.getElementById("end").value,
        region: document.getElementById("region").value
    }).toString();
    document.getElementById("apply").disabled = true;  // Disable controls while loading to avoid overlapping requests.
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
            stats.reviewed === 0 ? "No feedback yet" : stats.accuracy + "%";  // Show no feedback instead of presenting zero as measured accuracy.
        drawCharts(stats);
        fillTable("top-items", stats.top_items.map(item => [item.item_name, item.count]));  // Convert each top-item object into a two-cell row array.
        fillTable("wrong-results", stats.wrong_results.map(item =>  // Convert each wrong result into an item/category/city/date row.
            [item.item_name, item.category, item.region, item.created_at]));
        appliedFilters = query;  // Keep the filters that produced the numbers now on screen.
        document.getElementById("export").disabled = false;
        document.getElementById("summarize").disabled = false;
        message.textContent = stats.total === 0 ? "No data yet" : "";
    } catch (error) {
        message.textContent = error.message;
    } finally {  // finally runs after success or failure; unlock the form.
        document.getElementById("apply").disabled = false;
    }
}

document.getElementById("filters").addEventListener("submit", event => {  // Submit handler: reload selected statistics; returns undefined.
    event.preventDefault();  // Prevent the browser from submitting and reloading the whole page.
    loadStatistics();
});

document.getElementById("export").addEventListener("click", () => {  // Click handler: start the CSV download; returns undefined.
    window.location.href = "/api/stats/export?" + appliedFilters;  // Use the applied selection, not unsubmitted form edits.
});

document.getElementById("summarize").addEventListener("click", async () => {  // Async click handler: request a summary; Promise resolves to undefined.
    const button = document.getElementById("summarize");
    const summary = document.getElementById("summary");
    const query = appliedFilters;  // Summarise the same selection currently displayed.
    button.disabled = true;
    document.getElementById("apply").disabled = true;
    summary.hidden = false;
    summary.textContent = "Generating summary...";
    try {
        const data = await getJson("/api/stats/summary?" + query, { method: "POST" });  // POST starts the summary request; await the parsed JSON.
        summary.textContent = data.summary;
    } catch (error) {
        summary.textContent = error.message;
    } finally {  // Always re-enable controls, including after an API error.
        button.disabled = false;
        document.getElementById("apply").disabled = false;
    }
});

async function startDashboard() {  // Load city options and initial statistics; Promise resolves to undefined.
    try {
        const regions = await getJson("/api/regions");  // The shared rules API provides the available cities.
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

startDashboard();  // Run startup once after this script loads.
