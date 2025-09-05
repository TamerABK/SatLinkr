

async function fetchRegions() {
    const loader = document.getElementById('loader');
    loader.style.display = 'grid';
    document.getElementById('loading-text').textContent = `Loading Region Details...`;

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
            <p><strong>Source:</strong> ${region.satellite}</p>
            <p><strong>Radius:</strong> ${region.radius} km</p>
            <p><strong>Lat:</strong> ${(region.lat).toFixed(4)}  <strong>Lon:</strong> ${(region.lon).toFixed(4)}</p>
            <div class="calendar">
                ${region.available_dates.map(date => `<span class="date-cell">${date}</span>`).join('')}
            </div>
        `;
        if (region.satellite !== "TCCON") {
            const op = document.createElement('option')
            op.innerHTML = `<option value="${region.name}"> ${region.name}</option>`
            selectList.forEach(selectElement => {
                selectElement.appendChild(op.cloneNode(true));
            });
        }

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
    loader.style.display = 'None';
    document.getElementById('loading-text').textContent = ``;
}

// Load views when page loads
window.addEventListener('DOMContentLoaded',  fetchRegions);

