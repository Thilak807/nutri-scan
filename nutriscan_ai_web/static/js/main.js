(function () {
    const healthBar = document.querySelector(".progress-bar[data-score]");
    if (healthBar) {
        const score = Number(healthBar.getAttribute("data-score") || 0);
        healthBar.style.width = `${Math.max(0, Math.min(100, score))}%`;
    }

    const dropzone = document.getElementById("dropzone");
    const fileInput = document.getElementById("food_image");
    const fileLabel = document.getElementById("fileLabel");

    if (!dropzone || !fileInput || !fileLabel) {
        return;
    }

    const updateLabel = (file) => {
        fileLabel.textContent = file ? file.name : "No image selected";
    };

    dropzone.addEventListener("click", () => fileInput.click());

    fileInput.addEventListener("change", () => {
        updateLabel(fileInput.files[0]);
    });

    ["dragenter", "dragover"].forEach((eventName) => {
        dropzone.addEventListener(eventName, (event) => {
            event.preventDefault();
            dropzone.classList.add("active");
        });
    });

    ["dragleave", "drop"].forEach((eventName) => {
        dropzone.addEventListener(eventName, (event) => {
            event.preventDefault();
            dropzone.classList.remove("active");
        });
    });

    dropzone.addEventListener("drop", (event) => {
        const files = event.dataTransfer.files;
        if (!files || !files.length) {
            return;
        }
        fileInput.files = files;
        updateLabel(files[0]);
    });
})();
