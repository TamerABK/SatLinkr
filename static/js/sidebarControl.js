function showSidebar(n) {
    const sidebar1 = document.getElementById('mapBar');
    const sidebar2 = document.getElementById('fetchBar');
    const toggle1 = document.getElementById('toggle1');
    const toggle2 = document.getElementById('toggle2');

    if (n === 1) {
        sidebar1.style.display = "block";
        sidebar2.style.display = "none";
        toggle1.classList.add("active");
        toggle2.classList.remove("active");
    } else {
        sidebar1.style.display = "none";
        sidebar2.style.display = "block";
        toggle1.classList.remove("active");
        toggle2.classList.add("active");
    }
}