# 🚀 Piano SEO Completo — Mila Grow Partner
**Dominio:** milagrowpartner.com  
**Data:** Giugno 2026

---

## ✅ SEO TECNICO — Già Implementato

Tutto il codice qui sotto è già nel sito e live su Vercel.

| Elemento | Stato | Dettaglio |
|---|---|---|
| `<title>` ottimizzato | ✅ | "Mila Grow Partner \| Agenzia di Marketing & Branding — Firenze, Italia" |
| Meta `description` | ✅ | 155 caratteri con keyword primarie |
| Meta `keywords` | ✅ | 11 keyword target |
| `canonical` URL | ✅ | `https://www.milagrowpartner.com/` |
| Open Graph (Facebook/LinkedIn) | ✅ | Titolo, descrizione, immagine 1200x630 |
| Twitter Cards | ✅ | summary_large_image |
| JSON-LD Structured Data | ✅ | Organization, LocalBusiness, WebSite, WebPage, FAQPage |
| `sitemap.xml` | ✅ | 5 URL indicizzate |
| `robots.txt` | ✅ | Allow all + sitemap reference |
| `geo.region` / `geo.placename` | ✅ | Firenze, IT-FI |
| `theme-color` | ✅ | #0d0d0d |
| `robots` meta | ✅ | index, follow, max-snippet:-1 |
| Heading hierarchy (H1→H3) | ✅ | Struttura semantica corretta |
| Alt text immagini | ✅ | Descrittivo e keyword-rich |

---

## 🌐 STEP 1 — Collegare GoDaddy a Vercel

