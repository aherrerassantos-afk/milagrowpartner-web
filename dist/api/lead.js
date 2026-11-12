// Vercel Serverless Function: api/lead.js
// Gestione ricezione contatti da milagrowpartner.com verso il CRM Holding e notifiche

export default async function handler(req, res) {
  // CORS Headers
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version'
  );

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ ok: false, error: 'Method not allowed' });
  }

  try {
    const body = typeof req.body === 'string' ? JSON.parse(req.body) : (req.body || {});
    const nome = String(body.nome || body.referente || '').trim() || '[DA CONFERMARE]';
    const email = String(body.email || '').trim().toLowerCase() || '[DA CONFERMARE]';
    const telefono = String(body.telefono || '').trim() || '[DA CONFERMARE]';
    const messaggio = String(body.messaggio || body.note || '').trim() || 'Richiesta Partner Tecnologico 300€/mese';

    const payload = {
      source: 'milagrowpartner.com/abbonamento-300',
      nome,
      referente: nome,
      email,
      telefono,
      messaggio,
      servizio: 'Developer Tecnologico Flat 300€/mese',
      createdAt: new Date().toISOString()
    };

    // Forward facoltativo verso il CRM unificato di Holding su palazzobluearroyo.it
    let holdingForwarded = false;
    try {
      const crmResponse = await fetch('https://palazzobluearroyo.it/api/crm/prospect-sync', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: AbortSignal.timeout(4000)
      });
      if (crmResponse.ok) {
        holdingForwarded = true;
      }
    } catch (_) {
      holdingForwarded = false;
    }

    return res.status(200).json({
      ok: true,
      message: 'Lead registrato con successo nel flusso Mila Grow Partner',
      holdingForwarded,
      directContact: {
        titolare: 'Julian Herrera',
        telefono: '+39 351 038 0392',
        whatsappUrl: `https://wa.me/393510380392?text=${encodeURIComponent(`Ciao Julian, sono ${nome} (${telefono}). Ho richiesto info per l'abbonamento Developer da 300€/mese: ${messaggio}`)}`
      }
    });
  } catch (err) {
    return res.status(500).json({ ok: false, error: err.message });
  }
}
