// ==========================================================================
// MILA GROW PARTNER — CLIENT CONTROLLER & CRM DISPATCHER
// ==========================================================================

document.addEventListener('DOMContentLoaded', () => {
  // 1. Mobile Menu Toggle
  const burgerBtn = document.getElementById('burgerBtn');
  const mainNav = document.getElementById('mainNav');

  if (burgerBtn && mainNav) {
    burgerBtn.addEventListener('click', () => {
      const isOpen = mainNav.classList.toggle('is-open');
      burgerBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });

    // Chiudi il menu quando si clicca un link di navigazione
    const navLinks = mainNav.querySelectorAll('a');
    navLinks.forEach(link => {
      link.addEventListener('click', () => {
        mainNav.classList.remove('is-open');
        burgerBtn.setAttribute('aria-expanded', 'false');
      });
    });
  }

  // 2. Lead Form Submission & Direct WhatsApp Sync
  const form = document.getElementById('milaLeadForm');
  const formStatus = document.getElementById('formStatus');
  const submitBtn = document.getElementById('submitBtn');

  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      const nome = (document.getElementById('leadNome')?.value || '').trim();
      const telefono = (document.getElementById('leadTelefono')?.value || '').trim();
      const email = (document.getElementById('leadEmail')?.value || '').trim();
      const messaggio = (document.getElementById('leadMessaggio')?.value || '').trim();

      if (!nome || !telefono || !email) {
        showStatus('Per favore compila tutti i campi obbligatori.', 'error');
        return;
      }

      const originalBtnText = submitBtn.innerHTML;
      submitBtn.disabled = true;
      submitBtn.innerHTML = 'Trasmissione in corso...';
      showStatus('Elaborazione richiesta in corso...', '');

      const payload = {
        source: 'milagrowpartner.com/abbonamento-300',
        nome,
        referente: nome,
        telefono,
        email,
        messaggio,
        servizio: 'Developer Partner Flat 300€/mese',
        timestamp: new Date().toISOString()
      };

      // Tentativo invio CRM Holding via endpoint serverless locale
      try {
        await fetch('/api/lead', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        }).catch(() => null);
      } catch (_) {}

      // Tentativo secondario diretto verso il CRM Holding di Palazzo Blue Arroyo
      try {
        await fetch('https://palazzobluearroyo.it/api/crm/prospect-sync', {
          method: 'POST',
          mode: 'no-cors',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        }).catch(() => null);
      } catch (_) {}

      // Messaggio WhatsApp con Julian Herrera
      const textWhatsApp = `Ciao Julian! Sono ${nome} (${email} - tel: ${telefono}). Ho compilato il modulo sul sito milagrowpartner.com per attivare l'abbonamento Developer da 300 € / mese: "${messaggio}"`;
      const waUrl = `https://wa.me/393510380392?text=${encodeURIComponent(textWhatsApp)}`;

      showStatus(`✓ Richiesta presa in carico con successo! Apertura chat diretta con Julian Herrera...`, 'success');
      form.reset();

      setTimeout(() => {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalBtnText;
        window.open(waUrl, '_blank');
      }, 1200);
    });
  }

  function showStatus(msg, type) {
    if (!formStatus) return;
    formStatus.style.display = 'block';
    formStatus.className = 'mila-form-status ' + (type || '');
    formStatus.textContent = msg;
  }
});