### A) Su Vercel (Dashboard)
1. Vai su → [vercel.com/dashboard](https://vercel.com/dashboard)
2. Clicca sul progetto **mila-collective**
3. Vai su → **Settings** → **Domains**
4. Clicca **Add Domain**
5. Digita: `milagrowpartner.com` → Clicca **Add**
6. Aggiungi anche: `www.milagrowpartner.com`
7. Vercel ti mostrerà i **record DNS** da configurare (vedi sotto)

### B) Su GoDaddy — Configurazione DNS
1. Vai su → [dcc.godaddy.com](https://dcc.godaddy.com)
2. Trova il dominio **milagrowpartner.com** → Clicca **DNS**
3. Elimina i record A e CNAME esistenti
4. Aggiungi questi record:

| Tipo | Nome | Valore | TTL |
|---|---|---|---|
| `A` | `@` | `76.76.21.21` | 600 |
| `CNAME` | `www` | `cname.vercel-dns.com` | 3600 |

> [!IMPORTANT]
> La propagazione DNS può richiedere da 30 minuti a 48 ore. Vercel ti invierà una notifica quando il dominio è attivo.

---

## 📊 STEP 2 — Google Search Console

1. Vai su → [search.google.com/search-console](https://search.google.com/search-console)
2. Aggiungi proprietà → **URL prefix** → `https://www.milagrowpartner.com`
3. Verifica con metodo **HTML tag** (incolla nel `<head>`)
4. Invia sitemap: `https://www.milagrowpartner.com/sitemap.xml`
5. Richiedi indicizzazione della homepage

---

## 🎯 STEP 3 — Keyword Strategy (Posizionamento Organico)

### Keyword Primarie (Alta priorità)
| Keyword | Volume mensile stimato | Difficoltà | Intenzione |
|---|---|---|---|
| agenzia marketing firenze | 500-1K | Media | Commerciale |
| grow partner marketing italia | 100-500 | Bassa | Commerciale |
| branding firenze | 300-600 | Media | Commerciale |
| agenzia social media firenze | 200-500 | Bassa | Commerciale |
| posizionamento google firenze | 100-300 | Bassa | Commerciale |

### Keyword Secondarie (Long-tail)
| Keyword | Intenzione |
|---|---|
| come fare branding per una startup | Informazionale |
| funnel di vendita come si crea | Informazionale |
| migliorare posizionamento instagram | Informazionale |
| agenzia marketing digitale firenze prezzi | Commerciale |
| consulenza marketing firenze gratuita | Commerciale |
| campagne google ads firenze | Commerciale |

### Keyword Locali (Google Maps)
| Keyword |
|---|
| marketing agency florence italy |
| agenzia pubblicità firenze |
| consulenza branding toscana |

---

## 📅 STEP 4 — Piano di Contenuto (6 mesi)

### Mese 1-2: Fondamenta
- [ ] Creare pagina `/servizi` dedicata per ogni servizio
- [ ] Creare sezione Blog/Insights sul sito
- [ ] Pubblicare 4 articoli keyword-rich:
  - *"Come costruire un brand da zero: la guida completa 2026"*
  - *"Funnel di vendita: cos'è e come si crea per la tua azienda"*
  - *"Social Media Management: guida per le PMI italiane"*
  - *"SEO locale: come posizionarti su Google a Firenze"*

### Mese 3-4: Autorità
- [ ] Guest posting su blog di settore italiani
- [ ] Creare profilo Google Business (Google Maps)
- [ ] Profilo LinkedIn aziendale + pubblicazioni settimanali
- [ ] Backlink da directory locali (Pagine Gialle, Kompass, ecc.)
- [ ] Pubblicare case study cliente (anonimizzato)

### Mese 5-6: Scalabilità
- [ ] Ampliare blog con 2 articoli/settimana
- [ ] Avviare YouTube con tutorial marketing (con trascrizione SEO)
- [ ] Richiedere recensioni Google ai clienti
- [ ] Creare landing page dedicate per ogni keyword primaria

---

## 🔧 STEP 5 — Tool SEO da Configurare

| Tool | Scopo | Gratuito? |
|---|---|---|
| Google Search Console | Monitorare posizioni e clic | ✅ Gratis |
| Google Analytics 4 | Traffico e comportamento utenti | ✅ Gratis |
| Google Business Profile | Visibilità Maps e locale | ✅ Gratis |
| Ahrefs / Semrush | Analisi competitor e keyword | 💰 A pagamento |
| Screaming Frog | Audit tecnico SEO | ✅ Gratis (500 URL) |
| PageSpeed Insights | Velocità sito | ✅ Gratis |

---

## ⚡ STEP 6 — Ottimizzazione Velocità (Core Web Vitals)

> [!TIP]
> Google usa i Core Web Vitals come fattore di ranking dal 2021.

- **LCP** (Largest Contentful Paint): < 2.5s ✅ Le immagini sono ottimizzate
- **CLS** (Cumulative Layout Shift): < 0.1 ✅ Layout stabile
- **FID/INP** (Interaction): < 200ms ✅ JavaScript minimale

### Azioni consigliate:
- Convertire le immagini in formato WebP (riduce del 30% il peso)
- Aggiungere `loading="lazy"` alle immagini sotto il fold
- Minificare CSS e JS in produzione

---

## 📱 STEP 7 — SEO Locale (Google Maps)

1. Crea profilo su → [Google Business Profile](https://business.google.com)
2. Categoria: **Marketing Agency** + **Advertising Agency**
3. Aggiungi:
   - Indirizzo Firenze
   - Telefono
   - Sito: `www.milagrowpartner.com`
   - Orari lavorativi
   - Foto dello studio/team (usa le immagini già generate)
4. Chiedi ai primi clienti recensioni a 5 stelle 🌟

---

## 📈 KPI da Monitorare (ogni mese)

| KPI | Target mese 3 | Target mese 6 |
|---|---|---|
| Posizione Google "agenzia marketing firenze" | Top 10 | Top 5 |
| Visite organiche mensili | 200+ | 800+ |
| Click Through Rate (CTR) | > 3% | > 5% |
| Backlink acquisiti | 10+ | 30+ |
| Recensioni Google | 5+ | 15+ |
| Domain Authority | 10+ | 20+ |

---

> *"Il SEO non è una sprint — è una maratona. Ma ogni giorno che iniziamo prima, è un giorno di vantaggio sui competitor."*  
> — Mila Grow Partner Strategy Team
