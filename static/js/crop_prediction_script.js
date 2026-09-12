lucide.createIcons();

const validSoilTypes = [
    "Alluvial Soil",
    "Black Cotton Soil",
    "Black Soil",
    "Brown Loamy Soil",
    "Clay Loamy Soil",
    "Clay Soil",
    "Cotton Soil",
    "Deep Soil",
    "Friable Soil",
    "Heavy Black Soil",
    "Heavy Soil",
    "Laterite Soil",
    "Light Loamy Soil",
    "Light Soil",
    "Loamy Soil",
    "Medium Black Soil",
    "Red Lateritic Loamy Soil",
    "Red Loamy Soil",
    "Red Soil",
    "Rich Red Loamy Soil",
    "Salty Clay Loamy Soil",
    "Sandy Clay Loamy Soil",
    "Sandy Loamy Soil",
    "Sandy Soil",
    "Shallow Black Soil",
    "Silty Loamy Soil",
    "Well-Drained Loamy Soil",
    "Well-Drained Soil",
    "Well-Grained Deep Loamy Moist Soil"
];

const n = document.getElementById("nitrogen");
const nitrogenError = document.getElementById("nitrogenError");

const p = document.getElementById("phosphorus");
const phosphorusError = document.getElementById("phosphorusError");

const k = document.getElementById("potassium");
const potassiumError = document.getElementById("potassiumError");

const ph = document.getElementById("ph");
const phError = document.getElementById("phError");

const humidity = document.getElementById("humidity");
const humidityError = document.getElementById("humidityError");

const temp = document.getElementById("temperature");
const tempError = document.getElementById("tempError");

const downloadPdfBtn = document.getElementById("downloadPdfBtn");

const soil = document.getElementById("soil");
const soilError = document.getElementById("soilError");
for (let soilType of validSoilTypes) {
    soil.innerHTML += `<option value='${soilType}'>${soilType}</option>`;
}

n.addEventListener("change", event => {
    validateData(n, nitrogenError, "Nitrogen", 0, 300);
});

p.addEventListener("change", event => {
    validateData(p, phosphorusError, "Phosphorus", 0, 300);
});

k.addEventListener("change", event => {
    validateData(k, potassiumError, "Potassium", 0, 300);
});

ph.addEventListener("change", event => {
    validateData(ph, phError, "pH", 0, 14);
});

humidity.addEventListener("change", event => {
    validateData(humidity, humidityError, "Humidity", 0, 100);
});

temp.addEventListener("change", event => {
    validateData(temp, tempError, "Temperature", 0, 60);
});

function validateData(field, errorField, featureName, lowerLimit, upperLimit) {
    if (field.value<lowerLimit || field.value>upperLimit) {
        errorField.innerHTML = `<p class='small text-danger'>${featureName} value should be between ${lowerLimit} and ${upperLimit}!</p>`;
    }
    else {
        errorField.innerHTML = ``;
    }
}

async function predictCrop(event) {
    event.preventDefault();

    if (soil.value=="==Choose Soil Type==") {
        soilError.innerHTML = `<p class='small text-danger'>Soil type is necessary!</p>`;
        return;
    }

    // ----- SHOW LOADING -----
    document.getElementById("result-before").classList.add("d-none");
    document.getElementById("result-after").classList.add("d-none");
    document.getElementById("result-loading").classList.remove("d-none");

    // Disable submit button
    const submitBtn = event.target.querySelector("button[type='submit']");
    submitBtn.disabled = true;
    submitBtn.innerText = "Processing...";

    const formData = {
        n: n.value,
        p: p.value,
        k: k.value,
        ph: ph.value,
        temp: temp.value,
        humidity: humidity.value,
        soil_type: soil.value
    }

    const response = await fetch("/api/predict-crop", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(formData)
    });

    const data = await response.json();
    if (!response.ok || data.error) {
        document.getElementById("result-loading").classList.add("d-none");
        document.getElementById("result-before").classList.remove("d-none");
        document.getElementById("result-after").classList.add("d-none");
        document.getElementById("errorMessage").innerText = data.error || "Unknown Error Occured";

        submitBtn.disabled = false;
        submitBtn.innerText = "🌾 Get Recommendation"
    }
    else {
        document.getElementById("cropName").innerText = data.result;
        document.getElementById("matchText").innerText = `${data.match_percentage}% Match`;
        document.getElementById("matchBar").style.width = `${data.match_percentage}%`;
        document.getElementById("harvestTime").innerText = `${data.duration[0]} - ${data.duration[1]}`;
        document.getElementById("waterReqText").innerText = `${data.water_req} mm`;
        downloadPdfBtn.setAttribute("data-report-id", data.report_id);

        const fertList = document.getElementById("fertilizerList");
        if (fertList) {
            fertList.innerHTML = ""; // Clear old recommendations
            
            // Loop through the list that Python backend sent
            data.recommendations.forEach(rec => {
                const li = document.createElement("li");
                li.innerText = rec;
                li.classList.add("list-group-item", "d-flex", "justify-content-between", "align-items-center");
                
                // We convert text to lowercase to safely check keywords
                const lowerRec = rec.toLowerCase();
                if (lowerRec.includes("optimal")) {
                    // Green for good news
                    li.classList.add("bg-success-subtle");
                    li.innerHTML += ' <span class="badge bg-success rounded-pill">✔ Good</span>';
                } 
                else if (lowerRec.includes("low")) {
                    // Red for "Action Required" (Low nutrients)
                    li.classList.add("bg-danger-subtle");
                    li.innerHTML += ' <span class="badge bg-danger rounded-pill">⚠ Low</span>';
                } 
                else if (lowerRec.includes("high")) {
                    // Yellow for "Warning" (High nutrients)
                    li.classList.add("bg-warning-subtle");
                    li.innerHTML += ' <span class="badge bg-warning text-dark rounded-pill">! High</span>';
                }
                
                fertList.appendChild(li);
            });
        }
    
        document.getElementById("result-loading").classList.add("d-none");
        document.getElementById("result-after").classList.remove("d-none");

        submitBtn.disabled = false;
        submitBtn.innerText = "🌾 Get Recommendation";
    }
    lucide.createIcons();
}

downloadPdfBtn.addEventListener("click", function(event) {
    const reportId = downloadPdfBtn.getAttribute("data-report-id");
    if (!reportId) return alert("Please generate a prediction first!");
    
    // Triggers a browser navigation to the download route. 
    // Because the server responds with a 'Content-Disposition: attachment' header, 
    // the browser aborts the redirect and instead downloads the PDF file natively.
    window.location.href = `/download_report/${reportId}`;
});