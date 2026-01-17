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
        <div class="file-status" id="status-${i}">Pending...</div>
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
      body: formData,
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
          const originalNameMatch = currentFile.match(
            /^(.+)_[a-f0-9]{8}\.(mp4|mov|avi|mkv|webm)$/i
          );
          const displayName = originalNameMatch
            ? `${originalNameMatch[1]}.${originalNameMatch[2]}`
            : currentFile;

          // Update all progress bars
          for (let i = 0; i < status.total; i++) {
            const progressBar = document.getElementById(`progress-${i}`);
            const percentSpan = document.getElementById(`percent-${i}`);
            const statusSpan = document.getElementById(`status-${i}`);

            if (i < status.current - 1) {
              // Files already processed
              progressBar.value = 100;
              percentSpan.innerText = "100% - Done";
              statusSpan.innerText = "Completed!";
            } else if (i === status.current - 1) {
              // Current file being processed
              progressBar.value = status.percent;
              percentSpan.innerText = `${status.percent}% - Processing`;

              // When this one reaches 100%, mark as completed
              if (status.percent >= 100) {
                statusSpan.innerText = "Completed!";
              } else {
                // Still processing
                statusSpan.innerText = "Processing...";
              }
            } else {
              // Files not yet processed
              progressBar.value = 0;
              percentSpan.innerText = "0% - Waiting";
              // Keep them as Pending... until they start
              statusSpan.innerText = "Pending...";
            }
          }
        }
      } else if (status.status === "done") {
        clearInterval(interval);

        // Set all progress bars to 100%
        for (let i = 0; i < status.total; i++) {
          const progressBar = document.getElementById(`progress-${i}`);
          const percentSpan = document.getElementById(`percent-${i}`);
          const statusSpan = document.getElementById(`status-${i}`);

          progressBar.value = 100;
          percentSpan.innerText = "100% - Done";
          statusSpan.innerText = "Completed!";
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


/* ===============================
   Hamburger Menu & Mobile Navigation
   =============================== */

document.addEventListener("DOMContentLoaded", function () {
  const hamburger = document.getElementById("hamburger");
  const navLinks = document.querySelector(".nav-links");
  const dropdowns = document.querySelectorAll(".nav-links li.dropdown");

  // Hamburger menu toggle
  if (hamburger) {
    hamburger.addEventListener("click", function (e) {
      e.stopPropagation();
      hamburger.classList.toggle("active");
      navLinks.classList.toggle("active");
    });
  }

  // Close menu when clicking outside
  document.addEventListener("click", function (e) {
    if (window.innerWidth <= 768) {
      if (!navLinks.contains(e.target) && !hamburger.contains(e.target)) {
        navLinks.classList.remove("active");
        hamburger.classList.remove("active");
        // Close all dropdowns
        dropdowns.forEach((dropdown) => {
          dropdown.classList.remove("active");
        });
      }
    }
  });

  // Dropdown toggle for mobile
  dropdowns.forEach((dropdown) => {
    const link = dropdown.querySelector("a");

    link.addEventListener("click", function (e) {
      if (window.innerWidth <= 768) {
        e.preventDefault();

        const isActive = dropdown.classList.contains("active");

        // Close all other dropdowns
        dropdowns.forEach((other) => {
          if (other !== dropdown) {
            other.classList.remove("active");
          }
        });

        // Toggle this dropdown
        if (!isActive) {
          dropdown.classList.add("active");
        } else {
          dropdown.classList.remove("active");
        }

        e.stopPropagation();
      }
    });
  });

  // Prevent menu close when clicking inside dropdown menu
  document.querySelectorAll(".dropdown-menu").forEach((menu) => {
    menu.addEventListener("click", function (e) {
      e.stopPropagation();
    });
  });

  // Close menu on window resize if switching to desktop
  window.addEventListener("resize", function () {
    if (window.innerWidth > 768) {
      navLinks.classList.remove("active");
      hamburger.classList.remove("active");
      dropdowns.forEach((dropdown) => {
        dropdown.classList.remove("active");
      });
    }
  });
});
