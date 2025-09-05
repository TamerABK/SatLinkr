document.getElementById("fetchParams").addEventListener("submit", function(event) {
    event.preventDefault();
    const loader = document.getElementById('loader');
    loader.style.display='grid';

    const formData = new FormData(this);

    fetch("/fetchData", {
        method: "POST",
        body: formData
    })
    .catch(error => {
        console.error("Error:", error);
    }).finally(() => {
        console.log('Fetch Done')
        document.getElementById('loading-text').textContent = ``;
        loader.style.display = 'none';
        window.location.reload();
    });
});


socket.on('fetch_progress', function(data) {
    document.getElementById('loading-text').textContent = `Fetching progress : ${data.current} / ${data.total}`;
});