# 🗺️ PIANO D'AZIONE MASTERIZZATO
## Mila Grow Partner — Hub IA Multi-Cliente
### Aggiornato: 21 Giugno 2026

---

## INDICE GENERALE

| # | Nodo | Cliente | Stato |
|---|---|---|---|
| 1 | Hub Privato Milagrow (Chat UI + Login) | Mila | ✅ Live |
| 2 | Connessione n8n — Workflow v2.7.0 | Mila | ✅ Live |
| 3 | Agente Marco — Identity + Brand DNA | Tavola dei Santi | ✅ Live |
| 4 | Chat Marco end-to-end funzionante | Tavola dei Santi | ✅ Live |
| 5 | Sito Tavola dei Santi (wholesale, valute) | Tavola dei Santi | ✅ Live |
| ★ | Agente Chiara — Identity + Brand DNA | Palazzo Blue Arroyo | ✅ Live |
| ★ | Hub Admin Chiara — Pagina dedicata | Palazzo Blue Arroyo | ✅ Live |
| ★ | Protocollo Crescita — 7 Fasi standard | Tutti gli agenti | ✅ Live |
| ★ | Workflow Chiara n8n (chiara-chat) | Palazzo Blue Arroyo | ✅ Live |
| ★ | Brand DNA Marco v2.0 — Tavola dei Santi | Tavola dei Santi | ✅ Aggiornato 21/06 |
| 7 | SEO Tecnico completo — tavoladeisanti.com | Tavola dei Santi | ✅ **COMPLETATO** 21/06 |
| 6 | Meta Ads — Tavola dei Santi | Tavola dei Santi | 🔲 **PROSSIMO** |
| 8 | Pubblicazione automatica n8n → Meta | Tavola dei Santi | 🔲 Bloccato da 6 |
| 9 | Meta Ads — Palazzo Blue Arroyo | Palazzo Blue Arroyo | 🔲 In coda |
| 10 | Workflow Protocollo Crescita su n8n | Tutti gli agenti | 🔲 In coda |

---

## ✅ COMPLETATI

### Nodi 1–2 — Hub Milagrow + n8n
- area-privata.html live → https://milagrowpartner.com/area-privata · Password: Mila2026!
- Workflow v2.7.0 attivo su aherreras.app.n8n.cloud
- Bug 6b.2 Video Status corretto

### Nodi 3–4 — Agente Marco (Tavola dei Santi)
- 1 Briefing Director → Claude Sonnet 4.6
- Brand DNA completo: Val d'Orcia, olio EVO DOP, Bogotá/Medellín
- Webhook: https://aherreras.app.n8n.cloud/webhook/chat?sessionId=tavola_dei_santi_smm
- Chat live su https://milagrowpartner.com/area-privata

### Nodo 5 — Sito Tavola dei Santi
- Wholesale: Medio Pallet 540 bot. (−15%) + Pallet Completo 1.080 bot. (−20%)
- Retail → "Coming Soon" | Prezzi in EUR / USD / COP
- Live → https://tavoladeisanti.com/tienda.html

---

### ★ NUOVO — Agente Chiara (Palazzo Blue Arroyo)
- Workflow n8n: Chiara — Palazzo Blue Arroyo Marketing Team v1.0
- ID: oA3ZjaCx8HlG3tcl · Active: ✅
- Webhook: https://aherreras.app.n8n.cloud/webhook/chiara-chat
- Base: Marketing Team Blueprint v2.8.0 (57 nodi: Claude + Gemini + Image/Video)
- SessionId: palazzo_blue_arroyo_smm / _ops / _mktg / _report / _crescita

### ★ NUOVO — Hub Admin Chiara
- URL live: https://milagrowpartner.com/palazzo-blue-arroyo
- Deploy Vercel: dpl_DYDrQpnjqEgnLvbc5D9Qp49BRHrR
- Tab Chat → connessa a chiara-chat con 6 quick prompt
- Tab Crescita → form diagnosi margine, KPI table, To-Do Day 1, angoli vincitori
- Sidebar → Brand DNA collassabile, KPI snapshot (145 strutture, €82, 29% EBITDA)
- 4 sezioni con sessionId isolati: SMM / Operazioni / Campagne / Report

### ★ NUOVO — Protocollo Base Agenti (7 Fasi)
- File: PROTOCOL_AGENTE_CRESCITA.md
- REGOLA #0: Costo operativo ≤ 50% incasso — non negoziabile
- 7 Fasi: Diagnosi · Audit margini · Avatar ICA · KPI target · Business design · To-Do Day 1 · Marketing
- 6 KPI core: Lead · Agenda · Show-up · Cierre · AOV · Cancelación
- Angoli marketing: PAIN / GAIN / FEAR / CURIOSITY / PROOF / EDUCATION
- Tab Crescita integrata in entrambi gli hub (Marco + Chiara)

---

## 🔲 NODO 6 — Meta Ads Tavola dei Santi ← PROSSIMO

