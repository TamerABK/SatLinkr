var socket = io.connect('http://127.0.0.1:5000');



document.getElementById('region_option').addEventListener('change')
// Listen for satellite changes
document.getElementById('satellite').addEventListener('change', function() {
    const satellite = this.value;
    socket.emit('change_satellite', { 'satellite': satellite });
    updateGasOptions(satellite);
    var bandContainer = document.getElementById('band-container');

    var flagContainer = document.getElementById('quality-container');
    if (satellite === 'OCO2'){
        flagContainer.style.display = "block";
        bandContainer.style.display = 'none';
    } else{
        flagContainer.style.display = "none";
        bandContainer.style.display = 'block';
    }

});

document.getElementById('existing_region1').addEventListener('change', async function () {

    const region = this.value;

    const response = await fetch('/regions', {method: 'GET'});
    const regions = await response.json();

    const details = regions.find(r => r.name === region);
    const satellite = details.satellite;
    socket.emit('change_satellite', { 'satellite': satellite });
    updateGasOptions(satellite);
    var bandContainer = document.getElementById('band-container');

    var flagContainer = document.getElementById('quality-container');
    if (satellite === 'OCO2'){
        console.log('IN')
        flagContainer.style.display = "block";
        bandContainer.style.display = 'none';
    } else{
        flagContainer.style.display = "none";
        bandContainer.style.display = 'block';
    }


});

// Listen for gas changes
document.getElementById('gas').addEventListener('change', function() {
    const satellite = document.getElementById('satellite').value;
    const gas = this.value;
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
        var bandContainer = document.getElementById('band-container');
        bandContainer.style.display='block'
        data.bands.forEach(function(band) {
            var option = document.createElement('option');
            option.value = band;
            option.text = band;
            bandSelect.add(option);
        });
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
