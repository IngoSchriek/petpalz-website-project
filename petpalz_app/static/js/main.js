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
var checkboxes = document.querySelectorAll(".form-check-input");

// Add event listeners to each checkbox
checkboxes.forEach(function (checkbox) {
  checkbox.addEventListener("click", function () {
    // Submit the form
    this.closest("form").submit();

    // Toggle the checkbox's checked state
    this.checked = !this.checked;
  });
});

function submitForm(sortOrder) {
  var form = document.getElementById("filter-form");
  // Set a hidden input field to hold the sort order value
  var sortOrderInput = document.createElement("input");
  sortOrderInput.type = "hidden";
  sortOrderInput.name = "sortOrder";
  sortOrderInput.value = sortOrder;
  form.appendChild(sortOrderInput);
  // Submit the form
  form.submit();
}

const toggleButton = document.getElementById("toggle-button");
toggleButton.addEventListener("click", function () {
  if (toggleButton.textContent == "View less") {
    toggleButton.textContent = "View more";
  } else {
    toggleButton.textContent = "View less";
  }
});

function zoom(e){
  var zoomer = e.currentTarget;
  e.offsetX ? offsetX = e.offsetX : offsetX = e.touches[0].pageX
  e.offsetY ? offsetY = e.offsetY : offsetX = e.touches[0].pageX
  x = offsetX/zoomer.offsetWidth*100
  y = offsetY/zoomer.offsetHeight*100
  zoomer.style.backgroundPosition = x + '% ' + y + '%';
}

function decreaseValue() {
  var valueInput = document.getElementById("valueInput");
  var decreaseBtn = document.getElementById("decreaseBtn");

  var value = parseInt(valueInput.value);
  if (value > 1) {
      valueInput.value = value - 1;
      decreaseBtn.value = "decrease";
  }
}

function increaseValue(input) {
  var valueInput = document.getElementById("valueInput");
  var increaseBtn = document.getElementById("increaseBtn");

  var value = parseInt(valueInput.value);
  valueInput.value = value + 1;
  increaseBtn.value = "increase";
}

function handleInput(input) {
  if (!input.validity.valid) {
    input.value = '1';
  }
}

function handleBlur(input) {
  if (input.value === '') {
    input.value = '1';
  }
}

function changeValue(button, increment) {
  var inputElement = button.parentNode.querySelector('input[name="value"]');
  var currentValue = parseInt(inputElement.value);
  var newValue = currentValue + increment;

  if (newValue >= 1 && newValue <= 100) {
    inputElement.value = newValue;
    var form = button.closest('form');
    form.querySelector('input[name="value"]').value = newValue; // Update the input with the new value
    form.submit();
  }
}