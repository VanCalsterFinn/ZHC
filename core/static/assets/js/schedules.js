document.addEventListener("DOMContentLoaded", () => {

    const scheduleModal = document.getElementById('scheduleModal');

    scheduleModal.addEventListener('show.bs.modal', (event) => {
        const button = event.relatedTarget.closest('button'); // ensures we get the button element
        const form = scheduleModal.querySelector('#scheduleForm');
        const title = scheduleModal.querySelector('#scheduleModalTitle');
        const submitBtn = scheduleModal.querySelector('#scheduleFormSubmit');

        if (button.id === "addScheduleBtn") {
            title.textContent = "Add Schedule";
            submitBtn.textContent = "Add Schedule";
            form.action = button.getAttribute('data-create-url'); // Add URL from button
            form.reset();
        } else {
            // Edit schedule
            const schedId = button.getAttribute('data-id');
            const zone = button.getAttribute('data-zone');
            const day = button.getAttribute('data-day');
            const start = button.getAttribute('data-start'); // "HH:MM:SS"
            const end = button.getAttribute('data-end');     // "HH:MM:SS"
            const temp = button.getAttribute('data-temp');

            title.textContent = "Edit Schedule";
            submitBtn.textContent = "Save Changes";
            form.action = `/schedules/edit/${schedId}/`; // Edit URL

            form.querySelector('#id_zone').value = zone;
            form.querySelector('#id_day_of_week').value = day;
            form.querySelector('#id_start_time').value = start.slice(0, 5);
            form.querySelector('#id_end_time').value = end.slice(0, 5);
            form.querySelector('#id_target_temperature').value = temp;
        }
    });

    // Delete modal
    const deleteModal = document.getElementById('deleteScheduleModal');
    deleteModal.addEventListener('show.bs.modal', (event) => {
        const button = event.relatedTarget;
        const schedId = button.getAttribute('data-id');
        const schedName = button.getAttribute('data-name');

        deleteModal.querySelector('.schedule-name').textContent = schedName;
        deleteModal.querySelector('#deleteScheduleForm').action = `/schedules/delete/${schedId}/`;
    });

});
