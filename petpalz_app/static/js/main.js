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
