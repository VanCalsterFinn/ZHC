document.addEventListener("DOMContentLoaded", function() {
    const csrfToken = '{{ csrf_token }}';

    document.querySelectorAll('.adjust-btn').forEach(button => {
        button.addEventListener('click', function() {
            const zoneId = this.dataset.zone;
            const delta = this.dataset.delta;

            fetch("{% url 'controller:override_adjust' %}", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken
                },
                body: new URLSearchParams({zone: zoneId, delta: delta})
            })
            .then(res => res.json())
            .then(data => {
                if(data.success) {
                    const display = document.querySelector(`.zone-target-temp[data-zone-id='${zoneId}']`);
                    if(display) {
                        display.textContent = parseFloat(data.new_target).toFixed(1) + '°C';
                    }
                } else {
                    console.error(data.error);
                }
            })
            .catch(err => console.error(err));
        });
    });
});


