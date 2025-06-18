function sendCSV(){
    const loader = document.getElementById('loader');
    loader.style.display = 'block';

    event.preventDefault();

    const form = document.getElementById("mapParams");
    const formData = new FormData(form);

    fetch('/launch_csv', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Erreur réseau');
        }
        const filename = response.headers.get('Content-Disposition')
            ?.split('filename=')[1]
            ?.replace(/['"]/g, '');
        return response.blob().then(blob => ({
            blob: blob,
            filename: filename
        }));
    })
    .then(({blob, filename}) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename || 'data.csv';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();
    })
    .catch(error => {
        console.error('Erreur lors de la génération du CSV:', error);
        alert("Une erreur est survenue lors de la génération du CSV.");
    })
    .finally(() => {
        loader.style.display = 'none';
    });
}
