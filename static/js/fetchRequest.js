document.getElementById("fetchParams").addEventListener("submit", function(event) {
    event.preventDefault();
    const loader = document.getElementById('loader');
    loader.style.display='block';

    const formData = new FormData(this);

    fetch("/fetchData", {
        method: "POST",
        body: formData
    })
    .catch(error => {
        console.error("Error:", error);
    }).finally(() => {
        console.log('Fetch Done')
        loader.style.display = 'none';
        window.location.reload();
    });
});