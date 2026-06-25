// Mila Collective — index.js

document.addEventListener('DOMContentLoaded', () => {

  // ── Reveal on scroll ──
  const revealTargets = [
    '.section-who .two-col',
    '.section-values .two-col',
    '.section-header',
    '.service-card',
    '.contact-left',
    '.contact-right'
  ];

  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });

  revealTargets.forEach(sel => {
    document.querySelectorAll(sel).forEach((el, i) => {
      el.classList.add('reveal');
      el.style.transitionDelay = `${i * 80}ms`;
      revealObserver.observe(el);
    });
  });

  // ── Sticky header shadow ──
  const header = document.querySelector('.header');
  window.addEventListener('scroll', () => {
    if (window.scrollY > 40) {
      header.style.boxShadow = '0 2px 20px rgba(0,0,0,0.08)';
    } else {
      header.style.boxShadow = 'none';
    }
  });

  // ── Contact form submission ──
  const form = document.querySelector('.contact-form');
  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();

      const name = form.querySelector('input[type="text"]').value;
      const selectedServices = [];
      form.querySelectorAll('input[name="service"]:checked').forEach(cb => {
        selectedServices.push(cb.value);
      });

      const btn = form.querySelector('.btn-submit');
      btn.textContent = '✓ Inviato con Successo';
      btn.style.background = '#b8965a';
      btn.style.color = '#fff';

      setTimeout(() => {
        form.reset();
        btn.textContent = 'Invia Richiesta';
        btn.style.background = '';
        btn.style.color = '';
      }, 3500);
    });
  }

});
