// Farm Input Variables
const farmSelect = document.getElementById('farmSelect');
const formContainer = document.getElementById('trackingFormContainer');
const farmNameDisplay = document.getElementById('selectedFarmName');
const cropInfoDisplay = document.getElementById('selectedCropInfo');
const activeFarmInput = document.getElementById('activeFarmId');
const weekBadge = document.getElementById('currentWeekBadge');
const establishmentCard = document.getElementById('cardEstablishment');
const submitBtn = document.getElementById('submitLogBtn');
const alertArea = document.getElementById('alertArea');
const stageContainer = document.getElementById("stageContainer");
const lccScoreSelect = document.getElementById("lcc_score");
const height = document.getElementById("height");
const standCount = document.getElementById("stand_count");
// Charts Variables
const logisticsBtn = document.getElementById('showLogisticsBtn');
const heightChartImg = document.getElementById('heightChartImg');
const stageChartImg = document.getElementById('stageChartImg');
const chartsLoader = document.getElementById('chartsLoader');
const chartsContainer = document.getElementById('chartsContainer');

// 1. Handle Farm Selection
farmSelect.addEventListener('change', async function() {
    const selectedOption = this.options[this.selectedIndex];
    
    if (selectedOption.value) {
        // Get data attributes
        const farmId = selectedOption.value;
        const farmLabel = selectedOption.text.split('(')[0]; // Extract name
        const cropName = selectedOption.getAttribute('data-crop-name');
        const weekNum = parseInt(selectedOption.getAttribute('data-week'));

        // Populate UI
        farmNameDisplay.textContent = farmLabel;
        cropInfoDisplay.textContent = cropName;
        activeFarmInput.value = farmId;
        weekBadge.textContent = `Week ${weekNum}`;

        // Logic: Hide Establishment Card if Week > 4
        if (weekNum > 4) {
            establishmentCard.classList.add('d-none');
        } else {
            establishmentCard.classList.remove('d-none');
        }

        const response = await fetch(`api/crop_standards/${farmId}`);
        const data = await response.json();
        
        if (data && response.ok) {
            lccScoreSelect.innerHTML = `<option value="" selected>Select Score...</option>
                                    <option value="1">1 - Yellowish Green (Starved)</option>
                                    <option value="2">2 - Pale Green</option>
                                    <option value="3">3 - Green${(data.optimal_lcc==3)?' (Optimal)':''}</option>
                                    <option value="4">4 - Dark Green${(data.optimal_lcc==4)?' (Optimal)':''}</option>
                                    <option value="5">5 - Very Dark Green${(data.optimal_lcc==5)?' (Optimal)':''}</option>
                                    <option value="6">6 - Excessive Nitrogen</option>`

            stageContainer.innerHTML = "";
            let colors = ["success", "warning", "secondary"];
            data.stages.forEach((stage, index) => {
                let inputField = document.createElement('input');
                inputField.setAttribute('type', 'radio');
                inputField.setAttribute('class', 'btn-check');
                inputField.setAttribute('name', 'phenology_stage');
                inputField.setAttribute('value', stage[0]);
                inputField.setAttribute('id', stage[0]);
                inputField.setAttribute('autocomplete', 'off');

                let label = document.createElement('label');
                // index % colors.length makes sure that colors cycle through if more than 3 stages are there
                label.setAttribute('class', `btn btn-outline-${colors[index % colors.length]}`);
                label.setAttribute('for', stage[0]);
                label.innerText = stage[1].label;

                stageContainer.appendChild(inputField);
                stageContainer.appendChild(label);
            });

            activeFarmInput.value = farmId;
            formContainer.classList.remove('d-none');
        }
        else {
            console.log(data.error);
        }
        // Show Option for charts
        logisticsBtn.classList.remove('d-none');
    }
});

// 2. Handle Form Submission
submitBtn.addEventListener('click', async function() {
    const moisture = document.querySelector("#moistureBox>input:checked");
    const stage = document.querySelector("#stageContainer>input:checked");

    const formData = {
        moisture: (moisture)?moisture.value:null,
        height: height.value,
        lcc: lccScoreSelect.value,
        stage: (stage)?stage.value:null,
        stand_count: standCount.value
    }

    const farmId = activeFarmInput.value;

    // Reset Alerts
    alertArea.innerHTML = '';
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Saving...';

    try {
        const response = await fetch(`/log_field_data/${farmId}`, {
            method: 'POST',
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(formData)
        });
    
        const data = await response.json();
        
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i data-lucide="save" class="me-2"></i> Save Field Log';
        lucide.createIcons(); // Re-init icons
    
        // Show Alerts (The Roast/Advice)
        if (data.alerts && data.alerts.length > 0) {
            let alertHTML = '';
            data.alerts.forEach(alert => {
                alertHTML += `
                    <div class="alert alert-warning alert-custom alert-dismissible fade show shadow-sm" role="alert">
                        <div class="d-flex align-items-center">
                            <i data-lucide="alert-triangle" class="me-2"></i>
                            <div>${alert}</div>
                        </div>
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                `;
            });
            alertArea.innerHTML = alertHTML;
            lucide.createIcons();
        } else {
            // Success Message
            alertArea.innerHTML = `
                <div class="alert alert-success alert-dismissible fade show shadow-sm" role="alert">
                    <i data-lucide="check-circle" class="me-2"></i>
                    <strong>Log Saved!</strong> Great job keeping your records updated.
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `;
            lucide.createIcons();
            // Optional: Reset form or scroll to top
            // document.getElementById('fieldLogForm').reset();
        }
    }
    catch(error){
        console.error('Error:', error);
        submitBtn.disabled = false;
        submitBtn.textContent = 'Save Field Log';
        alert('An error occurred. Please try again.');
    }
});

logisticsBtn.addEventListener('click', async function() {
    const farmId = activeFarmInput.value;
    if(!farmId) return;

    // Reset Modal State
    chartsLoader.classList.remove('d-none');
    chartsContainer.classList.add('d-none');

    // Fetch Images
    try {
        const response = await fetch(`/api/farm_analytics/${farmId}`)
        
        const data = await response.json();
        // Inject Base64 Strings
        heightChartImg.src = `data:image/png;base64,${data.height_chart}`;
        stageChartImg.src = `data:image/png;base64,${data.stage_chart}`;
        
        // Swap Views
        chartsLoader.classList.add('d-none');
        chartsContainer.classList.remove('d-none');
    }
    catch(error) {
        console.error("Chart Error:", error);
        chartsLoader.innerHTML = `<p class="text-danger">Failed to load charts.</p>`;
    }
});