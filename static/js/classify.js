
async function loadClassifications() {
    const tableBody = document.getElementById("classifications");
    const message = document.getElementById("message");

    message.textContent = "Loading classifications...";

    try {
        const response = await fetch("/api/classifications");

        if (!response.ok) {
            throw new Error("Failed to load classifications");
        }

        const records = await response.json();

        tableBody.innerHTML = "";

        if (records.length === 0) {
            message.textContent = "No classifications found.";
            return;
        }

        for (const record of records) {
            const row = document.createElement("tr");

            const values = [
                record.id,
                record.item_name,
                record.category,
                record.region,
                record.bin_name,
                record.explanation,
                record.input_type,
                record.is_correct === null
                    ? "Not checked"
                    : record.is_correct ? "Yes" : "No",
                record.created_at
            ];

            for (const value of values) {
                const cell = document.createElement("td");
                cell.textContent = value ?? "";
                row.appendChild(cell);
            }

            tableBody.appendChild(row);
        }

        message.textContent = "";

    } catch (error) {
        message.textContent = "Error loading classifications.";
        console.error(error);
    }
}

loadClassifications();
