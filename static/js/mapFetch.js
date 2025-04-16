function attachMapListener() {
    window.map=null;
    const mapContainer = document.getElementById("map");
    if (!mapContainer) {
        console.error("Map container not found.");
        return;
    }

    const iframe = mapContainer.querySelector("iframe");
    if (!iframe) {
        console.error("No iframe found inside #map.");
        return;
    }

    iframe.addEventListener("load", () => {
        try {
            const iframeWindow = iframe.contentWindow;

            setTimeout(() => {
                // Dynamically find the Leaflet map object
                
                for (let key in iframeWindow) {
                    if (
                        iframeWindow[key] &&
                        typeof iframeWindow[key] === "object" &&
                        typeof iframeWindow[key].getCenter === "function" &&
                        typeof iframeWindow[key].getZoom === "function"
                    ) {
                        window.map = iframeWindow[key];
                        console.log("Found map variable:", key);
                        break;
                    }
                }

                if (!window.map) {
                    console.error("Leaflet map not found in iframe.");
                    return;
                }


            }, 200);
        } catch (e) {
            console.error("Error accessing map in iframe:", e);
        }
    });
}

attachMapListener();


function shiftMapNorthByPercent(map, prc) {
    // Get current center and zoom
    const center = map.getCenter();
    const zoom = map.getZoom();

    // Get pixel coordinates of the current center
    const centerPoint = map.project(center, zoom);

    // Compute 20% of the current map's pixel height
    const heightInPixels = map.getSize().y;
    const shiftPixels = heightInPixels * (prc/100);

    // Subtract pixels from Y to go north (Y increases downward)
    const newCenterPoint = centerPoint.subtract([0, shiftPixels]);

    // Convert pixel point back to LatLng
    const newCenter = map.unproject(newCenterPoint, zoom);

    return newCenter;
}






function sendMapHTML(){
    const loader = document.getElementById('loader');
    loader.style.display='block';

    
        const center= shiftMapNorthByPercent(window.map,19);
        const zoom= window.map.getZoom();


        const mapHTML=  document.getElementById('map');
        let html = mapHTML.innerHTML;
        const width=  window.innerWidth;
        const height= window.innerHeight;

        // Replace old map init with updated one
        const updatedHtml = html.replace(/center:\s*\[[^,\]]+,\s*[^,\]]+\]/, `center: [${center.lat}, ${center.lng}]`)
                                .replace(/&quot;zoom&quot;:\s*\d+/, `&quot;zoom&quot;: ${zoom}`)
                                .replace(/&quot;zoomControl&quot;:\s*(true|false)/, `&quot;zoomControl&quot;: false`);

        // Send to Flask as before
        fetch('/render_map_png', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                html: updatedHtml,
                width: width,
                height: height
            })
        })
        .then(response => response.blob())
        .then(blob => {
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `map_view_${center.lat.toFixed(4)}_${center.lng.toFixed(4)}.png`;
            a.click();
        })
        .catch(error => {
            console.error('Error generating PNG:', error);
            alert("Something went wrong while generating the image.");
        })
        .finally(() => {
            loader.style.display = 'none';
        });
    
}
