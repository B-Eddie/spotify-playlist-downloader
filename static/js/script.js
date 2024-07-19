document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('downloadForm');
    const downloadButton = document.getElementById('downloadButton');
    const progressDiv = document.getElementById('progress');
    const progressText = document.querySelector('.progress-text');

    const messageDiv = document.getElementById('messageDiv');
    const downloadLink = document.getElementById('downloadLink');
    const noStuffDiv = document.getElementById('noStuffDiv');
    const downloadButtonJS = document.getElementById('button');

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
                            document.querySelector('title').textContent = `(${progress.total_items}) Spotify Downloader`;
                        }
                    } else {
                        clearInterval(intervalId); // Stop polling
                        progressDiv.style.display = 'none';
                        document.querySelector('title').textContent = '✅ Spotify Downloader';

                        messageDiv.style.display = 'flex';
                        downloadButtonJS.onclick = () => {
                            window.location.href = '/finish/' + session_id;
                        };
                        downloadLink.href = `./download/${session_id}`;
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
