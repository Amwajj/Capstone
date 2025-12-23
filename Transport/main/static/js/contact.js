// Fade-in from left animation for contact-welcome

document.addEventListener('DOMContentLoaded', function() {
  var el = document.querySelector('.fadein-left');
  if (el) {
    setTimeout(function() {
      el.classList.add('show');
    }, 600);
  }
});
