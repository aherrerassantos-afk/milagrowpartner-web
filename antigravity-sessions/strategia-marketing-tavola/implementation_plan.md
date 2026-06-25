# Piano di Azione: Hub di Automazione Multi-Tenant
### Progetto: Tavola dei Santi × Mila Grow Partner

---

## 📌 Indice dei Nodi di Lavoro

### ✅ Completati
- [x] **Nodo 1:** Hub Privato su Milagrow — Chat UI + login deployati
- [x] **Nodo 2:** Connessione n8n API — Workflow v2.7.0 analizzato e corretto
- [x] **Nodo 3:** Agente Marco (Claude Sonnet 4.6) — Identity + Brand DNA iniettati
- [x] **Nodo 4:** Chat end-to-end funzionante — Marco risponde su milagrowpartner.com
- [x] **Nodo 5:** Sito Tavola dei Santi — Wholesale pallet, Coming Soon, valute live

### ⏳ Prossimi Nodi
- [ ] **Nodo 6:** Config Meta Ads — Instagram + Facebook Tavola dei Santi
- [ ] **Nodo 7:** Google SEO Optimization — tavoladeisanti.com
- [ ] **Nodo 8:** Integrazione pubblicazione automatica n8n → Meta

---

## ✅ Completato in Dettaglio

### Nodi 1–2 — Hub Milagrow + n8n
- `area-privata.html` live → [milagrowpartner.com/area-privata](https://milagrowpartner.com/area-privata) · Password: `Mila2026!`
- Workflow v2.7.0 attivo, bug `6b.2 Video Status` corretto su entrambi i workflow
- Webhook: `ed434e7c-2e49-426a-b0c9-717c24dc5317`

### Nodi 3–4 — Marco (Agente IA)
- `1 Briefing Director` → collegato a **Claude Sonnet 4.6** (staccato da Gemini)
- System prompt completo: identità Marco, brand DNA Tavola dei Santi, modalità conversazione/brief
- Brand corretto: **Val d'Orcia, Toscana** · Nicchia: cucina italiana premium
- Catalogo: Olio EVO DOP (focus attuale Colombia) + pasta/vino (coming soon)
- Chat live e funzionante con foto profilo Marco

### Nodo 5 — Sito Tavola dei Santi
- Wholesale: Medio Pallet 540 bot. (−15%) + Pallet Completo 1.080 bot. (−20%)
- Retail (0,5L / 6x / 12x) → "Coming Soon" disabilitato
- Prezzi dinamici in EUR / USD / COP (conversione automatica)
- Sezione "Próximamente" per pasta, vino, altri prodotti
- Live → [tavoladeisanti.com/tienda.html](https://tavoladeisanti.com/tienda.html)

---

## 🔲 Nodo 6 — Config Meta Ads (Instagram + Facebook)

**Obiettivo:** Collegare Tavola dei Santi all'account pubblicitario Meta esistente e lanciare le prime campagne.

**Stato attuale rilevato:**
- ✅ Account pubblicitario Meta: `1348377917008116`
- ✅ Business Manager attivo con portfolio: Blue Arroyo, Milagrowpartner, Palazzo Blue Arroyo
- ⏳ Tavola dei Santi non ancora collegata al BM

**Step da eseguire:**

### 6.1 — Collegare i social di Tavola al Business Manager
1. Vai su [business.facebook.com](https://business.facebook.com) → **Impostazioni Business**
2. **Account Instagram** → Aggiungi → inserisci credenziali Instagram Tavola dei Santi
3. **Pagine Facebook** → Aggiungi → seleziona o crea pagina "Tavola dei Santi"
4. Assegna entrambi al portfolio **Milagrowpartner** (così il team Mila li gestisce)

### 6.2 — Creare Pixel Meta per tavoladeisanti.com
1. Business Manager → **Origini dati** → Pixel → Crea nuovo
2. Nome: `TavolaPixel` · URL: `tavoladeisanti.com`
3. Installa il codice Pixel nel `<head>` di tutti i file HTML del sito
4. Configura eventi: `PageView`, `ViewContent`, `Contact` (form WhatsApp)

### 6.3 — Prima campagna Awareness Colombia
- **Obiettivo:** Awareness · **Budget:** €20/giorno (già configurato nel BM)
- **Target geo:** Colombia — Bogotá (età 28–55) + Medellín (età 25–50)
- **Target interessi:** cucina italiana, gastronomia premium, chef, vino, lifestyle luxury
- **Formato:** Reel verticale (Marco genera il copy via n8n) + carosello prodotto
- **Input per Marco:** `Brand: tavola_dei_santi · Formato: reel · Obiettivo: awareness · Tono: elegante`

### 6.4 — Connettere account Meta all'n8n (Nodo 8)
- Aggiungere credenziali API Meta al workflow `8.2a Instagram Publisher`
- Token: Meta Graph API · Scope: `pages_manage_posts`, `instagram_content_publish`
- Testare pubblicazione automatica da Marco → Meta

---

## 🔲 Nodo 7 — Google SEO Optimization

**Obiettivo:** Posizionare tavoladeisanti.com su Google per le ricerche premium in Colombia.

### 7.1 — Google Search Console
1. Vai su [search.google.com/search-console](https://search.google.com/search-console)
2. Aggiungi proprietà: `tavoladeisanti.com`
3. Verifica via DNS (GoDaddy) o meta tag nell'`<head>`
4. Invia sitemap: `tavoladeisanti.com/sitemap.xml` (da creare)

### 7.2 — Ottimizzazione On-Page (da fare sul sito)
| Pagina | Title Tag | Meta Description |
|---|---|---|
| `index.html` | Tavola dei Santi · Aceite de Oliva Premium Italia Colombia | Olio EVO DOP de la Val d'Orcia. Importación directa a Colombia. Calidad premium para chefs y gourmets. |
| `tienda.html` | Comprar Aceite de Oliva Extra Virgen IGP · Toscano Colombia | Aceite toscano certificado IGP. Disponible en Bogotá y Medellín. Pedidos wholesale desde 540 botellas. |
| `nosotros.html` | Quiénes Somos · Tavola dei Santi · Partner Italiano Premium | Somos el puente entre los mejores productores italianos y el mercado premium colombiano. |

### 7.3 — Sitemap + robots.txt (da creare)
- `sitemap.xml` con tutte le pagine indicizzabili
- `robots.txt` per escludere `/admin/`, `/data/`

### 7.4 — Schema Markup (JSON-LD)
- `Product` schema su `tienda.html` per l'olio (prezzo, disponibilità, recensioni)
- `Organization` schema su `index.html` (nome, logo, contatti, area servita)
- `LocalBusiness` per Colombia

### 7.5 — Google My Business
- Crea profilo Google Business per Tavola dei Santi in Colombia
- Categoria: "Importatore alimentare" · Area: Bogotá + Medellín
- Aggiunge visibilità locale nelle ricerche Maps

---

## 🔲 Nodo 8 — Pubblicazione Automatica n8n → Meta
*(Si sblocca dopo Nodo 6.4)*
- Marco genera copy + brief → workflow n8n → pubblica su Instagram/Facebook automaticamente
- Human Approval Gate: il team Mila approva prima della pubblicazione
- Log di tutte le pubblicazioni su Google Drive

---

> [!IMPORTANT]
> **Prossimo passo operativo — Nodo 6:**
> Fornisci le credenziali Instagram e Facebook di Tavola dei Santi così le colleghi al tuo Business Manager `1348377917008116` e partiamo con la prima campagna.
