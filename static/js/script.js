document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('downloadForm');
    const downloadButton = document.getElementById('downloadButton');
    const progressDiv = document.getElementById('progress');
    const progressText = document.querySelector('.progress-text');
    const messageDiv = document.getElementById('messageDiv');
    const hideParagraph = document.getElementById('hideParagraph');
    const downloadLink = document.getElementById('downloadLink');
    const noStuffDiv = document.getElementById('noStuffDiv');

    form.addEventListener('submit', async (event) => {
        downloadButton.disabled = true;
        progressDiv.style.display = 'flex';
        progressDiv.style.justifyContent = 'center';

        const response = await fetch('/get_id', {
            method: 'GET',
        });

        if (response.ok) {
            const jsonResponse = await response.json();
            const session_id = jsonResponse.session_id;

            // Polling for progress updates
            const intervalId = setInterval(async () => {
                const progressResponse = await fetch(`/download_progress/${session_id}`);
                if (progressResponse.ok) {
                    const progress = await progressResponse.json();
                    if (progress.path_exists === 'True') {
                        if (progress.total_items) {
                            progressText.textContent = `${progress.total_items} items`;
                        }
                    } else {
                        clearInterval(intervalId); // Stop polling
                        progressDiv.style.display = 'none';
                        
                        // Show appropriate message
                        if (progress.total_items > 0) {
                            messageDiv.style.display = 'block';
                            hideParagraph.textContent = 'Loading done. Click below to download.';
                            downloadLink.href = `./downloads/${session_id}.zip`;
                            downloadLink.textContent = 'Download';
                        } else {
                            noStuffDiv.style.display = 'block';
                        }
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
