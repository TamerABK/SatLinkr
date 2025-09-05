const form = document.getElementById('tcconUploadForm');
form.addEventListener('submit', async function(e) {
    const loader = document.getElementById('loader');
    loader.style.display = 'grid';
    document.getElementById('loading-text').textContent = `Uploading...`;

    e.preventDefault();
    const files = document.getElementById('tcconFile').files;
    const station_name = document.getElementById('station_name').value;
    const total= files.length
    let nb_uploaded = 0
    for (const file of files) {
        nb_uploaded++;
        document.getElementById('loading-text').textContent = `Uploading ${nb_uploaded}/${total}`;
        const formData = new FormData();
        formData.append('tcconFile', file);
        formData.append('station_name', station_name);
        try {
            const response = await fetch('/upload_tccon', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            console.log('Upload terminé:', file.name, data);
        } catch (error) {
            console.error('Erreur upload:', file.name, error);
        }
    }

    loader.style.display = 'none';
    document.getElementById('loading-text').textContent = ``;
    document.getElementById('tcconFile').value = '';
});