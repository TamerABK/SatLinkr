window.onload = function() {
    const mapContainer = document.querySelector('.map-container');
    const iframe = mapContainer.querySelector('iframe');
    if (iframe) {
        iframe.style.height = '100%';
    }
};