var socket = io.connect('http://127.0.0.1:5000');

// Listen for satellite changes
document.getElementById('satellite').addEventListener('change', function() {
    var satellite = this.value;
    socket.emit('change_satellite', { 'satellite': satellite });
    updateGasOptions(satellite);
    hideBandOptions();
});

// Listen for gas changes
document.getElementById('gas').addEventListener('change', function() {
    var satellite = document.getElementById('satellite').value;
    var gas = this.value;
    socket.emit('change_gas', { 'satellite': satellite, 'gas': gas });
    updateBandsForGas(gas);
});

// Listen for updated gas options from the server
socket.on('update_gases', function(data) {
    var gasSelect = document.getElementById('gas');
    gasSelect.innerHTML = '';  // Clear existing options
    data.gases.forEach(function(gas) {
        var option = document.createElement('option');
        option.value = gas;
        option.text = gas;
        gasSelect.add(option);
    });
    gasSelect.disabled = false; // Enable the gas select

    // Automatically update bands for the default gas (post form submission)
    var defaultGas = gasSelect.value;
    updateBandsForGas(defaultGas);
});

// Listen for updated band options from the server
socket.on('update_bands', function(data) {
    var bandSelect = document.getElementById('band');
    bandSelect.innerHTML = '';  // Clear existing options
    if (data.bands.length > 0) {
        // Show the band container
        document.getElementById('band-container').style.display = 'block';
        data.bands.forEach(function(band) {
            var option = document.createElement('option');
            option.value = band;
            option.text = band;
            bandSelect.add(option);
        });
    } else {
        hideBandOptions();
    }
});

// Function to update gas options based on selected satellite
function updateGasOptions(satellite) {
    var gasSelect = document.getElementById('gas');
    gasSelect.disabled = true;  // Disable the gas select while updating
    socket.emit('change_satellite', { 'satellite': satellite });
}

// Function to update the band options based on selected gas
function updateBandsForGas(gas) {
    var satellite = document.getElementById('satellite').value;
    socket.emit('change_gas', { 'satellite': satellite, 'gas': gas });
}

// Hide the band options if there's no need to show them
function hideBandOptions() {
    var bandContainer = document.getElementById('band-container');
    bandContainer.style.display = 'none';  // Hide the band container
}

// Run on page load to initialize the default values
function reload() {
    var satellite = document.getElementById('satellite').value;
    var gasSelect = document.getElementById('gas');
    var defaultGas = gasSelect.value;
    
    // Set the selected gas and band based on Flask data
    var selectedGas = document.getElementById("selected_gas").getAttribute("data-value");
    var selectedBand = document.getElementById("selected_band").getAttribute("data-value");
    console.log(selectedGas);
    console.log(selectedBand);

    // Automatically update the gas options when the page loads
    updateGasOptions(satellite);

    // Delay the selection update to ensure options are populated
    setTimeout(function() {
        // Set the selected gas in the dropdown
        gasSelect.value = selectedGas;

        var gasOptions = gasSelect.options;
        for (var i = 0; i < gasOptions.length; i++) {
            if (gasOptions[i].value == selectedGas) {
                gasOptions[i].selected = true;
                break;
            }
        } 
        updateBandsForGas(selectedGas);
        setTimeout( function() {
            // Update bands based on the selected gas

            // Set the selected band in the band dropdown
            var bandSelect = document.getElementById('band');
            var bandOptions = bandSelect.options;
            for (var i = 0; i < bandOptions.length; i++) {
                if (bandOptions[i].value === selectedBand) {
                    bandOptions[i].selected = true;
                    break;
                }
            }
        },300)
    }, 300);  // Adjust the timeout if necessary
};


window.onload = reload();
