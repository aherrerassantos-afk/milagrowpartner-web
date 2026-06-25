# Redesign Home Page - Smartsbookings.com (Turismo di Pregio)

Riprogettazione della homepage di `smartsbookings.com` per allineare l'estetica a quella del portale di lusso "MMega Homes & Villas", ottimizzandola per i turisti.

## User Review Required

> [!IMPORTANT]
> - Utilizzeremo le immagini copiate da *Toscan Costruzioni* (`hero-villa.jpg`, `project-casale.jpg`, `project-appartamento.jpg`) per allestire l'Hero banner e la sezione "Esperienze".
> - Modificheremo il selettore delle lingue (IT / EN) e i link del menu per uniformarli allo stile del portale premium.

## Proposed Changes

### [Home Page]

#### [MODIFY] [page.tsx](file:///Users/andresjulianherrerasantos/smartsbookings.com/src/app/page.tsx)
Riprogettazione della struttura del file:
* **Header & Navigazione:**
  * Layout centrato con Logo in evidenza.
  * Menu di navigazione: *Dicono di Noi*, *Destinazioni*, *Appartamenti*, *Ville*, *Experience*, *Affidaci il tuo immobile*.
  * Selettore di lingua `IT / EN` a sinistra.
  * Pulsante CTA elegante "Uffici e contatti" a destra.
* **Hero Section:**
  * Immagine di sfondo full-width ad alto impatto visivo (`hero-villa.jpg`).
  * Titolo in font Serif elegante: *"Sei pronto per una vacanza indimenticabile?"*.
* **Widget di Ricerca (Booking Search Bar):**
  * Posizionato in sovrapposizione all'Hero (layout a scheda "floating" premium).
  * Banner superiore nero: `MIGLIORE TARIFFA GARANTITA | SELEZIONE DEGLI ESPERTI | ASSISTENZA CLIENTI | VIAGGIA IN SICUREZZA`.
  * Selettori di Check-in (Arrivo), Check-out (Partenza), Destinazione e numero Ospiti disposti in griglia orizzontale, con pulsante di ricerca con icona a lente d'ingrandimento.
* **Sezione Esperienze ("Emozioni uniche da provare"):**
  * Sottotitolo: *"Lezioni di cucina italiana, pranzo tra i vigneti, tramonti indimenticabili"*.
  * Griglia/Slider con le tre card fotografiche premium dell'esperienza toscana (`project-casale.jpg`, `project-appartamento.jpg`, `hero-villa.jpg`).
* **Banner Cookies:**
  * Banner scuro a comparsa in basso con opzioni *Approfondisci*, *Rifiuta*, *Accetta*.

## Verification Plan

### Manual Verification
* Avvio dell'app in modalità sviluppo (`npm run dev`) per controllare la resa visiva, la responsività su mobile e l'allineamento dei font e dei componenti grafici.
