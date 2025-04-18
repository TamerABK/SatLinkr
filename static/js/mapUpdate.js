document.getElementById("mapParams").addEventListener("submit", function(event) {
    const loader = document.getElementById('loader');
    loader.style.display='block';
    event.preventDefault(); // prevent full page reload

    const formData = new FormData(this);

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