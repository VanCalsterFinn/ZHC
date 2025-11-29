document.addEventListener("DOMContentLoaded", () => {

    // -------------------------------
    // Delete Zone Modal
    // -------------------------------
    const deleteModal = document.getElementById('deleteZoneModal');
    deleteModal.addEventListener('show.bs.modal', (event) => {
        const button = event.relatedTarget; // Button that triggered modal
        const zoneName = button.getAttribute('data-name');
        const zoneId = button.getAttribute('data-id');

        const span = deleteModal.querySelector('.zone-name');
        span.textContent = zoneName;

        const form = deleteModal.querySelector('#deleteZoneForm');
        form.action = `/zones/${zoneId}/delete/`;
    });

    // -------------------------------
    // Edit/Add Zone Modal
    // -------------------------------
    const zoneModal = document.getElementById('zoneModal');
    zoneModal.addEventListener('show.bs.modal', (event) => {
        const button = event.relatedTarget;

        const form = zoneModal.querySelector('#zoneForm');
        const title = zoneModal.querySelector('#zoneModalTitle');

        if (button.id === "addZoneBtn") {
            // Add mode
            title.textContent = "Add Zone";
            form.action = "/zones/add/";
            form.reset();
        } else {
            // Edit mode
            const zoneId = button.getAttribute('data-id');
            const zoneName = button.getAttribute('data-name');
            const zonePin = button.getAttribute('data-pin');

            title.textContent = "Edit Zone";
            form.action = `/zones/${zoneId}/edit/`;
            form.querySelector('#id_name').value = zoneName;
            form.querySelector('#id_pin').value = zonePin;
        }
    });

});
