async function startCompression() {
    const files = document.getElementById("videos").files;
    const codec = document.getElementById("codec").value;

    if (!files.length) {
        alert("Select videos");
        return;
    }

    const form = new FormData();
    for (const f of files) form.append("videos", f);
    form.append("codec", codec);

    const res = await fetch("/start", { method: "POST", body: form });
    const { task_id } = await res.json();

    poll(task_id);
}

async function poll(id) {
    const interval = setInterval(async () => {
        const res = await fetch(`/status/${id}`);
        const data = await res.json();

        if (data.status === "processing") {
            document.getElementById("progress").innerText =
                `Compressing ${data.file} (${data.current}/${data.total}) – ${data.percent}%`;
        }

        if (data.status === "done") {
            clearInterval(interval);
            document.getElementById("progress").innerText = "Done!";
            document.getElementById("downloads").innerHTML =
                data.files.map(f => `<a href="/download/${f}">${f}</a>`).join("<br>");
        }
    }, 1000);
}
