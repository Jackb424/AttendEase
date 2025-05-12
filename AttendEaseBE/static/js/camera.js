document.addEventListener("DOMContentLoaded", function () {
    function updateStatus(message) {
        let statusElement = document.getElementById("statusMessage");
        if (statusElement) {
            statusElement.innerText = message;
        }
    }

    function fetchStatus() {
        fetch("/get-status")
            .then(response => {
                if (!response.ok) {
                    throw new Error("Status fetch failed");
                }
                return response.json();
            })
            .then(data => {
                updateStatus(data.message);
            })
            .catch((error) => {
                updateStatus("🚫 Could not retrieve camera status. Is the camera connected?");
                console.error("Status check error:", error);
            });
    }

    // ✅ Show immediate loading message
    updateStatus("Initialising camera... Please wait.");

    // ✅ After 8 seconds, start polling actual status
    setTimeout(() => {
        fetchStatus(); // Initial status fetch
        setInterval(fetchStatus, 1000); // Poll every second after
    }, 8000);
});