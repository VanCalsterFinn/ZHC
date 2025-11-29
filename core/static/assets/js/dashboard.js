// Get CSRF token from cookies
function getCSRFToken() {
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : null;
}

// Fetch zones and render dashboard (mobile-friendly)
async function fetchZones() {
    try {
        const response = await fetch("/api/zones/", {
            method: "GET",
            credentials: "include",
            headers: { "Accept": "application/json" }
        });

        if (!response.ok) {
            if (response.status === 401) alert("You are not logged in.");
            throw new Error(`Failed to fetch zones: ${response.status}`);
        }

        const zones = await response.json();
        const container = document.getElementById("zones-container");
        container.innerHTML = "";

        zones.forEach(zone => {
            const displayTemp = zone.manual_override?.target_temperature ?? zone.target_temperature;

            // Card column
            const cardCol = document.createElement("div");
            cardCol.className = "col-md-4 col-sm-6 mb-4";

            // Card container
            const card = document.createElement("div");
            card.className = "card zone-card shadow-sm position-relative p-3";
            card.dataset.zoneId = zone.id;
            card.dataset.targetTemp = displayTemp;

            // Badge
            const badge = document.createElement("span");
            badge.className = zone.manual_override?.active
                ? "badge bg-warning text-dark zone-badge position-absolute top-0 end-0 m-2"
                : "badge bg-success zone-badge position-absolute top-0 end-0 m-2";
            badge.textContent = zone.manual_override?.active ? "Manual Override" : "Schedule Active";

            // Card inner HTML
            card.innerHTML = `
                <h3 class="zone-title mb-3">${zone.name}</h3>

                <div class="d-flex align-items-center justify-content-start mb-2 target-temp-container">
                    <div class="target-temp display-3 me-3">${displayTemp.toFixed(1)}°C</div>
                    <div class="d-flex flex-column gap-2">
                        <button class="temperature-btn btn btn-outline-dark thermostat-btn" data-zone-id="${zone.id}" data-delta="1">
                            <i class="ti ti-plus"></i>
                        </button>
                        <button class="temperature-btn btn btn-outline-dark thermostat-btn" data-zone-id="${zone.id}" data-delta="-1">
                            <i class="ti ti-minus"></i>
                        </button>
                    </div>
                </div>

                <div class="current-temp text-muted">Current: ${zone.current_temperature.toFixed(1)}°C</div>
            `;

            card.appendChild(badge);
            cardCol.appendChild(card);
            container.appendChild(cardCol);
        });

        attachTemperatureButtons();

    } catch (error) {
        console.error("Error fetching zones:", error);
        alert("Failed to load zones. See console for details.");
    }
}

// Attach mobile-friendly +1/-1 buttons
function attachTemperatureButtons() {
    document.querySelectorAll(".thermostat-btn").forEach(btn => {
        const handleClick = async (event) => {
            const button = event.currentTarget; // the button, not the icon
            const zoneId = parseInt(button.dataset.zoneId, 10);
            const delta = parseInt(button.dataset.delta, 10);

            try {
                await adjustTemperature(zoneId, delta);

                // ripple effect
                button.classList.add("clicked");
                setTimeout(() => button.classList.remove("clicked"), 300);
            } catch (err) {
                console.error("Error adjusting temperature:", err);
            }
        };

        btn.addEventListener("click", handleClick);
        btn.addEventListener("touchend", handleClick);
    });
}

async function adjustTemperature(zoneId, delta) {
    const MIN_TEMP = 5;
    const MAX_TEMP = 30;

    try {
        // Get current zone
        const zoneRes = await fetch(`/api/zones/${zoneId}/`, { credentials: "include" });
        if (!zoneRes.ok) throw new Error("Failed to fetch zone");
        const zone = await zoneRes.json();

        const currentTemp = parseFloat(zone.manual_override?.target_temperature ?? zone.target_temperature);
        const newTemp = Math.min(MAX_TEMP, Math.max(MIN_TEMP, currentTemp + delta));

        const csrftoken = getCSRFToken();

        if (zone.manual_override) {
            // PATCH existing override
            const patchRes = await fetch(`/api/overrides/${zone.manual_override.id}/`, {
                method: "PATCH",
                credentials: "include",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrftoken
                },
                body: JSON.stringify({ target_temperature: newTemp })
            });

            if (!patchRes.ok) {
                const errData = await patchRes.json();
                console.error("Failed to update override:", errData);
                alert("Failed to update manual override. See console for details.");
                return;
            }

        } else {
            // POST new override
            const postRes = await fetch(`/api/overrides/`, {
                method: "POST",
                credentials: "include",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrftoken
                },
                body: JSON.stringify({ zone: zoneId, target_temperature: newTemp, active: true })
            });

            if (!postRes.ok) {
                const errData = await postRes.json();
                console.error("Failed to create override:", errData);
                alert("Failed to create manual override. See console for details.");
                return;
            }
        }

        // Update UI immediately
        const card = document.querySelector(`div[data-zone-id="${zoneId}"]`);
        card.dataset.targetTemp = newTemp;
        card.querySelector(".target-temp").textContent = `${newTemp.toFixed(1)}°C`;

    } catch (error) {
        console.error("Error adjusting temperature:", error);
        alert("An unexpected error occurred. See console for details.");
    }
}

// Call fetchZones on page load
document.addEventListener("DOMContentLoaded", fetchZones);

// Refresh zones every 10 seconds
setInterval(fetchZones, 10000);
