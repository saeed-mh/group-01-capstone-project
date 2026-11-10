
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


let currentClassificationId = null;

// Load available cities into the dropdown.
async function loadRegions() {
    const regionSelect = document.getElementById("region");

    try {
        const response = await fetch("/api/regions");

        if (!response.ok) {
            throw new Error("Failed to load cities.");
        }

        const regions = await response.json();

        for (const region of regions) {
            const option = document.createElement("option");
            option.value = region;
            option.textContent = region;
            regionSelect.appendChild(option);
        }

    } catch (error) {
        document.getElementById("classification-message").textContent =
            "Could not load cities.";
        console.error(error);
    }
}

// Submit text or image for classification.
async function classifyWaste(event) {
    event.preventDefault();

    const region = document.getElementById("region").value;
    const text = document.getElementById("item-text").value.trim();
    const image = document.getElementById("item-image").files[0];

    const message = document.getElementById("classification-message");
    const resultSection = document.getElementById("classification-result");
    const button = document.getElementById("classify-button");

    message.textContent = "";
    resultSection.hidden = true;
    currentClassificationId = null;

    if (!region) {
        message.textContent = "Please select a city.";
        return;
    }

    if ((text && image) || (!text && !image)) {
        message.textContent =
            "Please provide either text or an image.";
        return;
    }

    if (image) {
        const allowedTypes = ["image/jpeg", "image/png"];
        const allowedExtensions = /\.(jpg|jpeg|png)$/i;

        if (!allowedTypes.includes(image.type) ||
            !allowedExtensions.test(image.name)) {
            message.textContent = "Only JPG and PNG images are supported.";
            return;
        }

        if (image.size > 5 * 1024 * 1024) {
            message.textContent = "Image must not exceed 5 MB.";
            return;
        }
    }

    const formData = new FormData();
    formData.append("region", region);

    if (image) {
        formData.append("image", image);
    } else {
        formData.append("text", text);
    }

    button.disabled = true;
    message.textContent = "Classifying waste...";

    try {
        const response = await fetch("/api/classify", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            
            throw new Error(
                data.error || data.message || "Classification failed."
            );
        }

        currentClassificationId = data.id;

        document.getElementById("result-item").textContent =
            data.item_name;
        document.getElementById("result-category").textContent =
            data.category;
        document.getElementById("result-tip").textContent =
            data.tip || "No recycling tip available.";
        document.getElementById("result-explanation").textContent =
            data.explanation || "";

        const binElement = document.getElementById("result-bin");
        binElement.textContent = data.bin_name || "No bin information";

        // Show the bin in its assigned colour.
        const binColors = {
            yellow: "#d4a900",
            blue: "#1769aa",
            brown: "#8b5a2b",
            green: "#268347",
            black: "#333333",
            grey: "#666666",
            gray: "#666666",
            white: "#666666",
            red: "#ba3030",
            orange: "#c66a00"
        };

        const color = String(data.bin_color || "")
            .trim()
            .toLowerCase();

        binElement.style.color = binColors[color] || "";
        binElement.style.fontWeight = "bold";

        document.getElementById("feedback-message").textContent = "";
        document.getElementById("feedback-correct").disabled = false;
        document.getElementById("feedback-wrong").disabled = false;

        resultSection.hidden = false;
        message.textContent = "Classification completed successfully.";

        await loadClassifications();

    } catch (error) {
        message.textContent = error.message;
        console.error(error);

    } finally {
        button.disabled = false;
    }
}

// Send Correct/Wrong feedback to Flask.
async function submitFeedback(isCorrect) {
    if (currentClassificationId === null) {
        return;
    }

    const message = document.getElementById("feedback-message");
    const correctButton = document.getElementById("feedback-correct");
    const wrongButton = document.getElementById("feedback-wrong");

    correctButton.disabled = true;
    wrongButton.disabled = true;
    message.textContent = "Saving feedback...";

    try {
        const response = await fetch(
            `/api/classifications/${currentClassificationId}/feedback`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    is_correct: isCorrect
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            
            throw new Error(
                data.error || data.message || "Could not save feedback."
            );

        }

        message.textContent = "Thank you! Your feedback was saved.";

        await loadClassifications();

    } catch (error) {
        message.textContent = error.message;
        correctButton.disabled = false;
        wrongButton.disabled = false;
        console.error(error);
    }
}

// Connect the HTML controls to the JavaScript functions.
document.getElementById("classification-form")
    .addEventListener("submit", classifyWaste);

document.getElementById("feedback-correct")
    .addEventListener("click", () => submitFeedback(true));

document.getElementById("feedback-wrong")
    .addEventListener("click", () => submitFeedback(false));

loadRegions();

