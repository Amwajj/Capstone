// about-cards-anim.js
// Animation: show .about-card with fade-in when scrolled into view

document.addEventListener('DOMContentLoaded', function() {
    var cards = document.querySelectorAll('.about-card');
    if (!cards.length) return;

    function showCardsOnScroll() {
        var trigger = window.innerHeight * 0.92;
        var delay = 0;
        cards.forEach(function(card, idx) {
            var rect = card.getBoundingClientRect();
            if (rect.top < trigger && !card.classList.contains('visible')) {
                setTimeout(function() {
                    card.classList.add('visible');
                }, delay);
                delay += 180; // delay between each card
            }
        });
    }

    // Initial check
    showCardsOnScroll();
    // On scroll
    window.addEventListener('scroll', showCardsOnScroll);
});
