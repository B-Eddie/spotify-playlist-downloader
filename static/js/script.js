document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('downloadForm');
    const downloadButton = document.getElementById('downloadButton');
    const progressDiv = document.getElementById('progress');
    const progressText = document.querySelector('.progress-text');

    form.addEventListener('submit', async (event) => {
        console.log("Form submitted");
        event.preventDefault();
        downloadButton.disabled = true;
        progressDiv.style.display = 'flex';
        progressDiv.style.justifyContent = 'center';

        const formData = new FormData(form);
        console.log(formData);
        const response = await fetch('/download', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const jsonResponse = await response.json();
            const session_id = jsonResponse.session_id;

            // Polling for progress updates
            const intervalId = setInterval(async () => {
                console.log('Polling for progress updates');
                const progressResponse = await fetch(`/download_progress/${session_id}`);
                if (progressResponse.ok) {
                    const progress = await progressResponse.json();
                    progressText.textContent = `${progress.percentage}%`;

                    if (progress.percentage === 100) {
                        clearInterval(intervalId);
                        window.location.href = `/download_zip/${session_id}`;
                    }
                }
            }, 1000);
        } else {
            alert('Error downloading file.');
            downloadButton.disabled = false;
            progressDiv.style.display = 'none';
        }
    });
});
