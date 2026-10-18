document.addEventListener("DOMContentLoaded", function () {
    const slides = document.querySelectorAll(".family-slide");
    const slideBadge = document.getElementById("slideBadge");
    const slideTitle = document.getElementById("slideTitle");
    const slideSubtext = document.getElementById("slideSubtext");
    
    let currentIndex = 0;
    const totalSlides = slides.length;

    function showNextFamilySlide() {
        if (totalSlides === 0) return;
        
        slides[currentIndex].classList.remove("active");
        if (slideBadge) slideBadge.classList.add("text-fade");
        if (slideTitle) slideTitle.classList.add("text-fade");
        if (slideSubtext) slideSubtext.classList.add("text-fade");
        
        currentIndex = (currentIndex + 1) % totalSlides;

        setTimeout(() => {
            if (typeof slideData !== 'undefined' && slideData[currentIndex]) {
                const currentData = slideData[currentIndex];
                if (slideBadge) slideBadge.innerHTML = currentData.badge;
                if (slideTitle) slideTitle.innerHTML = currentData.title;
                if (slideSubtext) slideSubtext.innerHTML = currentData.subtext;
            }
            
            slides[currentIndex].classList.add("active");
            
            if (slideBadge) slideBadge.classList.remove("text-fade");
            if (slideTitle) slideTitle.classList.remove("text-fade");
            if (slideSubtext) slideSubtext.classList.remove("text-fade");
        }, 350);
    }
    
    if (totalSlides > 1) {
        // First slide-ku active class
        slides[0].classList.add("active");
        setInterval(showNextFamilySlide, 5000); // 5 seconds
    }
});