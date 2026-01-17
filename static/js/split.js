const videoInput = document.getElementById("video");
const videoPlayer = document.getElementById("player");
const splitButton = document.getElementById("split-button");
const resultDiv = document.getElementById("split-result");

const startTimeSpan = document.getElementById("start-time");
const endTimeSpan = document.getElementById("end-time");
const durationTimeSpan = document.getElementById("duration-time");

const sliderContainer = document.getElementById("range-slider");
let slider;
let videoDuration = 0;
let currentFile = null;

function formatTime(seconds) {
    seconds = Math.max(0, Math.floor(seconds));
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s.toString().padStart(2, "0")}`;
}

videoInput.addEventListener("change", function () {
    const file = this.files[0];
    if (!file) return;

    removeBtn.style.display = "flex";

    currentFile = file;
    const url = URL.createObjectURL(file);
    videoPlayer.src = url;
    videoPlayer.load();

    videoPlayer.onloadedmetadata = () => {
        videoDuration = videoPlayer.duration || 0;

        if (slider) slider.destroy();

        slider = noUiSlider.create(sliderContainer, {
            start: [0, videoDuration],
            connect: true,
            range: { min: 0, max: videoDuration },
            step: 0.1
        });

        // 🔥 Update preview when slider moves
        slider.on("update", function (values, handle) {
            const start = parseFloat(values[0]);
            const end = parseFloat(values[1]);
            const duration = Math.max(0, end - start);

            startTimeSpan.textContent = formatTime(start);
            endTimeSpan.textContent = formatTime(end);
            durationTimeSpan.textContent = formatTime(duration);

            // 🔥 Move video preview to the handle being moved
            if (handle === 0) {
                videoPlayer.currentTime = start;
            } else {
                videoPlayer.currentTime = end;
            }
        });
    };
});

splitButton.addEventListener("click", async function () {
    if (!currentFile || !slider) {
        alert("Please upload a video and select a segment first.");
        return;
    }

    const values = slider.get();
    const start = parseFloat(values[0]);
    const end = parseFloat(values[1]);

    if (end <= start) {
        alert("End time must be greater than start time.");
        return;
    }

    const formData = new FormData();
    formData.append("video", currentFile);
    formData.append("start", start);
    formData.append("end", end);

    splitButton.disabled = true;
    splitButton.textContent = "Splitting...";
    resultDiv.innerHTML = "";

    try {
        const res = await fetch("/split-video", {
            method: "POST",
            body: formData
        });

        const data = await res.json();

        if (!res.ok || data.error) {
            alert(data.error || "Failed to split video.");
        } else if (data.status === "done") {
            const link = document.createElement("a");
            link.href = `/download-split/${data.file}`;
            link.textContent = "Download split video";
            link.className = "download-link";
            link.download = data.file;

            resultDiv.innerHTML = "<h4>Split Result:</h4>";
            resultDiv.appendChild(link);
        }
    } catch (err) {
        console.error("Error splitting video:", err);
        alert("An error occurred while splitting the video.");
    } finally {
        splitButton.disabled = false;
        splitButton.textContent = "Split Video";
    }
});

// Remove/reset logic
const removeBtn = document.getElementById("remove-video");

removeBtn.addEventListener("click", () => {
    videoInput.value = "";
    videoPlayer.src = "";
    videoPlayer.load();

    if (slider) {
        slider.destroy();
        slider = null;
    }

    startTimeSpan.textContent = "0:00";
    endTimeSpan.textContent = "0:00";
    durationTimeSpan.textContent = "0:00";

    resultDiv.innerHTML = "";
    removeBtn.style.display = "none";
    currentFile = null;
});
