// One-Click Model Retraining (Requirement 3.3)
function retrain() {
    const btn = document.querySelector('.btn-primary');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> OPTIMIZING...';
    btn.style.opacity = '0.7';

    fetch('/retrain', { method: 'POST' })
        .then(r => r.json())
        .then(data => {
            btn.innerHTML = originalText;
            btn.style.opacity = '1';
            alert(data.status); // User confirmation mechanism
        })
        .catch(err => {
            btn.innerHTML = originalText;
            btn.style.opacity = '1';
            console.error("Retraining failed:", err);
        });
}

// Stability: Real-time feedback polling (Requirement 3.1)
function updateDashboard() {
    fetch('/get_status')
        .then(response => response.json())
        .then(data => {
            const feedbackEl = document.getElementById('live-feedback');
            const statusDot = document.getElementById('status-dot');
            const engineStatus = document.getElementById('engine-status');

            feedbackEl.innerText = data.last_gesture;

            if (data.status.includes("Error")) {
                feedbackEl.style.color = "#ef4444";
                feedbackEl.innerText = data.status;
                statusDot.style.background = "#ef4444";
                engineStatus.innerText = "Error Detected";
                engineStatus.style.color = "#ef4444";
            } else {
                feedbackEl.style.color = "#38bdf8";
                statusDot.style.background = "#22c55e";
                engineStatus.innerText = "Operational";
                engineStatus.style.color = "#22c55e";
            }
        });
}

// Poll every 500ms for Visual Clarity
setInterval(updateDashboard, 500);