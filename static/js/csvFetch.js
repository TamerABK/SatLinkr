function sendCSV(){
    const loader = document.getElementById('loader');
    loader.style.display='block';

    event.preventDefault();

    const form = document.getElementById("mapParams");
    const formData = new FormData(form);

    console.log("Form data being sent:", Array.from(formData.entries()));

    fetch('/launch_csv', {
        method: 'POST',
        body: formData
    }).then(response => response.blob())
    .then(blob => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');

        const satellite = formData.get('satellite');
        const dateStr = formData.get('datetime'); // format attendu : 'YYYY-MM-DDTHH:MM' ou similaire

        // Conversion de la date pour le format souhaité


        // Génération du nom de fichier
        const filename = `${satellite}_${dateStr}.csv`;
        a.href = url;

        a.download = filename;
        a.click();
    })
    .catch(error => {
        console.error('Erreur lors de la génération du CSV:', error);
        alert("Une erreur est survenue lors de la génération du CSV.");
    })
    .finally(() => {
        loader.style.display = 'none';
    });

}
