const fetchBtn = document.getElementById("fetch-formats");
const urlInput = document.getElementById("video-url");
const videoInfo = document.getElementById("video-info");
const thumbnail = document.getElementById("thumbnail");
const titleEl = document.getElementById("video-title");
const formatsList = document.getElementById("formats-list");
const resultDiv = document.getElementById("download-result");

let selectedFormat = null;
let currentURL = null;


fetchBtn.addEventListener("click", async () => {
    const url = urlInput.value.trim();
    if (!url) {
        alert("Please paste a video link.");
        return;
    }

    fetchBtn.disabled = true;
    fetchBtn.textContent = "Fetching formats...";

    formatsList.innerHTML = "";
    resultDiv.innerHTML = "";
    videoInfo.style.display = "none";

    try {
        const res = await fetch("/fetch-formats", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url })
        });

        const data = await res.json();

        if (data.error) {
            alert(data.error);
            return;
        }

        currentURL = url;

        // Show thumbnail + title
        videoInfo.style.display = "flex";
        thumbnail.src = data.thumbnail;
        titleEl.textContent = data.title;

        // Show formats
        formatsList.innerHTML = "<h4>Select Format:</h4>";

        // In the fetchBtn click handler, update how formats are displayed
        if (Array.isArray(data.formats)) {
            data.formats.forEach(f => {
                const btn = document.createElement("button");
                
                // NEW: Display format, resolution, and file size
                const sizeDisplay = f.size_str || "Unknown size";
                btn.textContent = `${f.display_resolution || f.resolution} • ${f.ext.toUpperCase()} • ${sizeDisplay}`;
                
                btn.style.display = "flex";
                btn.style.margin = "8px 0";
                btn.style.justifyContent = "space-between";
                btn.style.padding = "10px 15px";
                btn.style.width = "100%";

                // Add hover effect
                btn.onmouseover = () => {
                    btn.style.backgroundColor = "#e0e0e0";
                };
                btn.onmouseout = () => {
                    btn.style.backgroundColor = "";
                };

                btn.addEventListener("click", () => {
                    selectedFormat = f.format_id;
                    downloadSelected();
                });

                formatsList.appendChild(btn);
            });
        } else {
            formatsList.innerHTML += "<p>No formats available.</p>";
        }
    } catch (err) {
        alert("Failed to fetch formats.");
    }
});


async function downloadSelected() {
    if (!selectedFormat || !currentURL) {
        alert("Please select a format.");
        return;
    }

    resultDiv.innerHTML = "Downloading...";

    try {
        const res = await fetch("/download-video", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                url: currentURL,
                format_id: selectedFormat
            })
        });

        const data = await res.json();

        if (data.error) {
            alert(data.error);
            return;
        }

        const link = document.createElement("a");
        link.href = `/download-file/${data.file}`;
        link.textContent = "Click here to download";
        link.className = "download-link";
        link.download = data.file;

        resultDiv.innerHTML = "";
        resultDiv.appendChild(link);

    } catch (err) {
        alert("Failed to download video.");
    }
}
