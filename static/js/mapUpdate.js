document.getElementById("mapParams").addEventListener("submit", function(event) {
    const loader = document.getElementById('loader');
    loader.style.display='grid';
    document.getElementById('loading-text').textContent = ``;
    event.preventDefault(); // prevent full page reload

    const formData = new FormData(this);
    console.log(formData)

    fetch("/update_map", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);  // you can make this prettier
        } else {
            document.getElementById("map").innerHTML = data.map_html;
        }
    })
    .catch(error => {
        console.error("Error:", error);
    }).finally(() => {
        attachMapListener();

        loader.style.display = 'none';
    });
});