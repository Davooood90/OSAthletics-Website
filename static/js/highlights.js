// Default Index
let slideIndex = 1;
showSlides(slideIndex);

// Highlights Slide
function plusSlides(n) {
  showSlides(slideIndex += n);   
}

// Display Current Slide
function currentSlide(n) {
  showSlides(slideIndex = n);
}

// Display Slide
function showSlides(n) {
  let i;
  let slides = document.getElementsByClassName("slide");
  if (n > slides.length) {slideIndex = 1}    
  if (n < 1) {slideIndex = slides.length}
  for (i = 0; i < slides.length; i++) {
    slides[i].style.display = "none";  
  }
  slides[slideIndex-1].style.display = "block";  
  slides[slideIndex-1].style.width = "100%";  
}