**Obiettivo:** Collegare Tavola dei Santi al BM Meta e lanciare prime campagne.

Stato:
- ✅ Account pubblicitario Meta: 1348377917008116
- ✅ Business Manager attivo
- ⏳ Tavola dei Santi da collegare al BM

### Step 6.1 — Collegare social al Business Manager
1. business.facebook.com → Impostazioni Business
2. Account Instagram → Aggiungi → credenziali Tavola dei Santi
3. Pagine Facebook → Aggiungi "Tavola dei Santi"
4. Assegna al portfolio Milagrowpartner

⚠️ SERVE: credenziali Instagram e Facebook di Tavola dei Santi

### Step 6.2 — Pixel Meta per tavoladeisanti.com
1. Business Manager → Origini dati → Pixel → Crea TavolaPixel
2. Installa nel <head> di tutti i file HTML
3. Configura eventi: PageView, ViewContent, Contact

### Step 6.3 — Prima campagna Awareness Colombia
- Obiettivo: Awareness · Budget: €20/giorno
- Geo: Bogotá (28–55) + Medellín (25–50)
- Interessi: cucina italiana, chef, gastronomia premium, vino
- Formato: Reel verticale (Marco genera copy) + carosello prodotto

### Step 6.4 — Connettere Meta API a n8n
- Credenziali Meta Graph API nel workflow 8.2a Instagram Publisher
- Scope: pages_manage_posts, instagram_content_publish
- Test pubblicazione automatica Marco → Meta

---

## ✅ NODO 7 — SEO Google (tavoladeisanti.com) — COMPLETATO 21/06/2026

- ✅ `robots.txt` corretto e ottimizzato
- ✅ `sitemap.xml` con hreflang aggiornata e inviata a Google
- ✅ Title tag + meta description ottimizzati su tutte le pagine
- ✅ Schema JSON-LD: FAQ, LocalBusiness, Product, BreadcrumbList
- ✅ Blog creato con 3 articoli SEO completi
- ✅ `tavoladeisanti.com` verificato su Google Search Console
- ✅ Deploy completato su Vercel (GitHub CI/CD)

---

## 🔲 NODO 8 — Pubblicazione Automatica n8n → Meta
*(Bloccato da Nodo 6.4)*

- Marco genera copy → workflow n8n → pubblica su IG/FB
- Human Approval Gate prima della pubblicazione
- Log pubblicazioni su Google Drive

---

## 🔲 NODO 9 — Meta Ads Palazzo Blue Arroyo
*(Dopo Nodo 6 completato)*

- Stesso processo ma per Palazzo Blue Arroyo
- Target: Property Manager Firenze 35–55 anni
- Chiara genera copy via palazzo_blue_arroyo_mktg

---

## 🔲 NODO 10 — Workflow Protocollo Crescita su n8n
*(Da fare per tutti i nuovi clienti)*

- Workflow n8n dedicato alla diagnosi aziendale (Fasi 1–7)
- Input: dati finanziari → output: pacchetto crescita strutturato
- SessionId: {cliente}_crescita

---

## 📁 RIFERIMENTI

### URL Live
- https://milagrowpartner.com — Sito principale Mila
- https://milagrowpartner.com/area-privata — Hub Marco (Tavola dei Santi)
- https://milagrowpartner.com/palazzo-blue-arroyo — Hub Chiara (Palazzo Blue Arroyo)
- https://tavoladeisanti.com — Sito Tavola dei Santi

### n8n Workflows Attivi
- mZuQfe4pv0Gu1szz — Marketing Team Blueprint v2.7.0 (Marco) — /webhook/chat
- oA3ZjaCx8HlG3tcl — Chiara Palazzo Blue Arroyo v1.0 — /webhook/chiara-chat
- 9nvad964T9VJU446 — PBA Sales Manager
- olxuKaB0xoxlA1ZI — PBA Operations Manager
- xEWmmWLCX4qY2gsn — PBA Admin Manager
- n5Hj58eRjYnUADht — PBA Daily CEO Briefing

---

## 🧭 ORDINE D'ESECUZIONE

PROSSIMO:
  Nodo 6: Meta Ads Tavola dei Santi
  → Serve: credenziali IG + FB di Tavola dei Santi

IN PARALLELO (dopo credenziali):
  Nodo 6.2: Pixel TavolaPixel sul sito
  Nodo 6.3: Prima campagna Awareness Colombia

DOPO NODO 6:
  Nodo 8: Pubblicazione automatica n8n → Meta
  Nodo 9: Meta Ads Palazzo Blue Arroyo

BACKLOG:
  Nodo 10: Workflow Protocollo Crescita su n8n

---
Piano aggiornato: 21 Giugno 2026 · Mila Grow Partner × Antigravity
Versione 2.0 — SEO Tavola completato · Brand DNA Marco v2.0 · Piano parametrizzato per cliente
