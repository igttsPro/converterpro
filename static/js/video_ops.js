// static/js/video_ops.js
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("bgForm");
    const resultDiv = document.getElementById("bgResult");
    const videoFileInput = document.getElementById("videoFile");
    const videoPreview = document.getElementById("videoPreview");
    const removeBtn = document.getElementById("remove-video");
    const thresholdSlider = document.getElementById("thresholdSlider");
    const thresholdValue = document.getElementById("thresholdValue");

    // Video preview
    videoFileInput.addEventListener("change", (e) => {
        const file = e.target.files[0];
        if (file) {
            const url = URL.createObjectURL(file);
            videoPreview.src = url;
            videoPreview.style.display = "block";
            videoPreview.load();
            document.getElementById("videoMessage").style.display = "none";
            const ph = document.getElementById("videoPlaceholder");
            if (ph) ph.style.display = "none";
            if (removeBtn) removeBtn.style.display = "flex";
        } else {
            videoPreview.src = "";
            videoPreview.style.display = "block";
            document.getElementById("videoMessage").style.display = "block";
            const ph = document.getElementById("videoPlaceholder");
            if (ph) ph.style.display = "block";
            if (removeBtn) removeBtn.style.display = "none";
        }
    });

    // Threshold slider
    thresholdSlider.addEventListener("input", (e) => {
        thresholdValue.textContent = e.target.value;
    });

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        resultDiv.textContent = "Processing...";

        const formData = new FormData(form);

        const removeVoiceCheckbox = form.querySelector('input[name="remove_voice"]');
        if (removeVoiceCheckbox && removeVoiceCheckbox.checked) {
            formData.set("remove_voice", "true");
        } else {
            formData.delete("remove_voice");
        }

        try {
            const res = await fetch("/api/video-ops/process", {
                method: "POST",
                body: formData
            });

            const data = await res.json();

            if (!res.ok || data.error) {
                console.error("API ERROR:", data.error || res.statusText);
                resultDiv.textContent = "Error: " + (data.error || "Unknown error");
                return;
            }

            const downloadUrl = data.download_url || `/download/${encodeURIComponent(data.file)}`;

            resultDiv.innerHTML = `
                <p>Done!</p>
                <a href="${downloadUrl}" download>Download processed video</a>
            `;
        } catch (err) {
            console.error("REQUEST ERROR:", err);
            resultDiv.textContent = "Request failed. Check console.";
        }
    });

    // Remove/reset logic for uploaded video
    if (removeBtn) {
        removeBtn.addEventListener("click", () => {
            videoFileInput.value = "";
            videoPreview.src = "";
            videoPreview.load();

            document.getElementById("videoMessage").style.display = "block";
            const ph = document.getElementById("videoPlaceholder");
            if (ph) ph.style.display = "block";

            removeBtn.style.display = "none";
        });
    }
});
