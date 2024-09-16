// Default Slide
let slideIndex = 1;
showSlides(slideIndex);

// Next Slide
function plusSlides(n) {
    let slides = document.getElementsByClassName("slide");
    var checkRadio = document.querySelector('input[name="select"]:checked');
    if(n == 1 && slideIndex == 1 && checkRadio != null){
        slides[0].style.display = "none";  
        showSlides(slideIndex += n);
        if (document.getElementById('option-1').checked || document.getElementById('option-3').checked){
          document.getElementById("nextBtn").innerHTML = "Submit";
        }
    }
    else if (n == -1){
        slides[slideIndex - 1].style.display = "none";  
        showSlides(slideIndex += n);
    }
    else if (n == 1 && slideIndex == 2){
        // Data Validation
        var email = document.querySelector('input[name="email"]');
        var pwd = document.querySelector('input[name="password"]');
        var pwd2 = document.querySelector('input[name="confirmation"]');

        // If All Fields Are Complete
        if ((email.value == "") || (pwd.value == "") || (pwd2.value == "")) {
          alert("Please fill in all the fields")
        }
        // If Registering For A Student Account, Check If School Email Is Being Used
        else if (checkRadio.value == "student" && !(email.value).includes("@share.epsb.ca")){
          alert("Use your school email")
        }
        // Basic Email Verification
        else if (!(email.value).includes("@")){
          alert("Please enter a valid email")
        }
        // Password Complexity Verification
        else if (pwd.value.length < 8 || pwd.value.length > 72){
          alert("Password length must be 8 to 72 characters")
        }
        else if (/^[a-zA-Z]+$/.test(pwd.value) || /^[0-9]+$/. test(pwd.value)){
          alert("Password must include a combination of letters and numbers/special character")
        }
        else if (pwd.value != pwd2.value) {
          alert("Passwords do not match")
        }
        // If All Tests Have Been Passed
        else{
          if (document.getElementById('option-1').checked || document.getElementById('option-3').checked){
            document.getElementById("reg-form").submit();  
          }
          else if (document.getElementById('option-2').checked){
            slides[1].style.display = "none";  
            showSlides(slideIndex += n);    
          }    
        }
    }
    else if (n == 1 && slideIndex == 3){
      if (document.querySelector('input[name="conf-email"]').value == "" || !(document.querySelector('input[name="conf-email"]').value).includes("@share.epsb.ca")){
        alert("Please use a valid confirmation email.")
      }
      else {
        document.getElementById("reg-form").submit(); 
      }
       
    }
}

// Display Current Slide
function currentSlide(n) {
    showSlides(slideIndex = n);
}

// Display Slide
function showSlides(n) {
  let i;
  let slides = document.getElementsByClassName("slide");
  if ((n-1) == 0) {
    document.getElementById("prevBtn").style.display = "none";
  } else {
    document.getElementById("prevBtn").style.display = "inline";
    document.getElementById("prevBtn").style.marginRight = "10px";
  }
  if ((n-1) == (slides.length - 1)) {
    document.getElementById("nextBtn").innerHTML = "Submit";
  } else {
    document.getElementById("nextBtn").innerHTML = "Next";
  }
  if (n < 1) {slideIndex = slides.length}
  slides[slideIndex-1].style.display = "block";  
}

