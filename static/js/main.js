async function startCompression() {
    const files = document.getElementById("videos").files;
    const codec = document.getElementById("codec").value;

    if (!files.length) {
        alert("Please select at least one video.");
        return;
    }

    // Clear previous content
    document.getElementById("progress-container").innerHTML = "";
    document.getElementById("downloads").innerHTML = "";

    // Create progress bars for each file
    const fileProgress = {};
    for (let i = 0; i < files.length; i++) {
        const div = document.createElement("div");
        div.className = "file-progress";
        div.innerHTML = `
            <strong>${files[i].name}</strong>
            <div class="file-status">Pending...</div>
            <progress id="progress-${i}" value="0" max="100"></progress>
            <span id="percent-${i}">0%</span>
        `;
        document.getElementById("progress-container").appendChild(div);
        fileProgress[files[i].name] = i;
    }

    // Upload files via FormData
    const formData = new FormData();
    for (let file of files) {
        formData.append("videos", file);
    }
    formData.append("codec", codec);

    // Start compression
    try {
        const response = await fetch("/start", {
            method: "POST",
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || "Failed to start compression");
        }
        
        const data = await response.json();
        const taskId = data.task_id;
        
        // Start polling for progress
        pollProgress(taskId, fileProgress);
        
    } catch (error) {
        alert("Error: " + error.message);
    }
}

async function pollProgress(taskId, fileProgress) {
    const interval = setInterval(async () => {
        try {
            const res = await fetch(`/status/${taskId}`);
            const status = await res.json();
            
            if (status.status === "processing") {
                // Find which file is being processed
                const currentFile = status.file;
                
                if (currentFile) {
                    // Find the original filename (remove the unique ID)
                    const originalNameMatch = currentFile.match(/^(.+)_[a-f0-9]{8}\.(mp4|mov|avi|mkv|webm)$/i);
                    const displayName = originalNameMatch ? originalNameMatch[1] + originalNameMatch[2] : currentFile;
                    
                    // Update all progress bars
                    for (let i = 0; i < status.total; i++) {
                        const progressBar = document.getElementById(`progress-${i}`);
                        const percentSpan = document.getElementById(`percent-${i}`);
                        
                        if (i < status.current - 1) {
                            // Files already processed
                            progressBar.value = 100;
                            percentSpan.innerText = "100% - Done";
                        } else if (i === status.current - 1) {
                            // Current file being processed
                            progressBar.value = status.percent;
                            percentSpan.innerText = `${status.percent}% - Processing`;
                        } else {
                            // Files not yet processed
                            progressBar.value = 0;
                            percentSpan.innerText = "0% - Waiting";
                        }
                    }
                }
                
            } else if (status.status === "done") {
                clearInterval(interval);
                
                // Set all progress bars to 100%
                for (let i = 0; i < status.total; i++) {
                    const progressBar = document.getElementById(`progress-${i}`);
                    const percentSpan = document.getElementById(`percent-${i}`);
                    progressBar.value = 100;
                    percentSpan.innerText = "100% - Done";
                }
                
                // Show download links
                const downloadsDiv = document.getElementById("downloads");
                downloadsDiv.innerHTML = "<h4>Download Links:</h4>";
                
                for (let file of status.files) {
                    const a = document.createElement("a");
                    a.href = `/download/${file}`;
                    a.innerText = `Download: ${file}`;
                    a.className = "download-link";
                    a.download = file;
                    downloadsDiv.appendChild(a);
                    downloadsDiv.appendChild(document.createElement("br"));
                }
                
            } else if (status.status === "error") {
                clearInterval(interval);
                alert("Compression failed: " + (status.error || "Unknown error"));
            }
            
        } catch (error) {
            console.error("Error polling status:", error);
        }
    }, 1000); // Poll every second
}