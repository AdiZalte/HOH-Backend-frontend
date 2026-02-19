window.onload = () => {

    const needle = document.getElementById('gaugeNeedle');
    const scoreEl = document.getElementById('liveScore');
    const ratingEl = document.getElementById('liveRating');

    setTimeout(() => {
        const target = 750;
        const rotation = -90 + ((target - 300) / 550 * 180);
        needle.style.transform = `rotate(${rotation}deg)`;

        let current = 300;
        const duration = 2500;
        const startTime = performance.now();

        function animate(time) {
            const elapsed = time - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const easedProgress = 1 - Math.pow(1 - progress, 4);
            current = Math.floor(300 + (target - 300) * easedProgress);
            scoreEl.innerText = current;

            if (current > 700) {
                ratingEl.innerText = "Excellent";
                ratingEl.style.color = "#22c55e";
            }

            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                setTimeout(() => { document.body.classList.add('activated'); }, 800);
            }
        }
        requestAnimationFrame(animate);
    }, 1000);
};



async function fetchCustomerData() {
    const customerId = document.getElementById('custSearchInput').value;
    const btn = document.getElementById('fetchBtn');

    if (!customerId) {
        alert("Please enter a Customer ID!");
        return;
    }

    btn.innerText = "Analyzing...";
    btn.disabled = true;

    try {
        const response = await fetch(`/api/customer/${customerId}`);

        if (!response.ok) throw new Error("Customer not found!");

        const data = await response.json();
        const c = data.customer;

        // Profile
        document.getElementById('val-id').innerText = c.id || customerId;
        document.getElementById('val-age').innerText = c.age || "N/A";
        document.getElementById('val-income').innerText = c.MonthlyIncome ? `₹${Number(c.MonthlyIncome).toLocaleString()}` : "0";
        document.getElementById('val-debt').innerText = c.DebtRatio ? Number(c.DebtRatio).toFixed(4) : "0";
        document.getElementById('val-dep').innerText = c.NumberOfDependents || "0";
        document.getElementById('val-revol').innerText = c.RevolvingUtilizationOfUnsecuredLines ? Number(c.RevolvingUtilizationOfUnsecuredLines).toFixed(4) : "0";
        document.getElementById('val-late30').innerText = c['NumberOfTime30-59DaysPastDueNotWorse'] || "0";
        document.getElementById('val-late60').innerText = c['NumberOfTime60-89DaysPastDueNotWorse'] || "0";
        document.getElementById('val-late90').innerText = c.NumberOfTimes90DaysLate || "0";
        document.getElementById('val-open').innerText = c.NumberOfOpenCreditLinesAndLoans || "0";
        document.getElementById('val-real').innerText = c.NumberRealEstateLoansOrLines || "0";

        // Result
        if (typeof data.riskScore === 'number') {
            const riskVal = ((1 - data.riskScore) * 100).toFixed(1);
            updateRiskMeter(riskVal);

            // SHAP
            fetchShapExplanation(customerId);
        } else {
            console.warn("Invalid risk score from backend:", data.riskScore);
            document.getElementById('riskPercent').innerText = "N/A";
            document.getElementById('riskLevelText').innerText = "Score Unavailable";
            document.getElementById('riskLevelText').style.color = "#94a3b8";
            document.getElementById('riskNeedle').style.transform = `rotate(-90deg)`;
            document.getElementById('shapSection').style.display = 'none';
        }

    } catch (error) {
        console.error("Error:", error);
        alert(error.message || "Failed to connect to backend");
    } finally {
        btn.innerText = "Analyze";
        btn.disabled = false;
    }
}

async function fetchShapExplanation(id) {
    const shapChart = document.getElementById('shapChart');
    const shapSection = document.getElementById('shapSection');

    shapChart.innerHTML = '<p style="text-align: center;">Loading methodology...</p>';
    shapSection.style.display = 'block';

    try {
        const response = await fetch(`/api/customer/${id}/explain`);
        if (!response.ok) throw new Error("Explanation failed");

        const data = await response.json();
        renderShapExplanation(data.explanation);
    } catch (error) {
        console.error("SHAP Error:", error);
        shapChart.innerHTML = '<p style="color: #ff4d4d;">Unavailable</p>';
    }
}

function renderShapExplanation(explanation) {
    const container = document.getElementById('shapChart');
    container.innerHTML = '';

    const { shap_values, feature_names, feature_values } = explanation;

    // Sort
    const features = feature_names.map((name, idx) => ({
        name: name,
        value: shap_values[idx],
        featureValue: feature_values[idx]
    })).sort((a, b) => Math.abs(b.value) - Math.abs(a.value));

    const maxAbs = Math.max(...features.map(f => Math.abs(f.value)), 0.001);

    features.forEach(f => {
        const row = document.createElement('div');
        row.className = 'shap-bar-row';

        const isPositive = f.value > 0;
        const width = (Math.abs(f.value) / maxAbs) * 100;

        row.innerHTML = `
            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 5px;">
                <span style="color: #e2e8f0;">${f.name} <small style="color: #94a3b8;">(${Number(f.featureValue).toFixed(2)})</small></span>
                <span style="color: ${isPositive ? '#ff4d4d' : '#22c55e'}; font-weight: bold;">
                    ${isPositive ? '+' : ''}${f.value.toFixed(4)}
                </span>
            </div>
            <div class="shap-bar-container">
                <div class="shap-bar ${isPositive ? 'positive' : 'negative'}" style="width: ${width}%;"></div>
            </div>
        `;
        container.appendChild(row);
    });
}

function updateRiskMeter(percentage) {
    const riskNeedle = document.getElementById('riskNeedle');
    const riskPercentText = document.getElementById('riskPercent');
    const riskLevelText = document.getElementById('riskLevelText');

    const rotation = -90 + (percentage / 100 * 180);
    riskNeedle.style.transform = `rotate(${rotation}deg)`;
    riskPercentText.innerText = percentage + "%";

    if (percentage > 70) {
        riskLevelText.innerText = "Strong Profile";
        riskLevelText.style.color = "#22c55e";
    } else if (percentage > 30) {
        riskLevelText.innerText = "Moderate Risk";
        riskLevelText.style.color = "#fbbf24";
    } else {
        riskLevelText.innerText = "Critical Risk";
        riskLevelText.style.color = "#ff4d4d";
    }
}


document.getElementById('fetchBtn').addEventListener('click', fetchCustomerData);