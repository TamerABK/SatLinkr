function toggleRegionFields() {
        const option = document.getElementById('region_option').value;
        document.getElementById('existing_region_div').style.display = option === 'existing' ? 'block' : 'none';
        document.getElementById('new_region_div').style.display = option === 'new' ? 'block' : 'none';

        // Required field toggling (optional)
        document.getElementById('region_name').required = option === 'new';
        document.getElementById('latitude_fetch').required = option === 'new';
        document.getElementById('longitude_fetch').required = option === 'new';
    }

function toggleRegionSelect(){
        const option = document.getElementById('region_select').value;

        document.getElementById('selectRegion').style.display = option === 'existing' ? 'block' : 'none';
        document.getElementById('customRegion').style.display = option === 'custom' ? 'block' : 'none';

        // Required field toggling (optional)
        document.getElementById('latitude').required = option === 'custom';
        document.getElementById('longitude').required = option === 'custom';
        document.getElementById('radius').required = option === 'custom';


}

  window.onload = function () {
    toggleRegionSelect();
    toggleRegionFields();
  };