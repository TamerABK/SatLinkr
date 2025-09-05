function showSidebar(n) {
    const sidebar1 = document.getElementById('mapBar');
    const sidebar2 = document.getElementById('fetchBar');
    const sidebar3 = document.getElementById('tcconBar');
    const toggle1 = document.getElementById('toggle1');
    const toggle2 = document.getElementById('toggle2');
    const toggle3 = document.getElementById('toggle3');

    if (n === 1) {
        sidebar1.style.display = "block";
        sidebar2.style.display = "none";
        sidebar3.style.display = "none";
        toggle1.classList.add("active");
        toggle2.classList.remove("active");
        toggle3.classList.remove("active");
    } else if (n === 2) {
        sidebar1.style.display = "none";
        sidebar2.style.display = "block";
        sidebar3.style.display = "none";
        toggle1.classList.remove("active");
        toggle2.classList.add("active");
        toggle3.classList.remove("active");
    }else {
        sidebar1.style.display = "none";
        sidebar2.style.display = "none";
        sidebar3.style.display = "block";
        toggle1.classList.remove("active");
        toggle2.classList.remove("active");
        toggle3.classList.add("active");
    }
}