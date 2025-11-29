(function () {
  // Reusable Uppy setup function
  function initPlaylistUploader(modalEl) {
    const playlistForm = modalEl.querySelector("#playlistForm");
    if (!playlistForm) return;

    const playlistId = playlistForm.dataset.playlistId || playlistForm.querySelector("[name='id']")?.value;
    const uploaderEl = modalEl.querySelector("#uppyUploader");
    if (!uploaderEl || !playlistId) return;

    // Prevent multiple inits
    if (uploaderEl.dataset.uppyInitialized) return;
    uploaderEl.dataset.uppyInitialized = "true";

    console.log("Initializing Uppy for playlist:", playlistId);

    // Initialize Uppy
    const uppy = new Uppy.Core({
      restrictions: { maxNumberOfFiles: 50, allowedFileTypes: ["image/*", "video/*"] },
      autoProceed: true,
    });

    uppy.use(Uppy.DragDrop, {
      target: "#uppyUploader",
      note: "Upload images or videos by dragging here",
    });

    uppy.use(Uppy.XHRUpload, {
      endpoint: `/playlists/${playlistId}/upload/`,
      fieldName: "file",
    });

    // Handle upload success
    uppy.on("upload-success", (file, response) => {
      const data = response.body;
      const container = modalEl.querySelector("#playlistItems");
      if (!container) return;

      const preview = document.createElement("div");
      preview.classList.add("playlist-item", "border", "rounded-3", "p-2", "text-center");
      preview.dataset.id = data.id;
      preview.innerHTML = `
        ${
          data.file_url.endsWith(".mp4")
            ? `<video src="${data.file_url}" class="rounded" style="width:120px;height:80px;" controls muted></video>`
            : `<img src="${data.file_url}" class="rounded" style="width:120px;height:80px;object-fit:cover;">`
        }
        <div class="small mt-1 text-muted text-truncate" style="max-width:120px;">${data.filename}</div>
      `;
      container.appendChild(preview);
    });
  }

  // Initialize Uppy only after the modal is shown
  document.addEventListener("shown.bs.modal", function (event) {
    const modalEl = event.target;
    if (modalEl.id === "playlistModal") {
      initPlaylistUploader(modalEl);
    }
  });
})();
