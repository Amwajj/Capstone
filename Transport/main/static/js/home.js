// Animation for stats section on scroll
function animateStatsOnView() {
  const stats = document.querySelectorAll('.stat-box');
  const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('stat-animate');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.3 });
  stats.forEach(stat => observer.observe(stat));
}

// Animate timeline cards on scroll (vertical timeline)
function animateTimelineOnView() {
  const timelineCards = document.querySelectorAll('.timeline-card');
  timelineCards.forEach(card => card.classList.add('js-hide'));
  const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const card = entry.target;
        const step = card.closest('.timeline-step');
        const steps = Array.from(document.querySelectorAll('.timeline-step .timeline-card'));
        const idx = steps.indexOf(card);
        // If last card, show immediately
        if (idx === steps.length - 1) {
          card.classList.remove('js-hide');
          card.classList.add('animate-timeline');
        } else {
          setTimeout(() => {
            card.classList.remove('js-hide');
            card.classList.add('animate-timeline');
          }, idx * 300);
        }
        observer.unobserve(card);
      }
    });
  }, { threshold: 0.2 });
  timelineCards.forEach(card => observer.observe(card));
}

document.addEventListener('DOMContentLoaded', function() {
  animateStatsOnView();
  // Animate divider on scroll
  const divider = document.querySelector('.animate-divider');
  if (divider) {
    const dividerObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('divider-animate');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.2 });
    dividerObserver.observe(divider);
  }
  // Animate features on scroll
  const features = document.querySelectorAll('.animate-feature');
  const featuresObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry, idx) => {
      if (entry.isIntersecting) {
        setTimeout(() => {
          entry.target.classList.add('feature-animate');
        }, idx * 150);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.2 });
  features.forEach(f => featuresObserver.observe(f));

  // Animate FAQ fade-in
  const faq = document.querySelector('.animate-faq');
  if (faq) {
    faq.classList.add('faq-animate');
  }

  // Animate section titles
  document.querySelectorAll('.animate-fadein').forEach(el => {
    el.classList.add('fadein-animate');
  });

  animateTimelineOnView();
});

// CSS (add to your CSS file):
// .stat-box { opacity: 0; transform: translateY(40px); transition: all 0.7s cubic-bezier(.4,1.4,.6,1); }
// .stat-box.stat-animate { opacity: 1; transform: translateY(0); }
