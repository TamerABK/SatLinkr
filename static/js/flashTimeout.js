function hideFlashMessage() {
    var flash = document.getElementById('flash-message');
    if (flash) {
        setTimeout(function() {
            flash.style.display = 'none';
        }, 5000); // Hide after 5 seconds
    }
}

function startMessageTimer() {
    setInterval(function() {
        hideFlashMessage();
    }, 2000); // Run every 2 seconds
}

window.onload= startMessageTimer()