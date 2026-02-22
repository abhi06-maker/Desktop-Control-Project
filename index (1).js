// ================= START CAPTURE =================
function startCapture() {
    const name = prompt("Enter new gesture name:");
    if (!name) return;

    fetch("/start_capture", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: name })
    })
    .then(res => res.json())
    .then(data => alert(data.status))
    .catch(err => {
        console.error("Capture error:", err);
        alert("Failed to start capture");
    });
}


// ================= EDIT MAPPING =================
function editMapping() {
    const gesture = prompt("Enter gesture name:");
    if (!gesture) return;

    const action = prompt(
        "Enter action:\nSwitch_Tab\nMedia_Play\nVolume_Up"
    );
    if (!action) return;

    fetch("/update_mapping", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ gesture, action })
    })
    .then(res => res.json())
    .then(data => alert(data.status))
    .catch(err => {
        console.error("Mapping error:", err);
        alert("Mapping update failed");
    });
}


// ================= ONE-CLICK RETRAIN =================
function retrain() {
    const btn = document.querySelector('.btn-primary');
    const originalText = btn.innerHTML;

    btn.innerHTML =
        '<i class="fas fa-circle-notch fa-spin"></i> OPTIMIZING...';
    btn.style.opacity = '0.7';

    fetch('/retrain', { method: 'POST' })
        .then(r => r.json())
        .then(data => {
            btn.innerHTML = originalText;
            btn.style.opacity = '1';
            alert(data.status);
        })
        .catch(err => {
            btn.innerHTML = originalText;
            btn.style.opacity = '1';
            console.error("Retraining failed:", err);
            alert("Retrain failed");
        });
}


// ================= LIVE DASHBOARD =================
function updateDashboard() {
    fetch('/get_status')
        .then(response => response.json())
        .then(data => {
            const feedbackEl = document.getElementById('live-gesture');
            const statusDot = document.getElementById('status-dot');
            const engineStatus = document.getElementById('engine-status');

            // 🔥 Gesture update (safe)
            if (feedbackEl) {
                feedbackEl.innerText = data.last_gesture;
                feedbackEl.style.color = "#38bdf8";
            }

            // 🔥 Status update
            if (data.status.includes("Error")) {
                if (statusDot) statusDot.style.background = "#ef4444";
                if (engineStatus) {
                    engineStatus.innerText = "Error Detected";
                    engineStatus.style.color = "#ef4444";
                }
            } else {
                if (statusDot) statusDot.style.background = "#22c55e";
                if (engineStatus) {
                    engineStatus.innerText = "Operational";
                    engineStatus.style.color = "#22c55e";
                }
            }
        })
        .catch(err => {
            console.error("Dashboard update failed:", err);
        });
}


// ================= AUTO REFRESH =================
setInterval(updateDashboard, 500);

function editMapping() {
    const gesture = prompt("Enter gesture name (exact model label):");
    if (!gesture) return;

    const action = prompt(
        "Enter action:\nalt_tab\nplay_pause\nvolume_up"
    );
    if (!action) return;

    fetch("/update_mapping", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ gesture, action })
    })
    .then(r => r.json())
    .then(d => alert(d.status))
    .catch(() => alert("Mapping update failed"));
}

// ================= MODAL CONTROL =================
function openModal(type) {
    if (type === "mapping") {
        document.getElementById("mappingModal").style.display = "flex";
    }
}

function closeModal() {
    document.getElementById("mappingModal").style.display = "none";
}


// ================= SAVE MAPPING =================
function saveMapping() {
    const gesture = document.getElementById("gestureSelect").value;
    const action = document.getElementById("actionSelect").value;

    fetch("/update_mapping", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ gesture, action })
    })
    .then(r => r.json())
    .then(d => {
        alert(d.status);
        closeModal();
    })
    .catch(() => alert("Mapping update failed"));
}
