var socket = io.connect('http://127.0.0.1:5000');


const satelliteSelect = document.getElementById('satellite');
const regionSelect = document.getElementById('existing_region1');
const regionOption = document.getElementById('region_select');
const dateSpan = document.getElementById('date_span');
const deltaSpan = document.getElementById('delta_span');
const  deltaInput = document.getElementById('delta_time');

function handleSatelliteChange() {

  const satellite = satelliteSelect.value;
  socket.emit('change_satellite', { satellite });
  updateGasOptions(satellite);

  const bandContainer = document.getElementById('band-container');
  const flagContainer = document.getElementById('quality-container');
  changeDateSpan(satellite)
  if (satellite === 'OCO2') {
    flagContainer.style.display = "block";
    bandContainer.style.display = "none";
  } else {
    flagContainer.style.display = "none";
    bandContainer.style.display = "block";
  }
}

async function handleExistingRegionChange() {

  const region = regionSelect.value;
  const response = await fetch('/regions', { method: 'GET' });
  const regions = await response.json();
  const details = regions.find(r => r.name === region);
  const satellite = details.satellite;

  socket.emit('change_satellite', { satellite });
  updateGasOptions(satellite);

  const bandContainer = document.getElementById('band-container');
  const flagContainer = document.getElementById('quality-container');
  changeDateSpan(satellite);

  if (satellite === 'OCO2') {

    flagContainer.style.display = "block";
    bandContainer.style.display = "none";
  } else {
    flagContainer.style.display = "none";
    bandContainer.style.display = "block";
  }
}

// Flags to manage listeners
let satelliteListenerAttached = false;
let regionListenerAttached = false;

function enableSatelliteListener() {
  if (!satelliteListenerAttached) {
    satelliteSelect.addEventListener('change', handleSatelliteChange);
    satelliteListenerAttached = true;
    handleSatelliteChange();
  }
  if (regionListenerAttached) {
    regionSelect.removeEventListener('change', handleExistingRegionChange);
    regionListenerAttached = false;
  }
}

function enableRegionListener() {
  if (!regionListenerAttached) {
    regionSelect.addEventListener('change', handleExistingRegionChange);
    regionListenerAttached = true;
    handleExistingRegionChange().then(r => null);
  }
  if (satelliteListenerAttached) {
    satelliteSelect.removeEventListener('change', handleSatelliteChange);
    satelliteListenerAttached = false;
  }
}

// Main controller
regionOption.addEventListener('change', function () {
  if (this.value === 'existing') {
    enableRegionListener();
  } else if (this.value === 'custom') {
    enableSatelliteListener();
  }
});


// Listen for gas changes
document.getElementById('gas').addEventListener('change', async function () {
    let satellite;
    if (regionOption.value === 'existing') {
        const region = regionSelect.value;
        const response = await fetch('/regions', {method: 'GET'});
        const regions = await response.json();
        const details = regions.find(r => r.name === region);
        satellite = details ? details.satellite : null;
    } else {
        satellite = document.getElementById('satellite').value;
    }
    const gas = this.value;
    socket.emit('change_gas', {'satellite': satellite, 'gas': gas});
    updateBandsForGas(satellite, gas);
});

// Listen for updated gas options from the server
socket.on('update_gases', function(data) {
    var gasSelect = document.getElementById('gas');
    gasSelect.innerHTML = '';  // Clear existing options
    data.gases.forEach(function(gas) {
        var option = document.createElement('option');
        option.value = gas;
        option.text = gas.replace(/_/g, " ");
        gasSelect.add(option);
    });
    gasSelect.disabled = false; // Enable the gas select

    // Automatically update bands for the default gas (post form submission)
    var defaultGas = gasSelect.value;

    updateBandsForGas(data.satellite, defaultGas);
});

// Listen for updated band options from the server
socket.on('update_bands', function(data) {


    var bandSelect = document.getElementById('band');
    bandSelect.innerHTML = '';  // Clear existing options
    if (data.bands.length > 0) {
        // Show the band container
        var bandContainer = document.getElementById('band-container');
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
function updateBandsForGas(satellite,gas) {
    socket.emit('change_gas', { 'satellite': satellite, 'gas': gas });
}

function changeDateSpan(satellite) {
    if (satellite === "MODIS_DEEP_BLUE") {
        dateSpan.textContent = "Date (dd/mm/yyyy)";
        deltaSpan.style.display = 'none';
        deltaInput.style.display = 'none';
    } else {
        dateSpan.textContent = "Date (dd/mm/yyyy hh:mm)";
        deltaSpan.style.display = 'block';
        deltaInput.style.display = 'block';
    }
}


// Run on page load to initialize the default values
function reload() {
    enableRegionListener();
    handleExistingRegionChange();
}


window.onload = reload();
