// Function to update the displayed value of the slider
function updateRadiusValue() {
    var radiusSlider = document.getElementById('radius');
    var radiusValue = document.getElementById('radius-value');
    radiusValue.textContent = radiusSlider.value; // Update the span with the current slider value
}

// Call the function on page load to initialize the value display
window.onload = function() {
    updateRadiusValue(); // To show the initial value on page load
};