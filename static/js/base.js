// Close Popup
function closeAlert() {
  document.getElementById("alert").classList.toggle("closed");
}

// Open Navbar (For small screens)
function openMenu() {
  document.getElementById("choices").classList.toggle("show");
  document.body.style.overflow = 'hidden';
}

// Close Specified Dropdowns
function closeDropdown(type) {
  var dropdowns = document.getElementsByClassName(type);
  var i;
  for (i = 0; i < dropdowns.length; i++) {
    var openDropdown = dropdowns[i];
    if (openDropdown.classList.contains('show')) {
      openDropdown.classList.remove('show');
    }
  }
}

// Open News Dropdown
function openNews() {
  if (!document.getElementById("news").classList.contains('show')){
    closeDropdown("dropdown-content")
    closeDropdown("sub-dropdown-content")
  }
  document.getElementById("news").classList.toggle("show");
}

// Open Teams Dropdown
function openTeams(team) {
  if (team == null) {
    if (!document.getElementById("teams").classList.contains('show')){
      closeDropdown("dropdown-content")
    }
    document.getElementById("teams").classList.toggle("show");
  }
  else {
    if (!document.getElementById(team).classList.contains('show')){
      closeDropdown("sub-dropdown-content")
    }
    document.getElementById(team).classList.toggle("show");
  }
}

// Open Profile Dropdown
function openProfile() {
  if (!document.getElementById("profile").classList.contains('show')){
    closeDropdown("sub-dropdown-content")
    closeDropdown("dropdown-content")
  }
  document.getElementById("profile").classList.toggle("show");
}

// Close al of the dropdowns if the user clicks outside of it
window.onclick = function(event) {
  if (!event.target.matches('.menubtn') && !event.target.matches('.dropbtn') && !event.target.matches('.subdropbtn')) {
    closeDropdown("content-choices")
    closeDropdown("dropdown-content")
    closeDropdown("sub-dropdown-content")
    document.body.style.overflow = 'initial';
  }
}
