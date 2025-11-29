document.addEventListener("DOMContentLoaded", () => {
  const playlistId = document.getElementById("playlistPage").dataset.playlistId;
  const container = document.getElementById("playlistItems");
  const fileInput = document.getElementById("fileInput");
  const uploadTile = document.getElementById("uploadTile");
  let deleteTargetId = null; // store the item id to delete
  const deleteModal = new bootstrap.Modal(document.getElementById("deleteItemModal"));
  const confirmDeleteBtn = document.getElementById("confirmDeleteBtn");

  // ----------------------------
  // CSRF helper
  // ----------------------------
  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
  }

  // ----------------------------
  // Open file picker when clicking the upload tile
  // ----------------------------
  // Upload zone drag & drop support
    uploadTile.addEventListener("click", () => fileInput.click());

    uploadTile.addEventListener("dragover", (e) => {
    e.preventDefault();
    uploadTile.classList.add("dragover");
    });

    uploadTile.addEventListener("dragleave", () => {
    uploadTile.classList.remove("dragover");
    });

    uploadTile.addEventListener("drop", (e) => {
    e.preventDefault();
    uploadTile.classList.remove("dragover");
    fileInput.files = e.dataTransfer.files;

    // Trigger the normal upload handler
    const event = new Event("change");
    fileInput.dispatchEvent(event);
    });


  // ----------------------------
  // Upload handler
  // ----------------------------
  fileInput.addEventListener("change", async (e) => {
    for (const file of e.target.files) {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch(`/playlists/${playlistId}/upload/`, {
        method: "POST",
        body: formData,
        headers: { "X-CSRFToken": getCookie("csrftoken") },
      });

      const data = await res.json();
      if (!data.success) {
        alert("Upload failed!");
        continue;
      }

      // Create new media tile
      const col = document.createElement("div");
      col.classList.add("col-6", "col-md-4", "col-lg-3");
      col.innerHTML = `
        <div class="playlist-item position-relative border rounded-4 shadow-sm overflow-hidden" 
             data-id="${data.id}" style="width:100%; aspect-ratio:16/9;">
          
          ${file.type.startsWith("video")
            ? `<div class="video-placeholder bg-dark text-white d-flex justify-content-center align-items-center w-100 h-100 cursor-pointer">
                 <i class="ti ti-player-play fs-2"></i>
               </div>
               <video src="${data.file_url}" class="w-100 h-100 object-fit-cover d-none" controls muted></video>`
            : `<img src="${data.file_url}" class="w-100 h-100 object-fit-cover" />`
          }

          <button class="delete-item-btn btn btn-sm btn-danger position-absolute top-0 end-0 m-2 rounded-circle opacity-0 transition-opacity" data-id="${data.id}">
            <i class="ti ti-trash"></i>
          </button>
        </div>
      `;
      container.appendChild(col);
    }

    // Reset input
    fileInput.value = "";
  });

  // ----------------------------
  // Video placeholder click to load video
  // ----------------------------
  container.addEventListener("click", (e) => {
    const placeholder = e.target.closest(".video-placeholder");
    if (!placeholder) return;

    const parent = placeholder.parentElement;
    const video = parent.querySelector("video");
    placeholder.classList.add("d-none");
    video.classList.remove("d-none");
    video.play();
  });

  // ----------------------------
  // Delete handler
  // ----------------------------
    // click handler for delete buttons
    container.addEventListener("click", (e) => {
    const btn = e.target.closest(".delete-item-btn");
    if (!btn) return;

    e.preventDefault(); // prevent navigation
    deleteTargetId = btn.dataset.id;
    deleteModal.show();
    });

    // confirm deletion
    confirmDeleteBtn.addEventListener("click", async () => {
    if (!deleteTargetId) return;

    try {
        const res = await fetch(`/playlists/item/${deleteTargetId}/delete/`, {
        method: "POST",
        headers: { "X-CSRFToken": getCookie("csrftoken") },
        });
        const data = await res.json();
        if (data.success) {
        const itemEl = container.querySelector(`.playlist-item[data-id='${deleteTargetId}']`);
        if (itemEl) itemEl.closest(".col-6, .col-md-4, .col-lg-3").remove();
        } else {
        console.error("Failed to delete item:", data);
        }
    } catch (err) {
        console.error(err);
    } finally {
        deleteModal.hide();
        deleteTargetId = null;
    }
    });

  // ----------------------------
  // Drag & drop reorder using SortableJS
  // ----------------------------
  if (window.Sortable) {
    new Sortable(container, {
      animation: 150,
      handle: ".playlist-item",
      onEnd: () => {
        const order = Array.from(container.querySelectorAll(".playlist-item")).map((el, i) => ({
          id: el.dataset.id,
          order: i + 1,
        }));

        fetch(`/playlists/${playlistId}/reorder/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
          },
          body: JSON.stringify(order),
        });
      },
    });
  }

  // ----------------------------
  // Hover effects for delete button
  // ----------------------------
  container.addEventListener("mouseover", (e) => {
    const item = e.target.closest(".playlist-item");
    if (item) item.querySelector(".delete-item-btn").classList.remove("opacity-0");
  });

  container.addEventListener("mouseout", (e) => {
    const item = e.target.closest(".playlist-item");
    if (item) item.querySelector(".delete-item-btn").classList.add("opacity-0");
  });
});
