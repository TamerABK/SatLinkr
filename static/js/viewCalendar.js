

async function fetchRegions() {
    const response = await fetch('/regions', {method: 'GET'});
    const regions = await response.json();

    const option = document.getElementsByClassName('existing_region')
    const container = document.querySelector('.card-container');
    container.innerHTML = ''; // Clear existing cards

    const selectList = Array.from(option);
    selectList.forEach(selectElement => {
        selectElement.innerHTML=''
    })


    for (const region of regions) {
        const card = document.createElement('div');
        card.className = 'region-card';
        card.innerHTML = `
            <h3>${region.name}</h3>
            <p><strong>Satellite:</strong> ${region.satellite}</p>
            <p><strong>Radius:</strong> ${region.radius} km</p>
            <p><strong>Lat:</strong> ${region.lat}  <strong>Lon:</strong> ${region.lon}</p>
            <div class="calendar">
                ${region.available_dates.map(date => `<span class="date-cell">${date}</span>`).join('')}
            </div>
        `;

        const op = document.createElement('option')
        op.innerHTML = `<option value="${region.name}"> ${region.name}</option>`
        selectList.forEach(selectElement => {
          selectElement.appendChild(op.cloneNode(true));
        });

        container.appendChild(card);
    }

    if ($('.card-container').hasClass('slick-initialized')) {
        $('.card-container').slick('unslick');
    }

    // Re-initialize slick
    $('.card-container').slick({
        slidesToShow: 1,
        slidesToScroll: 1,
        arrows:false,
        dots:true,
        infinite:true
    });
}

// Load views when page loads
window.addEventListener('DOMContentLoaded',  fetchRegions);

