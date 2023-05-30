// SPY SCROLL NAVBAR
var prevScrollpos = window.pageYOffset;
window.onscroll = function () {
  var currentScrollPos = window.pageYOffset;
  if (prevScrollpos > currentScrollPos) {
    document.getElementById("navbar__logo").classList.remove("logo-down");
    document.getElementById("subnav").classList.remove("scroll-down");
  } else {
    document.getElementById("navbar__logo").classList.add("logo-down");
    document.getElementById("subnav").classList.add("scroll-down");
  }
  prevScrollpos = currentScrollPos;
};
function darkenScreen() {
  document.querySelector("footer").classList.add("darken-on-hover");
  document.querySelector("main").classList.add("darken-on-hover");
}

function normalizeScreen() {
  document.querySelector("footer").classList.remove("darken-on-hover");
  document.querySelector("main").classList.remove("darken-on-hover");
}

// Get all the category checkboxes
var checkboxes = document.querySelectorAll('.form-check-input');

// Add event listeners to each checkbox
checkboxes.forEach(function(checkbox) {
  checkbox.addEventListener('click', function() {
    // Submit the form
    this.closest('form').submit();

    // Toggle the checkbox's checked state
    this.checked = !this.checked;
  });
});

function submitForm(sortOrder) {
  var form = document.getElementById('filter-form');
  // Set a hidden input field to hold the sort order value
  var sortOrderInput = document.createElement('input');
  sortOrderInput.type = 'hidden';
  sortOrderInput.name = 'sortOrder';
  sortOrderInput.value = sortOrder;
  form.appendChild(sortOrderInput);
  // Submit the form
  form.submit();
}