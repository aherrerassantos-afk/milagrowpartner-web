---
name: marketing-agency-funnel-blueprint
description: "Spec ejecutable y referencia para construir el sistema de marketing end-to-end de una agencia de contenido: desde scout de tendencias y producción creativa hasta publicación pautada/orgánica, captura de lead y push de notificación por WhatsApp al equipo de ventas del cliente. Pensado para implementar en n8n con agentes IA, integrando con el workflow ya existente Marketing_Team_Blueprint_v1_3_0."
version: 1.4.0
compatibility: "Claude Code, Google Antigravity (Agent Skills format), n8n v1.70+"
existing_workflow: "Marketing_Team_Blueprint_v1_3_0.json"
language: "es"
changelog:
  - "1.4.0 — Autonomía 100%: eliminados los últimos approval gates dispersos (Trend Scout aprobación, Weekly Report aprobación de budgets). Los únicos puntos de contacto humano son los dos checkpoints (input/output) + las 3 excepciones operativas (herramientas nuevas, credenciales faltantes, pagos pendientes). Nueva sección 0.0 con el principio de autonomía total."
  - "1.3.0 — Arquitectura simétrica de dos checkpoints universales (Quality Input + Pre-Flight Output Report)."
  - "1.2.0 — Agregado Workflow E: Cold Email Outbound."
  - "1.1.0 — Agregadas plataformas: YouTube, TikTok Ads, Google Ads, blog autónomo."
  - "1.0.0 — Versión inicial: Meta Ads, Instagram orgánico, TikTok orgánico, WhatsApp Cloud API."
---

# Marketing Agency Funnel Blueprint

> **Cómo leer este documento.** Las primeras cuatro secciones son referencia conceptual (qué falta, por qué, cómo encaja). De la sección 5 en adelante es **spec ejecutable**: cada rol nuevo trae sistema-prompt, inputs/outputs y nodos n8n sugeridos. Claude Code o Antigravity pueden tomar las secciones marcadas como `## SPEC:` y materializarlas como JSON de n8n.

---

## 0. Los dos checkpoints universales (lectura obligatoria)

Antes de los workflows hay dos secciones que aplican a TODO lo que sigue:

- **Sección 0.A — Controllo Qualità Input**: define el form base + extensiones por workflow que se completa antes de disparar cualquier cooking.
- **Sección 9.ter — Pre-Flight Output Report**: define el formato del report final que un humano debe aprobar con "go for it" antes de cualquier acción online.

Estas dos secciones son el esqueleto de control del sistema. Las secciones de cada workflow asumen que ambas existen y las referencian.

### 0.0 Principio de autonomía total (lectura obligatoria antes que todo)

**El sistema corre con 100% de autonomía operativa.** Hay EXACTAMENTE dos momentos en los que el sistema requiere intervención humana del CEO/owner:

1. **Checkpoint 1 — Input**: completar el form de Quality Input Control cuando se inicia un nuevo run.
2. **Checkpoint 2 — Output**: responder "go for it" (o solicitar correcciones) en el Pre-Flight Output Report antes del go-live.

**Fuera de esos dos checkpoints, el sistema NUNCA molesta al CEO** salvo en estas 3 excepciones (que no son aprobaciones, son bloqueos físicos):

| Tipo de excepción | Ejemplo | Acción del sistema |
|---|---|---|
| **Herramienta nueva necesaria** | Un workflow nuevo necesita una integración que aún no está conectada (ej: agregar Calendly al pipeline) | Notificación con: qué herramienta, por qué, cuánto cuesta, link al setup. Pausa el workflow afectado hasta que se confirme. |
| **Credencial / acceso faltante** | Token de Meta Ads expiró y no se puede auto-renovar; cuenta de Smartlead pide MFA; dominio nuevo necesita verificación DNS | Notificación con: qué credencial, cómo otorgarla, link directo a la página de setup. Pausa el workflow afectado. |
| **Pago / fondos pendientes** | Saldo de Apify <€5 y campaña próxima necesita scraping; tarjeta de Meta Ads rechazada; renovación de dominio en 7 días | Notificación con: monto a pagar, dónde, deadline. Pausa solo el workflow que necesita esos fondos. |

**Todo lo demás se decide solo**: qué trends priorizar, qué creativos generar, qué audiencias targetear, cuándo publicar, cómo reasignar presupuesto entre adsets, cómo clasificar leads, qué follow-ups mandar, cuándo pausar un mailbox que tira bounces, etc. Para todo eso el sistema tiene autoridad delegada y solo deja registro en Airtable.

**Implementación práctica:** ningún nodo del sistema usa "Telegram Notify CEO" como gate. El único canal de comunicación bidireccional con el CEO es el Pre-Flight Output Report (Checkpoint 2). El resto son **alertas operativas** que llegan a un canal Telegram aparte (`#operations-alerts`) y solo aparecen cuando corresponde a una de las 3 excepciones de arriba.

---

## 0.A. Controllo Qualità Input (Checkpoint 1)

### 0.A.1 Propósito

Un brief malo cuesta dinero, tiempo y reputación. El Controllo Qualità Input es un **agente conversacional con form estructurado** que valida el input antes de que ningún token, credit o segundo de cómputo se gaste.

Reglas duras del agente:
1. No deja avanzar con respuestas vagas o placeholders ("lo que sea", "estándar", "como siempre").
2. Hace pushback inteligente: si el usuario responde algo débil, propone alternativas en vez de simplemente repreguntar.
3. Cuando algo falta y el usuario lo permite, marca el campo como `weak` en el output. El Pre-Flight Output Report (Checkpoint 2) los muestra como warnings.
4. El output siempre es un JSON estructurado que se escribe en Airtable `WorkflowRuns` con `status = input_validated` antes de disparar el workflow.

### 0.A.2 Arquitectura del form: base común + extensiones

El form tiene dos partes:

**Parte 1 — Base común** (siempre, todos los workflows): identifica quién pide qué, para qué cliente, con qué presupuesto de tiempo/dinero y dónde está el contexto.

**Parte 2 — Extensión específica del workflow**: preguntas adicionales que dependen de A/B/C/D/E. El agente decide qué extensión cargar leyendo el campo `workflow_target` de la Parte 1.

### 0.A.3 Form base común (Parte 1)

| # | Campo | Validación |
|---|---|---|
| 1 | `requester_name` | requerido, free text |
| 2 | `brand_id` | requerido, debe existir en Airtable `Brands` (autocompletado de lista) |
| 3 | `workflow_target` | requerido, enum: discovery / production / distribution / performance_review / cold_email |
| 4 | `business_objective` | requerido, free text. Validación: debe contener al menos un verbo de resultado (vender, generar leads, posicionar, fidelizar, etc.) y un sustantivo medible. Rechaza "más visibilidad" → pide "qué métrica concreta querés mover y cuánto". |
| 5 | `success_metric` | requerido, free text. Ejemplo aceptable: "10 leads calificados/semana", "CTR > 1.5%", "30 reservas/mes". Rechaza "que funcione". |
| 6 | `deadline` | requerido, fecha. Validación: si <72h y el workflow pedido normalmente tarda más, alerta de incompatibilidad. |
| 7 | `budget_eur` | opcional para A/B/D, requerido para C/E. Si requerido y vacío, pide número. |
| 8 | `language` | requerido, default = idioma del brand en Airtable. |
| 9 | `context_attachments` | opcional pero **muy recomendado**: URLs a brand guidelines, decks previos, ejemplos de competencia, briefs anteriores. Si vacío, el agente pregunta "¿hay algún material previo que deba conocer?" antes de marcarlo vacío. |
| 10 | `non_negotiables` | opcional. Cosas que NO se pueden hacer (ej: "no mencionar al competidor X", "no usar fotos de comida con flash"). El agente las inyecta como hard constraint en todos los prompts downstream. |

### 0.A.4 Extensiones por workflow

#### Extensión Workflow A — Discovery
| # | Campo | Notas |
|---|---|---|
| A1 | `discovery_scope` | enum: trending_now / evergreen_seo / competitor_gap / new_audience |
| A2 | `geography_focus` | array de países o regiones |
| A3 | `time_window` | enum: last_7d / last_30d / last_90d (qué tan reciente debe ser el trend) |
| A4 | `excluded_topics` | trends que ya se trabajaron y no queremos repetir |

#### Extensión Workflow B — Production
| # | Campo | Notas |
|---|---|---|
| B1 | `media_type` | image / video_generate / video_edit (lo que ya tenés en tu schema) |
| B2 | `channel` | instagram / tiktok / youtube / linkedin / blog / multi |
| B3 | `format` | feed_post / reel / story / short / long_form / carousel |
| B4 | `funnel_stage` | TOFU / MOFU / BOFU |
| B5 | `variant_count` | integer, default 3 |
| B6 | `key_message` | requerido, max 200 chars. Validación: debe responder "qué quiero que el viewer entienda en 1 frase". |
| B7 | `reference_url` | opcional |
| B8 | `mood` y `style_notes` | opcionales |

#### Extensión Workflow C — Distribution & Funnel
| # | Campo | Notas |
|---|---|---|
| C1 | `pieces_ids` | array de Piece IDs aprobadas en Workflow B |
| C2 | `publishing_targets` | multi-select: instagram_organic / tiktok_organic / youtube / blog / meta_ads / tiktok_ads / youtube_ads / google_ads |
| C3 | `campaign_budget_per_platform` | si publishing_targets incluye ads, objeto con budget por plataforma |
| C4 | `landing_url` | requerido si hay ads o si CTA pide landing |
| C5 | `whatsapp_notify_numbers` | requerido, default = `sales_team_whatsapp_numbers` del brand |

#### Extensión Workflow D — Performance Review
| # | Campo | Notas |
|---|---|---|
| D1 | `review_window_days` | default 7 |
| D2 | `platforms_to_include` | multi-select |
| D3 | `comparison_baseline` | enum: previous_period / brand_average / industry_benchmark |

#### Extensión Workflow E — Cold Email Outbound
| # | Campo | Notas |
|---|---|---|
| E1 | `target_sector` | objeto: {industry, sub_niche, company_size, geography, additional_filters} |
| E2 | `icp_decision_maker` | objeto: {titles[], department, seniority} |
| E3 | `sharp_proposition` | max 200 chars. Validación: debe incluir resultado concreto + plazo + diferenciador. |
| E4 | `credibility_proof` | case study + métrica, o garantía/trial alternativo |
| E5 | `cta_type` | enum: reply / book_call / watch_loom_reply |
| E6 | `cta_link` | requerido si cta_type ≠ reply |
| E7 | `target_volume` | integer. Validación contra capacidad de mailboxes disponibles. |
| E8 | `mailboxes_to_use` | array de Mailbox IDs de Airtable EmailMailboxes |
| E9 | `compliance_region` | enum: EU / UK / US / CA / LATAM / other |

> **Nota**: la extensión E es prácticamente el `Pre-Flight Interview Agent` del Workflow E (nodo E1) que ya existía en v1.2.0. En v1.3.0 lo formalizamos como **extensión** del Quality Input Control universal, no como un agente aparte. La lógica conversacional sigue siendo la misma.

### 0.A.5 SPEC: agente `Quality Input Control`

- **Tipo**: `@n8n/n8n-nodes-langchain.agent` con `memoryBufferWindow` + `outputParserStructured` + sub-workflow para cargar extensión dinámica
- **Modelo**: Claude Sonnet 4.6 (necesita razonamiento conversacional + pushback)
- **System prompt**:

```
Sos el Quality Input Control. Tu trabajo es transformar un pedido vago
del usuario en un brief estructurado, completo y accionable.

PROCESO:

1) Saludá y preguntá: "¿qué workflow querés correr?"
   Opciones: discovery / production / distribution / performance_review
   / cold_email.

2) Una vez identificado workflow_target, hacé las preguntas de la
   PARTE 1 (form base) UNA por vez, en orden.

3) Después de Parte 1, cargá la EXTENSIÓN correspondiente al workflow
   elegido y hacé esas preguntas UNA por vez.

REGLAS DURAS:

- Si el usuario responde algo vago ("PYMEs", "lo que funcione", "como
  siempre"), NO aceptás. Pedís especificidad con ejemplos.
- Si el usuario insiste en avanzar con un campo débil, lo aceptás
  pero lo marcás en weak_fields[].
- Si detectás incoherencia entre campos (ej: deadline 24h + workflow E
  que necesita 14 días de warmup), lo planteás como bloqueante.
- Si non_negotiables incluye algo que choca con la oferta del brand,
  lo señalás antes de avanzar.

AL FINAL:

Mostrá un resumen del brief completo y preguntá literalmente:
"¿confirmás este brief para arrancar el cooking? (sí / corrijo / cancelo)"

Si "sí" → devolvé el JSON final y escribí en Airtable WorkflowRuns
con status = input_validated.

Si "corrijo" → preguntá qué campo y volvé al loop.

Si "cancelo" → devolvé status = cancelled_by_user, no escribas nada.

OUTPUT JSON SCHEMA (al final):
{
  "workflow_run_id": "uuid",
  "workflow_target": "string",
  "base": { ... todos los campos de Parte 1 },
  "extension": { ... todos los campos de la extensión },
  "weak_fields": ["string"],
  "warnings": ["string"],
  "confirmed_at": "ISO timestamp",
  "confirmed_by": "requester_name"
}
```

### 0.A.6 Dónde se invoca

- En todos los workflows, el **primer nodo** después del trigger es siempre `Quality Input Control`.
- El trigger puede ser: chat manual, cron schedule (en cuyo caso el form se pre-rellena desde una `Brands.default_*` y solo pide confirmación), o webhook (que debe traer el JSON ya armado y el agente solo valida).
- Sin `status = input_validated` en Airtable, ningún nodo downstream se ejecuta. Esto es enforced con un IF node al inicio de cada workflow.

---

## 1. Objetivo del sistema

Correr una agencia de contenido que para cada cliente gestione, de punta a punta:

1. **Discovery** de tendencias y oportunidades por nicho (lo que falta hoy).
2. **Producción creativa** de la pieza (lo que ya hace `Marketing_Team_Blueprint_v1_3_0`).
3. **Distribución** pautada (Meta Ads) y orgánica (publicación programada).
4. **Captura de lead** desde el creativo hasta el formulario o conversación.
5. **Notificación push por WhatsApp** al equipo de ventas del cliente con la info del lead estructurada.
6. **Loop de performance** que aprende de lo que funciona y alimenta el discovery del próximo ciclo.

El sistema debe responder por la marca de varios clientes a la vez, así que el diseño favorece:

- **Multi-tenancy**: todo lo que hoy vive en la dataTable `2 Brand Context` debe poder escalar a 10-20 marcas sin reescribir el flujo.
- **Autonomía total con dos checkpoints**: el sistema decide solo en todo, salvo dos momentos puntuales — completar el input form al inicio, y responder "go for it" al output report antes del go-live (ver sección 0.0).
- **Trazabilidad**: cada lead se puede rastrear hasta el creativo, la campaña y la tendencia que lo originaron.

---

## 2. Arquitectura general: cuatro workflows + dos checkpoints universales

Todo el sistema está envuelto por dos puntos de control que aplican a **cualquier** workflow (A/B/C/D/E):

```
                  ┌──────────────────────────────────────┐
                  │  CHECKPOINT 1 — CONTROLLO QUALITÀ   │
                  │  INPUT                               │
                  │  (form estructurado antes del        │
                  │   cooking — base común +             │
                  │   extensiones por workflow)          │
                  └──────────────────┬───────────────────┘
                                     ▼
       ┌────────────────────────────────────────────────────┐
       │                                                    │
       │   ┌─────────┐  ┌─────────┐  ┌─────────┐           │
       │   │   WF A  │  │   WF B  │  │   WF C  │           │
       │   │Discovery│─▶│ Product.│─▶│Distrib. │           │
       │   └─────────┘  └─────────┘  └─────────┘           │
       │                                  ▲                 │
       │                                  │                 │
       │   ┌─────────┐                ┌─────────┐           │
       │   │   WF D  │◀───────────────│   WF E  │           │
       │   │Perform. │                │Cold     │           │
       │   │Loop     │                │Email    │           │
       │   └─────────┘                └─────────┘           │
       │              C O O K I N G                         │
       └────────────────────┬───────────────────────────────┘
                            ▼
                  ┌──────────────────────────────────────┐
                  │  CHECKPOINT 2 — PRE-FLIGHT OUTPUT   │
                  │  REPORT                              │
                  │  (report unificado del output        │
                  │   completo → revisión humana →       │
                  │   correcciones → "go for it")        │
                  └──────────────────┬───────────────────┘
                                     ▼
                  ┌──────────────────────────────────────┐
                  │  G O   L I V E                       │
                  │  (publicar / enviar / activar)       │
                  └──────────────────────────────────────┘
```

**Principio rector**: hay UN solo punto donde un humano dice "go" y el sistema ejecuta acciones irreversibles online (publicar, enviar emails, activar gasto). Todos los micro-approvals que existían dispersos (uno antes de Drive upload, otro antes de Meta API, otro antes de Smartlead, etc.) se consolidan en el Checkpoint 2.

**Por qué dos checkpoints y no uno solo:**
- Checkpoint 1 (input) ahorra **tokens y credits**: si el brief está mal definido, mejor frenar antes de quemar Apify, Apollo, Flux, etc.
- Checkpoint 2 (output) ahorra **reputación y gasto online**: si el resultado del cooking no convence, mejor frenar antes de tocar inboxes ajenos, presupuestos de ads o el dominio del cliente.

### 2.1 Los 4 workflows

- **Workflow A — Discovery**: corre semanal, busca tendencias por nicho, guarda en Airtable. Alimenta a B.
- **Workflow B — Production**: tu blueprint actual mejorado. Lee de Airtable, produce piezas creativas.
- **Workflow C — Distribution & Funnel**: lee piezas listas, publica orgánico, sube creativos a las 4 plataformas de ads, escucha leads, notifica al equipo de ventas via WhatsApp.
- **Workflow D — Performance Loop**: lee métricas multi-plataforma, sintetiza aprendizajes, los inyecta como contexto en A y B.
- **Workflow E — Cold Email Outbound**: prospección B2B activa. Las respuestas positivas entran al mismo pipeline de leads del Workflow C.

> **Cómo se distinguen C y E**: C es inbound (el lead viene a vos a través del contenido o un ad). E es outbound (vos vas a buscar al lead que ni te conoce). Ambos terminan en la misma `Leads` table de Airtable y disparan la misma notificación WhatsApp al equipo de ventas del cliente, pero los workflows previos son completamente distintos.

---

## 3. Mapa de roles: existentes vs. nuevos

### 3.1 Lo que ya cubre `Marketing_Team_Blueprint_v1_3_0`

| Rol | Nodo actual | Función |
|---|---|---|
| Briefing Director | `1 Briefing Director` (Gemini) | Extrae brief estructurado del chat |
| Brand Context | `2 Brand Context` (dataTable) | Tono, visual style, lo que no se dice |
| Reference Analyzer | `2.5 Reference Analyzer` (Gemini) | Convierte URL de referencia en cues visuales |
| Strategy Director | `3 Strategy Director` (Gemini) | Ángulo, USP, insight, CTA |
| Copywriter | `4 Copywriter` (Gemini) | Copy adaptado al canal |
| Art Director | `5a Art Director` (Gemini) | Prompt visual borrador para Flux |
| Design Critic | `5a.5 Claude Design Critic` (Claude) | Refina prompt con criterio Emil Kowalski |
| Image Generator | `6a Flux Predict` (Replicate) | Genera imagen |
| Video Director | `5b Video Director` (Gemini) | Prompt video para LTX |
| Video Generator | `6b Video Predict` (Replicate) | Genera video |
| Video Editor | `5c Video Editor` (Gemini) | Devuelve un *plan de edición* (no edita) |
| Storage | `7a/7b Drive Upload` | Sube assets a Google Drive |

### 3.2 Roles nuevos a sumar (gap analysis)

| Rol nuevo | Workflow | Por qué falta | Resuelve |
|---|---|---|---|
| **Trend Scout** | A | El "Reference Analyzer" actual analiza una URL que vos le pasás. No busca trends. | Discovery proactivo por nicho |
| **SEO Strategist** | A / B | No existe. El flujo nunca toca keywords ni search intent. | Contenido evergreen + tráfico orgánico de búsqueda |
| **Funnel Stage Classifier** | B | El brief no captura TOFU/MOFU/BOFU. Toda pieza se trata igual. | Copy y creativos diferenciados por etapa del embudo |
| **Variant Generator** | B | Se genera 1 sola pieza. No hay A/B. | Test de hooks/ángulos sin reescribir el brief |
| **Quality Input Control** + **Pre-Flight Output Reporter** | TODOS | Los antiguos "Approval Gatekeepers" dispersos se eliminan. | Único punto de contacto humano: input al inicio + report con "go for it" al final. Ver secciones 0.A y 9.ter. |
| **Social Media Publisher (IG/FB/TikTok)** | C | No hay scheduling ni publicación. | Publicación orgánica programada multi-canal |
| **YouTube Publisher & SEO** | C | No existe. YouTube es el segundo buscador del mundo. | Publicación de Shorts y long-form con metadata SEO-optimizada |
| **Blog Autonomous Publisher** | C | No existe. El SEO Strategist solo recomienda. | Publicación directa de posts SEO sobre el trend del momento |
| **Meta Ads Campaign Manager** | C | No existe. No sube nada a Meta Ads. | Creación y push de creativos a campañas pautadas |
| **TikTok Ads Campaign Manager** | C | No existe. | Campañas pautadas en TikTok Ads Manager |
| **YouTube Ads Campaign Manager** | C | No existe. | Campañas video pautadas (in-stream, Shorts ads, Discovery) |
| **Google Ads Campaign Manager** | C | No existe. Falta capturar demanda activa (search). | Campañas Search + Performance Max para BOFU |
| **Landing Page / Form Builder** | C | No hay captura de lead. | Punto de aterrizaje del clic pago/orgánico |
| **Lead Qualifier** | C | No existe. | Enriquece y puntúa el lead antes de notificar |
| **WhatsApp Sales Notifier** | C | No existe. | Push estructurado al equipo de ventas del cliente |
| **Conversation Router** | C | No existe. | Maneja respuestas iniciales si el lead llega por WhatsApp |
| **Pre-Flight Campaign Interview** | E | No existe. | Entrevista al usuario antes de cada cold email campaign (sector, ICP, propuesta sharp) |
| **Prospect Scout (Maps + Web)** | E | No existe. | Encuentra empresas que matchean el ICP via Google Maps + búsquedas web |
| **Data Enrichment & Recovery** | E | No existe. | Recupera datos de contacto (sobre todo email del decision-maker) a partir de la empresa |
| **Email Verifier** | E | No existe. | Valida sintaxis + MX + catch-all + bounces antes de enviar |
| **Cold Email Copywriter** | E | No existe. Distinto al copywriter de social. | Escribe asunto + cuerpo + follow-ups con personalización a escala |
| **Email Sequence Manager** | E | No existe. | Orquesta secuencia 3-5 touches via Smartlead API |
| **Inbox Reply Router** | E | No existe. | Clasifica respuestas (interesado / no / out-of-office / unsubscribe) y rutea |
| **Performance Analyst** | D | No existe. Sin loop. | Cierra el ciclo: aprende de pautado + orgánico + cold email |
| **Budget Optimizer** | D | No existe. | Reasigna presupuesto entre adsets según performance |

24 roles nuevos. Algunos son agentes IA, otros son nodos de integración pura, otros son humanos en el loop. Cada plataforma de pautado (Meta, TikTok, YouTube, Google) tiene su propio Campaign Manager Agent porque las lógicas de bidding, formatos y objetivos son distintas: forzar un solo agente "multi-plataforma" da resultados mediocres en todas. Lo mismo aplica a cold email: el copywriting outbound es un oficio aparte del social.

---

## 4. Funnel end-to-end (vista del lead)

Cómo una tendencia detectada el lunes se convierte en un lead notificado por WhatsApp el viernes:

```
[Lunes 9:00]    Trend Scout detecta "hashtag X creciendo +40% en nicho hospitality"
                → guarda en Airtable.Trends con score 8/10
                → no notifica al CEO (decisión autónoma)

[Lunes 10:00]   SEO Strategist cruza el trend con keywords del cliente
                → propone ángulo "Cómo X resuelve Y para [audiencia]"
                → Auto-trigger: dispara Workflow B con brief pre-rellenado

[Lunes 10:01]   Workflow B arranca con su Checkpoint 1 (Quality Input
                Control) que valida el brief auto-generado contra
                Brands.context y completa campos faltantes con defaults
                inteligentes (sin molestar al CEO).

[Lunes 11:00]   Production cocina las 3 variantes completas
                → genera Pre-Flight Output Report (Checkpoint 2)
                → notifica al CEO por Telegram (PRIMERA VEZ EN EL DÍA)

[Lunes 14:00]   CEO responde "go for it" desde el celular
                → Workflow B marca pieces como ready_to_publish
                → Auto-trigger: Workflow C arranca

[Lunes 14:05]   Workflow C cocina: estructura de campañas en 4 plataformas,
                copy de publicación orgánica, landing form
                → genera Pre-Flight Output Report (Checkpoint 2)
                → notifica al CEO

[Lunes 17:00]   CEO responde "go for it"
                → Sistema ejecuta TODO en paralelo:
                  - Publica orgánico programado en IG/TikTok/YouTube
                  - Activa campañas Meta + TikTok + YouTube + Google Ads
                  - Activa landing + webhook lead capture
                  - Activa Click-to-WhatsApp si aplica

[Martes 14:00]  Primer lead llena el form
                → Lead Qualifier enriquece y puntúa autónomo (score 7/10)
                → WhatsApp Sales Notifier dispara mensaje al equipo de
                  ventas del cliente (autónomo, no pasa por CEO)

[Miércoles+]    Performance Analyst lee métricas cada 24h
                → al día 3, variante A tiene 3x CTR de variante B
                → Budget Optimizer pausa B y duplica budget de A
                  (autónomo, respeta reglas duras de 30% máximo
                   y cap mensual)
                → Log queda en Airtable.BudgetChanges

[Viernes]       Performance Analyst sintetiza la semana
                → escribe en Airtable.Learnings y WeeklyReports
                → NO notifica al CEO
                → Los Learnings se inyectan auto-mágicamente como
                  contexto en próximos Workflow B
```

**Resumen del recorrido**: 5 días de operación, el CEO fue molestado 2 veces (Lunes 11:00 y Lunes 14:05) para responder "go for it" en los dos Pre-Flight Output Reports. Todo lo demás corrió solo.

---

## 5. Stack tecnológico recomendado

Como elegiste "decidilo vos", el criterio fue: APIs oficiales o quasi-oficiales, n8n-friendly, costo bajo para arrancar, escalable. Cada herramienta lista el precio ballpark y la **alternativa** por si la principal no encaja.

### 5.1 Capa de datos y orquestación

| Función | Principal | Alternativa | Notas |
|---|---|---|---|
| Single source of truth | **Airtable** (free hasta 1000 records/base) | Notion DBs, NocoDB self-hosted | n8n tiene nodo nativo |
| Orquestación | **n8n** (self-host o cloud) | Make.com | Ya lo usás |
| Almacenamiento de assets | **Google Drive** | Cloudflare R2 | Ya lo usás |
| Comunicación CEO ↔ sistema | **Telegram Bot** (2 canales: `#checkpoints` para input/output reports, `#operations-alerts` para las 3 excepciones de autonomía) | Slack, n8n Form trigger | Telegram es gratis. El bot recibe respuestas en texto, no botones. |

### 5.2 Discovery (Workflow A)

| Función | Principal | Alternativa | Notas |
|---|---|---|---|
| Trends generales | **Google Trends** (vía SerpAPI o pytrends) | Glimpse, Exploding Topics API | SerpAPI tiene tier free 100 req/mes |
| TikTok trends | **TikTok Creative Center** (scrape o API no-oficial) | ScrapeCreators, TikAPI | Creative Center no tiene API oficial, hay que scrapear o usar un wrapper |
| Meta competidor ads | **ScrapeCreators API** ($1/1000 ads) o Apify | Adyntel, SociaVault | El API oficial de Meta Ad Library es limitado para uso comercial |
| Keywords SEO | **DataForSEO API** (pay-as-you-go) | Serper.dev, Keywords Everywhere | Más barato que Ahrefs/Semrush para arrancar |
| Reddit/foros | **Reddit API** (free 100 req/min auth) | RSS de subreddits | Útil para detectar "pains" reales |

### 5.3 Distribución orgánica (Workflow C)

| Función | Principal | Alternativa | Notas |
|---|---|---|---|
| Publicación orgánica IG/FB | **Meta Graph API** (Instagram Content Publishing) | Metricool API, Publer API | Free, requiere cuenta Business + token long-lived |
| Publicación TikTok orgánico | **TikTok Content Posting API** | Scheduler manual + recordatorio | Free, requiere aprobación de app (~1-2 semanas según TikTok). Desde enero 2026 obliga Business Account verificado. |
| Publicación YouTube (Shorts + long-form) | **YouTube Data API v3** | Manual via Studio | Free hasta 10K unidades/día. Desde dic 2025 el costo de upload bajó: ~100 uploads/día con quota default (antes eran 6). |
| Publicación LinkedIn | **LinkedIn Marketing API** | Manual | Más burocrático |
| **Blog autónomo (sitio propio)** | **Ghost API** o **WordPress REST API** | Astro + GitHub Actions + n8n webhook | Ghost es el más rápido para arrancar; WordPress si el cliente ya tiene infra. Ver sección 8.5. |
| Publicación cross-platform unificada (fallback) | Metricool API, Buffer API | Postiz (open source) | Si APIs nativas se rompen |

### 5.3.bis Distribución pautada (Workflow C — branch ads)

| Plataforma | API principal | Notas críticas |
|---|---|---|
| **Meta Ads** (Facebook + Instagram) | Meta Marketing API (Graph v21+) | Free. n8n tiene HTTP request + credential predefinida. |
| **TikTok Ads** | TikTok Marketing API (`business-api.tiktok.com`) | Free. Requiere Business Center verificado + business registration cert. Sandbox para desarrollo, audit para producción. Tokens duran 24h, refresh tokens 365d. |
| **YouTube Ads** | **Google Ads API** (las campañas de YouTube se gestionan desde Google Ads, NO desde YouTube Data API) | Ver fila Google Ads. |
| **Google Ads** (Search + Performance Max + YouTube Ads) | Google Ads API v17+ | Free. Requiere developer token (process de aprobación: ~1-3 días para Test → semanas para Standard). n8n tiene nodo built-in `Google Ads node` con operaciones básicas; lo avanzado vía HTTP Request con misma credential OAuth2. Hay community node `@zhibinyang/n8n-nodes-google-ads` para operaciones extendidas. |
| Landing pages | **Tally** (forms + landings) | Carrd, Webflow, Unbounce, página propia en Astro/Next | Tally es el más rápido; Astro si querés control total y SEO máximo |
| Email transaccional | **Resend** (3K emails free/mes) | Brevo, Postmark | Si el funnel incluye email |

### 5.4 Lead y notificación (Workflow C)

| Función | Principal | Alternativa | Notas |
|---|---|---|---|
| WhatsApp outbound | **WhatsApp Cloud API directo** (sin BSP) | Twilio, 360dialog | Meta cobra por template message desde 2025. Service conversations (inbound) siguen gratis. Click-to-WhatsApp ads dan 72h gratis. |
| Lead enrichment | **Clearbit** (deprecado) → **Apollo.io** free tier | Hunter.io, Lusha | Para emails B2B |
| Scoring | Lógica propia en n8n + Claude | HubSpot, ActiveCampaign | Mantener simple al principio |

### 5.4.bis Cold Email Outbound (Workflow E)

| Función | Principal | Alternativa | Notas |
|---|---|---|---|
| Búsqueda de empresas en Google Maps | **Apify Google Maps Scraper** (~$3-7 / 1000 leads) | Outscraper (similar precio), Scrap.io | ~10x más barato que Places API oficial ($32/1000) y devuelve más campos. La Places API New oficial sigue siendo mejor para apps de producción en tiempo real, no para prospección masiva. |
| Búsqueda complementaria web | **Serper.dev** o **SerpAPI** | Google Custom Search | Para captar empresas que no están en Maps (B2B puro sin oficina física) |
| Enrichment de decision-maker email | **Apollo.io API** (75 emails free/mes, luego ~$0.01/email) | Hunter.io, Prospeo, RocketReach | Apollo tiene la base de contactos B2B más grande, integra LinkedIn data |
| Email verification | **Million Verifier** (~$0.0004/email) o **NeverBounce** | EmailListVerify, ZeroBounce | Crítico antes de enviar; bounce rate >5% mata el dominio |
| Cold email sending + warmup + sequences | **Smartlead** (~$39/mes Basic, $94 Pro) | Instantly ($47-97), Lemlist | Smartlead gana para agencias multi-cliente: workspaces separados por cliente, unlimited inboxes desde plan básico, API + webhook + integración n8n nativa, master inbox para gestionar respuestas. Instantly es más simple pero más caro a escala. |
| DNS / dominios secundarios | **Cloudflare Registrar** | Namecheap, Porkbun | Para cold email NO usar el dominio principal del cliente. Comprar 2-3 dominios secundarios (variaciones: get-clientname.com, try-clientname.com) y warmearlos antes de enviar. |
| Inbox provider para sending | **Google Workspace** ($6/usuario/mes) o **Microsoft 365** | Privateemail, Zoho | Mailboxes dedicados para outbound; nunca mezclar con el inbox real del cliente. Regla práctica: 3-5 mailboxes por dominio, 30-50 emails/día por mailbox. |

### 5.5 Performance (Workflow D)

| Función | Principal | Alternativa | Notas |
|---|---|---|---|
| Métricas Meta | **Meta Insights API** | Supermetrics | Free vía Graph API |
| Métricas orgánicas IG | **Meta Graph API** (Instagram Insights) | Iconosquare API | Mismo token |
| Métricas TikTok | **TikTok Display API** | Scrape propio | Si está aprobado |
| Análisis y síntesis | **Claude Opus** vía API | Gemini 2.5 Pro | Para razonamiento sobre los datos |

### 5.6 Modelos IA (lo que ya usás + lo que conviene sumar)

| Tarea | Modelo recomendado | Por qué |
|---|---|---|
| Briefing, extracción estructurada | Gemini 2.5 Flash | Barato, rápido, lo que ya usás |
| Strategy & insight | **Claude Sonnet 4.6** | Mejor razonamiento que Flash para angles estratégicos |
| Copywriting | Claude Sonnet 4.6 o Gemini 2.5 Pro | Calidad de prosa superior |
| Design critic | Claude Sonnet 4.6 (lo que ya usás) | Mantener |
| Image gen | Flux Schnell (lo que ya usás) | Mantener; subir a Flux Pro para finales si calidad lo pide |
| Video gen | LTX Video (lo que ya usás) | Mantener; evaluar Kling o Veo 3 para hero pieces |
| Performance analysis | Claude Opus 4.7 | Razonamiento profundo sobre datos cruzados |
| Conversational lead routing | Claude Haiku 4.5 | Latencia baja para responder en WhatsApp |

> **Single point of failure ya detectado**: hoy 6 agentes corren sobre Gemini 2.5 Flash. Diversificar al menos Strategy y Copywriter a Claude reduce riesgo si Gemini cambia precio o disponibilidad.

---

## 6. SPEC: Workflow A — Discovery & Strategy

### 6.1 Trigger
- **Cron**: lunes 09:00 hora local del cliente.
- **Manual**: webhook para ejecutar on-demand desde el chat del CEO.

### 6.2 Nodos secuenciales

#### Nodo A1: `Brand Loop`
Lee de Airtable `Brands` todos los brands con `status = active`. Itera el resto del workflow por cada uno.

#### Nodo A2: `Trend Scout Agent`
- **Tipo**: `@n8n/n8n-nodes-langchain.agent`
- **Modelo**: Gemini 2.5 Flash (volumen alto, tareas simples de síntesis)
- **System prompt**:

```
Sos el Trend Scout de una agencia de marketing. Tu trabajo es detectar
oportunidades de contenido para una marca específica.

INPUT: brand (nombre, nicho, tono, audiencia), región objetivo.

PROCESO:
1) Vas a recibir resultados crudos de 4 fuentes: Google Trends,
   TikTok Creative Center, Meta Ad Library de competidores, Reddit.
2) Identificá 3-5 señales que sean RELEVANTES para esta marca, no
   solo populares. Una señal relevante combina:
   - momentum (creciendo, no ya saturada)
   - fit con la audiencia del brand
   - hueco que la marca puede llenar (no es solo "lo mismo que hace
     todo el mundo")
3) Para cada señal devolvé:
   - title: nombre corto del trend
   - source: dónde la viste
   - momentum_score: 1-10 (qué tan en alza está)
   - fit_score: 1-10 (qué tan bien encaja con esta marca)
   - hook_idea: 1 frase con un ángulo posible
   - funnel_stage_sugerido: TOFU / MOFU / BOFU

OUTPUT: JSON array de máximo 5 señales. Sin preámbulo.
```

- **Tools / nodos previos que alimentan input**:
  - HTTP Request a SerpAPI Google Trends (categoría del brand)
  - HTTP Request a ScrapeCreators TikTok (hashtags trending del nicho)
  - HTTP Request a ScrapeCreators Meta Ad Library (top 3 competidores del brand)
  - HTTP Request a Reddit API (top posts últimos 7 días de subreddits relevantes)

#### Nodo A3: `Airtable Write — Trends`
Guarda cada señal como row en `Trends` con `status = pending_review`.

#### Nodo A4: `SEO Strategist Agent`
- **Modelo**: Claude Sonnet 4.6
- **System prompt**:

```
Sos el SEO Strategist. Para cada trend detectado, evaluás si tiene
potencial SEO (búsqueda orgánica sostenida) además del valor social
de corto plazo.

INPUT: trend (title, hook_idea, brand context).

PROCESO:
1) Generá 3 keyword variants relacionadas con el trend.
2) Para cada una indicá search_intent: informational, navigational,
   transactional, commercial.
3) Sugerí si vale la pena pieza evergreen (blog post, video YouTube)
   además del social de corto plazo.

OUTPUT: JSON con keyword_opportunities array + evergreen_recommendation
boolean + reasoning (max 50 palabras).
```

- **Integración opcional**: HTTP a DataForSEO para validar volumen real de las keywords antes de devolverlas.

#### Nodo A5: `Airtable Write — Brief Proposals`
Combina trend + SEO en un row en `BriefProposals` con `status = auto_approved` (el sistema decide solo qué trends ameritan brief, sin gate humano). Los BriefProposals con score combinado ≥ 7 (momentum + fit + SEO) disparan automáticamente Workflow B.

#### Nodo A6: `Auto-trigger Workflow B`
Lee los BriefProposals con `status = auto_approved` y `combined_score ≥ 7` y dispara Workflow B para cada uno con el brief pre-rellenado. El Workflow B arrancará en su propio Checkpoint 1 (Quality Input Control) que validará el brief auto-generado antes de cocinar.

> **Nota sobre autonomía**: el Trend Scout NO molesta al CEO para "elegir trends". Decide solo. La revisión humana sustantiva ocurre recién en el Pre-Flight Output Report del Workflow B, donde el CEO ve la pieza ya cocinada y decide si va online.

---

## 7. SPEC: Workflow B — Production (mejoras al blueprint actual)

### 7.1 Cambios al brief schema (`Brief Schema` outputParser)

Agregar campos al JSON schema actual:

```json
{
  "funnel_stage": "TOFU | MOFU | BOFU",
  "variant_count": "integer, default 3",
  "trend_source_id": "string, ref to Trends table",
  "campaign_id": "string, ref to Campaigns table, optional",
  "publishing_targets": ["instagram_organic", "instagram_ads", "tiktok_organic"]
}
```

### 7.2 Nuevo nodo: `Funnel Stage Classifier`
Si el brief no trae `funnel_stage` explícito, este agente lo infiere del `key_message`.

- **Modelo**: Gemini 2.5 Flash
- **System prompt**:

```
Clasificás un brief de marketing en una de 3 etapas del funnel:

TOFU (awareness): no conoce el problema o la marca. Hook educativo,
emocional, entretenido. Sin CTA agresivo.

MOFU (consideration): conoce el problema, evalúa soluciones. Demuestra
diferenciales, prueba social, contenido comparativo.

BOFU (decision): listo para comprar. CTA directo, oferta, urgencia,
remoción de fricción.

INPUT: key_message del brief.
OUTPUT: SOLO uno de: TOFU, MOFU, BOFU.
```

### 7.3 Modificación: `Strategy Director` recibe contexto extra

Cambiar el prompt del Strategy Director para que reciba además:
- `funnel_stage`
- Últimos 3 `Learnings` del brand desde Airtable (Workflow D los escribe)

Esto cierra el loop: cada nueva estrategia se construye sabiendo qué funcionó antes.

### 7.4 Nuevo nodo: `Variant Generator`
Después del Copywriter, antes del Art Director, generar N variantes (default 3) de hooks distintos para el mismo key_message.

- **Modelo**: Claude Sonnet 4.6
- **System prompt**:

```
Recibís un copy base y generás {variant_count} variantes que mantienen
el key_message pero cambian el HOOK inicial. Cada variante usa un
ángulo distinto:

Variante A: pain-led ("¿Cansado de X?")
Variante B: outcome-led ("Imaginá Y...")
Variante C: contrarian ("Todos dicen X, pero...")
(adaptá si pediste >3)

OUTPUT: JSON array, cada item con {variant_label, hook, full_copy}.
```

Cada variante luego pasa por el Art Director / Video Director independientemente, produciendo N creativos.

### 7.5 ~~Approval Gatekeeper~~ → reemplazado por Checkpoint 2

A partir de v1.3.0, el approval intermedio antes de subir a Drive **se elimina**. El Workflow B ahora ejecuta el cooking completo (Variant Generator → Art Director → Critic → Flux → Drive) y al final genera el **Pre-Flight Output Report** (ver sección 9.ter) que muestra las N variantes con preview y espera el "go for it" antes de marcarlas como `ready_to_publish`.

Razón: tener un solo punto de aprobación humano evita fatiga de aprobación y permite ver el output completo (todas las variantes lado a lado) en vez de pieza por pieza.

### 7.6 Multi-tenancy: migrar `Brand Context`

Reemplazar el nodo `2 Brand Context` (dataTable hardcodeada) por **Airtable Read** sobre tabla `Brands` con campos:

```
brand_id, name, niche, target_audience, tone_of_voice, visual_style,
dont_say, brand_guidelines_pdf_url, sample_winning_content_urls (multi),
sales_team_whatsapp_numbers (multi), meta_ad_account_id,
instagram_business_id, status
```

Esto permite agregar clientes nuevos sin tocar el workflow.

---

## 8. SPEC: Workflow C — Distribution & Funnel

### 8.1 Trigger
- **Webhook**: dispara cuando una `Piece` cambia a `status = ready_to_publish` en Airtable (vía Airtable Automation → Webhook a n8n).

### 8.2 Branch 1: Publicación orgánica

#### Nodo C1a: `Channel Router`
- **Tipo**: Switch node sobre `target_channels` del brief (puede ser multi-output, una pieza va a varios canales en paralelo).

#### Nodo C2a: `Instagram Organic Publisher`
- **Tipo**: HTTP Request a Meta Graph API
- **Endpoint**: `POST /{ig-user-id}/media` (create container) → `POST /{ig-user-id}/media_publish`
- **Auth**: long-lived access token guardado en n8n credentials por brand
- Adjunta UTM-tagged link en la bio link o sticker.

#### Nodo C2b: `TikTok Organic Publisher`
- **Tipo**: HTTP Request a TikTok Content Posting API
- **Endpoint**: `POST /v2/post/publish/video/init/` → upload chunk → `POST /v2/post/publish/status/fetch/`
- **Pre-req**: Business Account verificado (obligatorio desde enero 2026) + app aprobada (sandbox → producción ~1-2 semanas según madurez del request)
- Rate limit: 6 requests/minuto en posting endpoints

#### Nodo C2c: `YouTube Publisher` (NUEVO)
- **Tipo**: HTTP Request a YouTube Data API v3
- **Endpoint**: `POST /upload/youtube/v3/videos` (resumable upload, multipart)
- **Auth**: OAuth 2.0 con scope `youtube.upload` (token refresh programático mensual)
- **Costo en quota**: ~100 unidades por upload desde diciembre 2025 (antes 1600). Con quota default de 10K/día se pueden hacer ~100 uploads diarios sin pedir extensión.
- **Diferenciación Shorts vs long-form**: la API no tiene un flag explícito. Para que YouTube clasifique el video como Short hay que cumplir:
  - Duración ≤ 60 segundos
  - Aspect ratio vertical (9:16)
  - Hashtag `#Shorts` en título o descripción
- **Metadata SEO** (importante, se setea en el mismo upload):
  - `snippet.title` (máx 100 chars, optimizado con keyword principal)
  - `snippet.description` (con keywords secundarias, link a landing en primera línea)
  - `snippet.tags` (máx 500 chars total)
  - `snippet.categoryId` (depende del nicho)
  - `snippet.defaultLanguage`

#### Nodo C2d: `YouTube SEO Optimizer Agent` (NUEVO, corre ANTES del Publisher)
- **Modelo**: Claude Sonnet 4.6
- **System prompt**:

```
Sos el YouTube SEO Optimizer. Recibís el copy de la pieza y devolvés
metadata YouTube-ready optimizada para descubrimiento.

INPUT: copy_text, brand_niche, target_keyword (del SEO Strategist),
video_duration_seconds, aspect_ratio.

PROCESO:
1) Title: 60-70 chars, keyword principal en los primeros 50 chars,
   gancho emocional. NO clickbait engañoso.
2) Description: párrafo 1 (primeras 2 líneas visibles) con keyword +
   propuesta de valor + link CTA. Resto: 150-300 palabras con keywords
   secundarias naturalmente integradas + timestamps si aplica + links
   relevantes.
3) Tags: 10-15 tags, mix de keyword exacta, variantes y términos del nicho.
4) Si es Short (≤60s + 9:16): agregar #Shorts al inicio del título.
5) Sugerí 3 ideas de thumbnail (rostro humano + texto grande + contraste).

OUTPUT: JSON {title, description, tags[], is_short, thumbnail_ideas[]}.
```

#### Nodo C2e: `LinkedIn Publisher` (opcional)
- **Tipo**: HTTP Request a LinkedIn Marketing API
- Útil sobre todo si el brand tiene posicionamiento B2B.

### 8.3 Branch 2: Pautado multi-plataforma

Cada plataforma tiene su propio Campaign Manager Agent. El **Ad Platform Router** decide a cuál(es) mandar la pieza según `target_channels` del brief y `funnel_stage`. Reglas por defecto:

| funnel_stage | Plataformas sugeridas | Por qué |
|---|---|---|
| TOFU | Meta + TikTok + YouTube Ads (in-stream skippable) | Discovery visual masivo, CPM bajo |
| MOFU | Meta + YouTube (Discovery/in-feed) | Audiencias custom, engagement |
| BOFU | Meta retargeting + **Google Ads Search** + Performance Max | Capturar demanda activa con intent |

> **Insight clave**: Google Ads Search es la única plataforma que captura **intención activa** (alguien ya está buscando lo que el cliente vende). Las otras 3 son **interrupción**. Un funnel completo necesita ambas.

#### Nodo C1b: `Ad Platform Router`
- **Tipo**: Switch node multi-output
- Lee `target_channels` + `funnel_stage` y decide a cuáles de los 4 Campaign Managers manda la pieza.

#### Nodo C2f: `Meta Ads Campaign Manager Agent`
- **Modelo**: Claude Sonnet 4.6
- **System prompt**:

```
Sos el Campaign Manager de Meta Ads. Recibís variantes aprobadas y
decidís la estructura de campaña para Facebook + Instagram.

INPUT: pieces array (variantes aprobadas), brand context, funnel_stage,
campaign_budget (de Airtable.Campaigns).

PROCESO:
1) Decidí campaign objective según funnel_stage:
   - TOFU → OUTCOME_AWARENESS o OUTCOME_ENGAGEMENT
   - MOFU → OUTCOME_TRAFFIC o OUTCOME_ENGAGEMENT
   - BOFU → OUTCOME_LEADS o OUTCOME_SALES
2) 1 adset por audiencia. TOFU = lookalike o interest; BOFU = custom audience
   (visitantes web 30d, engagement IG 90d).
3) Cada variante creativa = 1 ad dentro del adset (A/B nativo de Meta).
4) Placements: automatic para TOFU; manual (solo feed + reels) para BOFU.
5) Devolvé JSON listo para crear vía API: campaign{}, adsets[], ads[].

OUTPUT: JSON con estructura Meta-compatible.
```

- **Push API**: `POST /act_{id}/campaigns` → `/act_{id}/adsets` → `/act_{id}/adcreatives` → `/act_{id}/ads`. Status inicial `PAUSED`.

#### Nodo C2g: `TikTok Ads Campaign Manager Agent` (NUEVO)
- **Modelo**: Claude Sonnet 4.6
- **System prompt**:

```
Sos el Campaign Manager de TikTok Ads. La lógica TikTok es DISTINTA a
Meta: aquí gana el contenido nativo (que parece TikTok orgánico), no
el ad-looking.

INPUT: pieces array (variantes aprobadas), brand context, funnel_stage,
campaign_budget.

PROCESO:
1) Campaign objective:
   - TOFU → REACH o VIDEO_VIEWS (Spark Ads cuando sea posible: usar post
     orgánico ya publicado como creativo, dispara mejor performance)
   - MOFU → TRAFFIC o ENGAGEMENT
   - BOFU → LEAD_GENERATION o CONVERSIONS
2) Considerá Smart+ para automatizar targeting/budget/placement si la
   cuenta tiene historial; si es cuenta nueva, manual.
3) Audience: TikTok usa "Interest & Behavior" + "Hashtag interactions"
   (esto último es muy potente, no existe en Meta).
4) Placements: solo TikTok (NO usar audience network para BOFU).
5) Devolvé JSON con estructura: campaign, adgroups, ads.

REGLAS DURAS:
- NO usar ads con copy de fondo blanco/genérico (TikTok los penaliza).
- Hook en primeros 1.5 segundos.
- CTA nativa: "Tap to learn more", no "Click here".

OUTPUT: JSON TikTok Marketing API-compatible.
```

- **Push API**: TikTok Marketing API `business-api.tiktok.com/open_api/v1.3/`. Endpoints: `/campaign/create/` → `/adgroup/create/` → `/ad/create/`.
- **Auth**: OAuth con access_token (24h) + refresh_token (365d). Setear cron de refresh.

#### Nodo C2h: `YouTube Ads Campaign Manager Agent` (NUEVO)
- **Modelo**: Claude Sonnet 4.6
- **System prompt**:

```
Sos el Campaign Manager de YouTube Ads. Las campañas YouTube se crean
vía Google Ads API (NO YouTube Data API).

INPUT: pieces array (variantes video), brand context, funnel_stage,
campaign_budget, video_youtube_ids (los assets ya deben estar subidos a
YouTube como "unlisted" o "public" antes de crear el ad).

PROCESO:
1) Decidí campaign sub-type:
   - TOFU → Video Reach Campaign (Bumper 6s + Skippable in-stream)
   - MOFU → Video View Campaign o In-Feed Video Ads (Discovery)
   - BOFU → Video Action Campaign (call-to-action overlay + lead form)
2) Para Shorts ads: usar formato vertical 9:16 + Performance Max o
   Demand Gen campaign con creativos cortos.
3) Audience: affinity + in-market para TOFU; custom intent (keywords
   de búsqueda) para MOFU; remarketing para BOFU.
4) Si hay landing con conversiones tracked (GA4 + Google Ads tag),
   activar Smart Bidding (Target CPA o Maximize Conversions).

OUTPUT: JSON Google Ads API-compatible con resourceName de Campaign,
AdGroup, AdGroupAd. Status inicial PAUSED.
```

- **Push API**: Google Ads API v17+ via HTTP Request (n8n credential OAuth2 Google).
- **Pre-req**: video debe existir en YouTube primero (lo sube `YouTube Publisher` C2c).

#### Nodo C2i: `Google Ads Campaign Manager Agent` (NUEVO)
- **Modelo**: Claude Sonnet 4.6
- **System prompt**:

```
Sos el Campaign Manager de Google Ads. Tu fuerza está en BOFU porque
capturás demanda activa (search intent), no interrumpís.

INPUT: pieces, brand context, funnel_stage, keywords (del SEO Strategist),
landing_page_url, campaign_budget.

PROCESO según funnel_stage:

BOFU (priorizá esto, es donde Google Ads brilla):
1) Search Campaign con keywords transaccionales (exact + phrase match).
   Negative keywords obligatorias para filtrar tráfico basura.
2) Responsive Search Ads: 15 headlines, 4 descriptions, generadas a
   partir del copy aprobado, manteniendo brand voice.
3) Conversion tracking activo (GA4 + Google Ads tag). Sin esto, no se
   puede optimizar.
4) Bidding: Maximize Conversions si hay <30 conv/mes; Target CPA si más.

MOFU:
5) Performance Max si la cuenta ya tiene data de conversiones (>30/mes).
   Si no, mejor Search + Display separadas para tener control.

TOFU:
6) Demand Gen Campaign (reemplazo de Discovery en 2026). Visual-heavy,
   funciona en Gmail + YouTube Feed + Discover.

REGLAS:
- NO crear campañas Search sin conversion tracking previo. Tirar plata.
- NO usar broad match al inicio (gasta presupuesto sin datos).
- Cada Search campaign debe tener al menos 3 ad groups temáticos.

OUTPUT: JSON Google Ads API-compatible. Campaigns siempre creadas en
status PAUSED.
```

- **Push API**: Google Ads API v17+. Operaciones: `mutate Campaigns`, `mutate AdGroups`, `mutate AdGroupAds`, `mutate Keywords`.
- **Pre-req crítico**: developer token aprobado (Test → Standard via support request). Sin developer token Standard, solo se puede operar sobre Test Accounts.
- **Node n8n**: usar el built-in `Google Ads node` para operaciones básicas; HTTP Request con la misma credential OAuth2 para el resto.

#### Nodo C3: ~~Approval & Activation Gateway~~ → reemplazado por Checkpoint 2

A partir de v1.3.0, **no hay un approval por plataforma**. Después de que los 4 Campaign Manager Agents proponen las estructuras de campaña, el Workflow C corre los nodos de creación en las 4 APIs en modo `PAUSED` y luego genera el **Pre-Flight Output Report** (sección 9.ter) que muestra las 4 campañas + previews orgánicos + landing en un solo documento.

Solo con un "go for it" único el sistema activa todas las campañas en paralelo (Meta, TikTok, YouTube, Google) + publica orgánicos según calendario + activa landing/webhook.

### 8.4 Branch 3: Landing + captura

#### Nodo C3: `Landing Builder` (opcional, si el cliente no tiene)
- **Principal**: webhook a Tally (form pre-armado por cliente, una vez)
- O: deploy automático de página estática a Cloudflare Pages

#### Nodo C4: `Lead Form Webhook`
- **Trigger**: webhook que escucha el submit del form de Tally / landing propia.

#### Nodo C5: `Lead Qualifier Agent`
- **Modelo**: Claude Haiku 4.5 (latencia baja)
- **System prompt**:

```
Sos el Lead Qualifier. Recibís un lead crudo del form y devolvés un
lead enriquecido + puntuado.

INPUT: lead_data (nombre, email, teléfono, mensaje opcional, UTM source/
campaign/ad), brand context (qué ofrece, ICP).

PROCESO:
1) Validá email (regex + dominio existe).
2) Detectá si es email corporativo o personal.
3) Cruzá el mensaje del lead contra el ICP del brand:
   - menciona problema que el brand resuelve → +2
   - menciona urgencia/timeline → +2
   - tiene presupuesto implícito → +2
   - hace pregunta específica vs. genérica → +1
   - dominio corporativo relevante → +1
4) Score final 1-10. Hot ≥ 7, Warm 4-6, Cold ≤ 3.
5) Sugerí prioridad de respuesta: inmediata, <1h, <24h, batch.

OUTPUT: JSON con enriched_lead, score, priority, suggested_action,
reasoning (max 30 palabras).
```

- **Integración opcional**: HTTP a Apollo.io / Hunter para enriquecer email B2B con info de empresa.

#### Nodo C6: `Airtable Write — Leads`
Guarda lead enriquecido + score + referencia a `Piece`, `Campaign`, `Ad` que lo originó.

#### Nodo C7: `WhatsApp Sales Notifier`
- **Tipo**: HTTP Request a WhatsApp Cloud API
- **Endpoint**: `POST /v21.0/{phone-number-id}/messages`
- **Auth**: token de WhatsApp Business del cliente
- **Template** (pre-aprobado, categoría `utility`):

```
🔔 Nuevo lead | {{brand_name}}

👤 {{lead_name}}
📧 {{lead_email}}
📱 {{lead_phone}}

🌡 Score: {{score}}/10 ({{temperature}})
🎯 Origen: {{campaign_name}} → {{ad_name}}
💬 Mensaje: "{{lead_message}}"

⚡ Acción sugerida: {{suggested_action}}

Ver en Airtable: {{airtable_url}}
```

- Destino: `sales_team_whatsapp_numbers` del brand (puede ser multi-recipient).
- **Costo**: la categoría `utility` cuesta menos que `marketing` (~$0.008-0.012 USD por mensaje según región).

#### Nodo C8 (opcional): `Click-to-WhatsApp Lead Router`
Si el lead llega por ad Click-to-WhatsApp (no por form), entra directo a WhatsApp del brand. Un agente Claude Haiku responde la primera interacción para no perder al lead, recolecta datos básicos, y luego notifica al equipo de ventas (mismo flujo C5-C7).

- **Ventaja Meta**: los leads de Click-to-WhatsApp ads dan 72h gratis de mensajería (no aplica fee por conversación).

---

### 8.5 Branch 4: Blog autónomo (publicación SEO sobre trend del momento)

Este branch convierte una señal del Trend Scout en un blog post publicado directamente al sitio del cliente, optimizado para SEO. Se dispara cuando el SEO Strategist (Workflow A, nodo A4) marca `evergreen_recommendation = true` para un trend.

#### Nodo C9: `Blog Brief Generator`
- **Modelo**: Claude Sonnet 4.6
- **System prompt**:

```
Sos el Blog Brief Generator. Convertís una keyword opportunity + trend
en un brief de blog post optimizado para SEO.

INPUT: target_keyword, search_intent, trend_context, brand_voice,
audience.

PROCESO:
1) Validá search intent → match con tipo de contenido:
   - informational → guía / how-to / explainer
   - commercial → comparativa / review / "best X for Y"
   - transactional → landing-like, pero hosted en blog
2) Definí estructura con H2/H3 jerárquica (mínimo 5 H2, idealmente con
   keyword en al menos 3).
3) Sugerí: meta title (≤60 chars), meta description (≤155 chars), slug,
   primary keyword + 3-5 LSI keywords, internal links a otras pages
   del brand (si están en Airtable.Brands.published_urls), external
   links a fuentes autoritativas.
4) Word count target: 1200-2500 (depende del SERP analysis).

OUTPUT: JSON brief con structure, meta_tags, keyword_map, internal_links.
```

#### Nodo C10: `Long-form Writer Agent`
- **Modelo**: Claude Sonnet 4.6 (no Flash, calidad de prosa importa para SEO)
- **System prompt**:

```
Sos el Long-form Writer. Escribís el post completo siguiendo el brief
exacto, manteniendo brand voice y SEO best practices.

INPUT: blog_brief del nodo anterior, brand tone_of_voice, dont_say list.

REGLAS DE ESCRITURA:
1) Primer párrafo: hook + responder la query principal en las primeras
   2-3 líneas (featured snippet bait).
2) Keyword principal en H1, primer párrafo, al menos 1 H2, y conclusión.
   Densidad natural (no keyword stuffing).
3) Cada H2 = subtema autónomo. Lectura escaneable: párrafos cortos
   (máx 3 líneas), bullets cuando aplique.
4) Incluí 1-2 ejemplos concretos o casos reales por sección.
5) CTA al final + 1 CTA mid-content si el post es >1500 palabras.
6) Markdown puro. Imágenes referenciadas con alt text descriptivo.

OUTPUT: Markdown completo del post, listo para publicar.
```

#### Nodo C11: `Featured Image Generator`
- Reutiliza el pipeline `Art Director` + `Claude Design Critic` + `Flux` ya existente, pero con aspect ratio 16:9 (blog hero).
- Sube a Drive y al CMS.

#### Nodo C12: `Blog Publisher`
Dos opciones según el cliente:

**Opción A — Ghost (recomendado para arrancar):**
- **Tipo**: HTTP Request a Ghost Admin API
- **Endpoint**: `POST /ghost/api/admin/posts/`
- **Auth**: Admin API Key (JWT-based)
- **Payload**: `{posts: [{title, slug, html o mobiledoc, meta_title, meta_description, feature_image, tags, status: "published" o "draft"}]}`

**Opción B — WordPress:**
- **Tipo**: HTTP Request a WordPress REST API
- **Endpoint**: `POST /wp-json/wp/v2/posts`
- **Auth**: Application Passwords (más simple) o JWT plugin
- **Payload**: `{title, content, slug, excerpt, status, categories, tags, featured_media}`

**Opción C — Sitio estático (Astro/Next):**
- Push a repo GitHub vía API → GitHub Actions hace deploy automático.
- Más control, mejor performance SEO (Core Web Vitals), pero más setup.

#### Nodo C13: `SEO Submit & Indexing`
Después de publicar:
- HTTP a Google Indexing API: `POST https://indexing.googleapis.com/v3/urlNotifications:publish` con `{url, type: "URL_UPDATED"}`. Acelera la indexación.
- (Opcional) Notificación a Bing Webmaster Tools API.
- Agregar URL al sitemap.xml si el CMS no lo hace automáticamente.

#### Nodo C14: `Cross-promotion Trigger`
Una vez publicado el blog, dispara automáticamente:
- Brief al Workflow B para generar 1 pieza social (IG/TikTok) que linkee al blog → tráfico orgánico.
- Email (opcional) a la lista del brand vía Resend con el resumen + link.

> **Por qué el blog autónomo importa**: combina la velocidad del social (publicás sobre el trend mientras está caliente) con la durabilidad del SEO (el post sigue trayendo tráfico orgánico meses después). Es el único canal del stack con **rendimiento compuesto**: los demás (social orgánico, ads) tienen vida útil de horas a días; un blog post bien rankeado capitaliza durante años.

---

## 9. SPEC: Workflow D — Performance Loop

### 9.1 Trigger
- **Cron diario**: 02:00 lectura de métricas.
- **Cron semanal**: viernes 18:00 síntesis de aprendizajes.

### 9.2 Nodos

#### Nodo D1: `Metrics Collector`
Para cada `Campaign` activa o `Piece` publicada en Airtable, recolecta métricas por plataforma:

| Plataforma | Endpoint | Métricas clave |
|---|---|---|
| Meta Ads | `GET /act_{id}/insights?fields=impressions,clicks,spend,actions&level=ad` | CTR, CPM, CPC, CPL, ROAS |
| Instagram orgánico | `GET /{media-id}/insights?metric=impressions,reach,engagement,saved,shares` | Reach, engagement rate, saves |
| TikTok Ads | `POST /open_api/v1.3/report/integrated/get/` | CTR, CPM, conversion rate, video play 25/50/75/100% |
| TikTok orgánico | TikTok Display API `/video/query/` (si app aprobada) | Views, likes, shares, comments |
| YouTube orgánico | YouTube Analytics API `/reports?metrics=views,estimatedMinutesWatched,subscribersGained,likes` | Watch time (clave), retention, CTR del thumbnail |
| YouTube Ads | Vía Google Ads API (las campañas de YouTube reportan ahí) | View rate, CPV, conversiones |
| Google Ads | Google Ads API `GoogleAdsService.SearchStream` query GAQL | Impressions, clicks, conversions, cost_per_conversion, quality_score |
| Blog autónomo | **GA4 Data API** (`runReport`) + **Google Search Console API** | Sessions, avg engagement time, conversions, organic positions, CTR de SERP, query terms |

Escribe todo en Airtable `Metrics` con `timestamp`, `piece_id` o `campaign_id`, `platform`, y métricas normalizadas (mismos nombres de campo cross-platform donde sea posible: `impressions`, `clicks`, `engagement`, `conversions`, `spend`).

> **Por qué normalizar**: el Performance Analyst del nodo D2 razona sobre métricas cross-platform. Si Meta dice `clicks` y TikTok dice `link_clicks` y YouTube dice `cta_clicks`, el agente se confunde. Normalizar a la escritura en Airtable es más simple que parchear el prompt del agente.

#### Nodo D2: `Performance Analyst Agent` (semanal)
- **Modelo**: Claude Opus 4.7 (razonamiento profundo)
- **System prompt**:

```
Sos el Performance Analyst. Analizás 7 días de métricas cruzando
creativos, copys, audiencias, funnel stages.

INPUT: metrics array (todas las pieces publicadas la semana, con sus
KPIs: CTR, CPM, CPC, conversion rate, leads, lead_score promedio).

PROCESO:
1) Identificá top 3 performers y bottom 3 por funnel stage.
2) Aislá la variable: ¿fue el hook? ¿el visual? ¿la audiencia?
3) Generá hipótesis: "X funcionó porque {patrón concreto}, no porque
   {alternativa obvia descartada}".
4) Recomendaciones accionables:
   - Qué replicar en próximas piezas
   - Qué pausar
   - Qué reasignar de presupuesto

OUTPUT: Markdown estructurado con:
## Top Performers
## Underperformers
## Hipótesis validadas
## Recomendaciones (con acción específica + impacto esperado)
```

#### Nodo D3: `Airtable Write — Learnings`
Guarda el output del analyst como row en `Learnings` con `brand_id` y `week_of`. El Strategy Director del Workflow B lee los últimos 3 learnings cada vez que arma una estrategia nueva.

#### Nodo D4: `Budget Optimizer Agent`
- **Modelo**: Claude Sonnet 4.6
- **System prompt**:

```
Recibís métricas de adsets activos y ejecutás reasignación de presupuesto
según ROAS o CPL (según el objetivo de la campaña).

REGLAS DURAS (no negociables, deben respetarse siempre):
- No reasignar antes de 72h de data (estadísticamente débil).
- No mover más de 30% del budget en una sola iteración.
- No exceder el cap mensual definido en Brands.default_funnel_budget.
- Pausar ads con CPL > 2x el promedio del adset Y >50 clicks.

Si un cambio que querés hacer VIOLA alguna regla dura → NO lo ejecutás,
marcás el evento en BudgetChanges con status = blocked_by_rule y rotás
al alert operativo "necesita decisión humana sobre cap".

Si el cambio respeta las reglas → EJECUTÁ directamente vía API, escribí
en BudgetChanges el log. No pidas aprobación.

OUTPUT: JSON con array de cambios ejecutados: {ad_id, action: pause|
increase_budget|decrease_budget, amount, reasoning, executed_at}.
Los cambios se ejecutan automáticamente respetando las reglas duras (no mover más de 30% del budget por iteración, no reasignar antes de 72h de data). El Budget Optimizer no pide aprobación humana para cambios que cumplen las reglas. Solo escribe en Airtable `BudgetChanges` el log de cada ajuste con timestamp + razón + métrica que lo justificó.
```

#### Nodo D5: `Weekly Report Archive`
El report del Performance Analyst se guarda como row en Airtable `WeeklyReports` con `brand_id` y `week_of` para auditoría y consulta. **No se notifica al CEO**: si el CEO quiere ver el report, lo consulta en Airtable cuando quiera. Si hay aprendizajes críticos que afecten próximos Workflows A o B, se inyectan automáticamente como contexto vía la tabla `Learnings`.

> **Nota sobre autonomía**: el Workflow D corre completamente solo. Lee métricas, sintetiza, reasigna budgets dentro de los límites configurados, guarda aprendizajes. Solo escala al CEO si Budget Optimizer detecta una situación que excede las reglas duras (ej: querría mover >30% del budget, o querría aumentar gasto total más allá del cap mensual configurado en `Brands.default_funnel_budget`). En ese caso entra en la categoría "pago/fondos pendientes" del principio de autonomía.

---

## 9.bis SPEC: Workflow E — Cold Email Outbound (B2B)

> Workflow paralelo al resto. Pensado para prospección B2B activa: nuestra agencia (o el cliente al que servimos) define un perfil de empresa objetivo, el sistema sale a buscarlas, recupera contactos, escribe propuestas personalizadas y las envía como secuencia de cold email. Las respuestas positivas entran al mismo `Leads` table que los inbound de Workflow C.

### 9.bis.1 Principio rector
**Claude NUNCA dispara una campaña sin pasar por el `Pre-Flight Interview Agent`.** Es la salvaguarda contra el problema clásico: ejecutar 5000 emails con un targeting mal definido quema dominios y reputación, y se tardan meses en recuperar. La fricción del interview es deliberada.

### 9.bis.2 Trigger
- **Manual**: el CEO o account manager le dice a Claude "lancemos una cold email campaign para {brand_o_para_nosotros}".
- Esto inicia un **chat con el Pre-Flight Interview Agent**, no el scraping directo.

### 9.bis.3 Nodos secuenciales

#### Nodo E1: `Quality Input Control — Extensión E` (Checkpoint 1 para Workflow E)

> A partir de v1.3.0, este nodo es una instancia del **Quality Input Control universal** (sección 0.A) cargando la **extensión E**. Lo que en v1.2.0 era el "Pre-Flight Interview Agent" exclusivo de E ahora se integra al sistema de checkpoints universal.

El agente Quality Input Control conduce la entrevista interactiva pidiendo, en orden, los campos del **form base** (sección 0.A.3) + la **extensión E** (sección 0.A.4). Las preguntas críticas que el agente NO acepta vagas:

1. **Sector / nicho objetivo** (campo `target_sector`)
   - Ejemplo aceptable: "Restaurantes de cocina italiana de 5-15 empleados en Milán y Roma".
   - Ejemplo NO aceptable: "Restaurantes en Italia" → pide especificación.

2. **Perfil del decision-maker** (campo `icp_decision_maker`)
   - Pide: cargo + área + seniority.
   - Si el usuario no sabe, ofrece hipótesis basada en el sector y pide confirmación.

3. **Propuesta comercial sharp** (campo `sharp_proposition`, máx 200 chars)
   - Aceptable: "Te conseguimos 30 reservas mensuales nuevas desde redes sociales en 60 días, o no nos pagás el siguiente mes."
   - NO aceptable: "Servicios de marketing digital de calidad" → pide re-escritura con resultado + plazo + diferenciador.

4. **Validaciones de capacidad** que el agente hace automáticamente:
   - Si `target_volume` > (mailboxes_disponibles × 30 × timeline_days), alerta y propone cronograma realista.
   - Si `compliance_region = EU/UK/CA`, requiere confirmación de legitimate interest documentado.
   - Si `cta_type ≠ reply`, requiere `cta_link`.

Output: JSON con schema completo (ver 0.A.5) escrito en Airtable `WorkflowRuns` y `OutboundCampaigns` con `status = input_validated`. El resto del Workflow E (nodos E2 en adelante) no se ejecuta sin este status.

#### Nodo E2: `Prospect Scout — Google Maps`
- **Tipo**: HTTP Request a Apify Google Maps Scraper
- **Input** (del JSON del E1): industry + geography + sub_niche → se traduce a queries Apify (ej: `"restaurants italian Milano"`, `"restaurants italian Roma"`).
- **Apify run**: `POST https://api.apify.com/v2/acts/compass~crawler-google-places/runs?token={APIFY_TOKEN}`
- **Output esperado**: array de empresas con `title, address, website, phone, category, totalScore, reviewsCount, openingHours`
- **Filtros aplicados después**:
  - Eliminar las que no tienen website (sin website ≈ sin email fácil de recuperar)
  - Filtrar por tamaño aproximado (si `reviewsCount` es proxy de tamaño, ajustar al rango pedido)
  - Deduplicar por website domain

#### Nodo E3: `Prospect Scout — Web Search` (complementario)
- **Tipo**: HTTP Request a Serper.dev
- Para empresas B2B puras que no aparecen en Google Maps (SaaS, agencias remotas, etc.)
- Query construida del JSON: `"{industry} {sub_niche} companies {geography} site:linkedin.com/company"` (o similar)
- Útil cuando el ICP es muy específico y Maps no es el canal natural

#### Nodo E4: `Airtable Write — Prospects (raw)`
- Escribe todo en tabla `Prospects` con `status = needs_enrichment`, vinculado al `outbound_campaign_id`.
- Esto crea el **único database de potenciales clientes** consolidado que pediste.

#### Nodo E5: `Data Enrichment & Recovery Agent`
Este es el "software de recuperación de datos" que mencionaste, implementado como nodo orchestrator.

- **Tipo**: Loop sobre prospects + HTTP Requests a Apollo.io / Hunter.io
- **Para cada prospect**:
  1. Buscar la empresa en Apollo por dominio: `POST https://api.apollo.io/v1/organizations/enrich`
  2. Una vez encontrada la org, buscar personas que matcheen el ICP: `POST https://api.apollo.io/v1/mixed_people/search` con filtros `person_titles`, `organization_ids`, `seniorities`
  3. Si Apollo no tiene email para esa persona, fallback a Hunter: `GET https://api.hunter.io/v2/email-finder?domain=X&first_name=Y&last_name=Z`
  4. Si ningún proveedor devuelve email, marcar prospect como `enrichment_failed` (no se descarta, podría ser útil para LinkedIn outreach manual)

- **Output**: `Prospects` actualizado con `contact_first_name, contact_last_name, contact_title, contact_email, contact_linkedin_url, enrichment_source, enrichment_confidence`

#### Nodo E6: `Email Verification`
- **Tipo**: HTTP Request a Million Verifier API (o NeverBounce)
- **Endpoint**: `GET https://api.millionverifier.com/api/v3/?api={KEY}&email={EMAIL}`
- **Filtra**: solo prospects con `result = "ok"` siguen. Los `catch_all` van a una lista B (sending con cuidado). Los `invalid` o `disposable` se descartan.
- **Por qué importa**: bounce rate >5% en cold email destruye la reputación del dominio en días. Verificar antes de enviar es no-negociable.

#### Nodo E7: `Cold Email Copywriter Agent`
- **Modelo**: Claude Sonnet 4.6 (la calidad del copy es lo que separa una campaña que convierte de una que es ignorada)
- **System prompt**:

```
Sos el Cold Email Copywriter. Escribís emails outbound que SIENTEN
escritos a mano, no spam masivo.

INPUT: prospect_data (contact_name, title, company, company_website,
industry), pre_flight_brief (sharp_proposition, credibility_proof,
cta_type, cta_link), brand_signature_info (sender_name, sender_role,
sender_company, sender_contact).

REGLAS DE COPY:
1) Asunto: 3-6 palabras, lowercase preferido, sin "Re:" falso, sin
   "última oportunidad", sin emojis. Que parezca un email personal.
   Ejemplos buenos: "quick question, {first_name}", "{company} +
   {nuestro_servicio_corto}".

2) Primera línea: referencia específica al prospect (nombre, empresa,
   algo de su web). Probá que NO es un mass-send.
   Mal: "Hola, espero que estés bien."
   Bien: "Vi que {company} acaba de abrir una segunda sede en {ciudad}.
   Felicitaciones."

3) Cuerpo (máx 90 palabras):
   - 1 frase de contexto (por qué le escribís a esta persona específica)
   - 1 frase con el sharp_proposition adaptado
   - 1 frase con credibility_proof
   - CTA según cta_type

4) Firma: nombre, rol, empresa, contact info clara (email + teléfono
   + web). Esto es OBLIGATORIO por compliance y trust.

5) PS opcional (incrementa response rate): 1 línea con un dato
   curioso/útil para el prospect, no salesy.

6) Follow-ups (escribir 3 adicionales):
   - Follow-up 1 (día +3): "subiendo al inbox" + reframe del valor
   - Follow-up 2 (día +7): case study breve o nuevo ángulo
   - Follow-up 3 (día +14): break-up email ("entiendo que no es
     prioridad, cerramos el loop")

ANTI-PATRONES (nunca hacer):
- NO usar "Espero que este mensaje te encuentre bien"
- NO usar "Soy {nombre} de {empresa} y nos especializamos en..."
- NO mencionar AI o automatización
- NO usar más de 1 link en el primer email
- NO adjuntar archivos en el primer email

OUTPUT: JSON con:
{
  "subject": "string",
  "body_email_1": "string (markdown)",
  "body_followup_1": "string",
  "body_followup_2": "string",
  "body_followup_3": "string",
  "personalization_tokens_used": ["string"]
}
```

#### Nodo E7.5: `Visual Asset Generator` (opcional, solo si CTA = watch_loom_reply o si querés diferenciarte)
- Reutiliza el pipeline Art Director + Flux del Workflow B para generar 1 imagen custom para el email (ej: mockup del servicio aplicado a la empresa del prospect, con su logo si está disponible vía Clearbit Logo API gratuita).
- Sube a Drive y mete URL en el email.
- **Cuidado**: imágenes en cold emails bajan deliverability si están mal embebidas. Solo usar si el copy gana clarity con ella.

#### Nodo E8: ~~Approval Gate Sample Review~~ → reemplazado por Checkpoint 2

A partir de v1.3.0, el approval del sample de cold email se consolida en el **Pre-Flight Output Report** (sección 9.ter). El Workflow E genera todos los emails del batch, los lista en el report con 5 muestras aleatorias + stats del batch completo (verificación, mailboxes, cronograma), y espera el "go for it" único antes de pushear a Smartlead.

#### Nodo E9: `Smartlead Campaign Push`
- **Tipo**: HTTP Request a Smartlead API
- **Endpoints secuenciales**:
  1. `POST /api/v1/campaigns/create` con campaign_name del pre-flight brief
  2. `POST /api/v1/campaigns/{id}/leads` con array de leads (email + personalización tokens)
  3. `POST /api/v1/campaigns/{id}/sequences` con los 4 mensajes (initial + 3 followups) y delays
  4. `POST /api/v1/campaigns/{id}/email-accounts` para asignar los mailboxes del cliente/agencia
  5. `POST /api/v1/campaigns/{id}/schedule` con timezone del target y horario óptimo (martes-jueves 10am-12pm timezone del prospect)
  6. `POST /api/v1/campaigns/{id}/start` (status: paused por default; humano confirma)

#### Nodo E10: `Smartlead Webhook Listener`
- **Tipo**: Webhook trigger
- Smartlead manda eventos en tiempo real: `reply_received`, `bounced`, `unsubscribed`, `opened`, `link_clicked`.
- Cada evento se procesa según tipo.

#### Nodo E11: `Inbox Reply Router Agent`
- **Modelo**: Claude Haiku 4.5 (latencia baja, decisión rápida)
- **System prompt**:

```
Clasificás respuestas a cold emails en una de 6 categorías:

1. INTERESTED — pide más info, quiere call, está abierto.
2. NOT_NOW — interesado pero pide volver en X meses.
3. NOT_INTERESTED — declina explícitamente. Mover a no_contact.
4. WRONG_PERSON — derivá a otro contacto en la empresa.
5. OUT_OF_OFFICE — auto-reply. Re-encolar followup +7 días.
6. UNSUBSCRIBE — pide no recibir más emails. Mover a permanent_suppression.

INPUT: reply_body + original_email_context.
OUTPUT: JSON {category, confidence_score, suggested_next_action,
extracted_referral_email (si WRONG_PERSON)}.

Si confidence_score < 0.7, marcar para revisión humana.
```

#### Nodo E12: `Lead Push to Main Pipeline`
- Si la respuesta es **INTERESTED**: crear row en `Leads` (la misma tabla del Workflow C) con `source = cold_email`, `score = 7` (default warm para reply positivo a cold), `priority = within_1h`.
- Dispara el **mismo** `WhatsApp Sales Notifier` (Nodo C7) que ya tenés del Workflow C.
- **Esto es lo elegante**: cold email y ads/orgánico convergen al mismo lead-handling pipeline. El equipo de ventas del cliente recibe la notificación WhatsApp idéntica, vengan de donde vengan.

#### Nodo E13: `Domain & Inbox Health Monitor` (cron diario)
- Lee métricas de Smartlead por mailbox: bounce_rate, reply_rate, spam_complaints
- Si bounce_rate > 3% en 24h → **pausa automática del mailbox** + log en EmailMailboxes (no notifica al CEO, es decisión autónoma dentro de los límites configurados)
- Si spam_complaint_rate > 0.1% → **pausa todo el dominio** + log + escala a operations-alerts SOLO si el problema requiere acción humana (ej: "se quemaron todos los mailboxes del dominio X, hay que comprar dominio nuevo Y warmear, ETA 14 días, costo €40/año") — entra en categoría "pago/fondos pendientes" del principio 0.0.

### 9.bis.4 Cómo encaja con el resto del sistema

- **Workflow A (Discovery)**: si una campaña cold email funciona bien para un sector, el Trend Scout puede usar ese sector como input para discovery orgánico ("si vendemos bien a clínicas dentales, busquemos trends de marketing dental").
- **Workflow B (Production)**: si el visual asset del E7.5 funciona, el Art Director puede aprender de eso para futuras piezas.
- **Workflow C (Distribution)**: comparten `Leads` table y notificación WhatsApp. Un prospect que respondió cold email + después interactuó con un ad orgánico tiene score combinado más alto.
- **Workflow D (Performance)**: el Performance Analyst incluye métricas cold email (reply rate, meeting booked rate) en el report semanal.

---

## 9.ter Pre-Flight Output Report (Checkpoint 2)

### 9.ter.1 Propósito

Es el **único** punto de control humano antes de que el sistema ejecute acciones online irreversibles: publicar, enviar emails, activar gasto en ads, postear en redes del cliente.

Reemplaza y consolida todos los micro-approvals que antes estaban dispersos:
- ❌ Approval Gatekeeper antes de Drive upload (Workflow B, antiguo nodo 7.5)
- ❌ Approval & Activation Gateway por plataforma de ads (Workflow C, antiguo nodo C3)
- ❌ Approval Gate sample review de cold email (Workflow E, antiguo nodo E8)
- ❌ Approval del Performance Analyst para mover budgets (Workflow D, antiguo nodo D5)

Todos esos se eliminan. **En su lugar, cada workflow termina su cooking generando un Pre-Flight Output Report unificado, y espera el "go for it" antes de la fase online.**

### 9.ter.2 Por qué un solo checkpoint y no varios

Tres razones:
1. **Fatiga de aprobación**: si el CEO recibe 8 notificaciones por día con micro-approvals, termina aprobando todo sin mirar. Una sola revisión sustantiva por workflow es mejor que 8 superficiales.
2. **Visión holística**: ver el output completo (copy + visual + plan de pauta + targeting + presupuesto) en un solo report permite detectar incoherencias que mirando cada pieza por separado se escapan.
3. **Una sola palabra mágica**: "go for it" es una decisión clara. Múltiples aprobaciones parciales generan estados ambiguos ("aprobé el copy pero no el visual, ¿qué hace el sistema?").

### 9.ter.3 Estructura del report

Todo Pre-Flight Output Report tiene 5 bloques fijos + bloques específicos del workflow:

**Bloques fijos (siempre):**

1. **Header**
   - workflow_run_id, brand_name, workflow_target, requester_name
   - timestamp de inicio del cooking y duración total
   - costo estimado del cooking (tokens IA + APIs externas consumidas)
   - costo estimado del go-live (presupuesto ads, emails a enviar, etc.)

2. **Input echo**
   - Resumen del brief que disparó el workflow (qué se pidió)
   - `weak_fields` y `warnings` del Quality Input Control si los hubo
   - Esto le recuerda al revisor qué prometió el sistema entregar

3. **Output preview (el contenido propiamente dicho)**
   - Bloque específico del workflow (ver 9.ter.4)

4. **Plan de ejecución online**
   - Lista paso a paso de qué pasa exactamente si se aprueba con "go for it"
   - Cada paso: qué API se llama, qué se publica/envía, en qué momento, con qué irreversibilidad
   - Ejemplo: "1) Publicar reel en IG @brand a las 10:00 AM (irreversible: se puede borrar pero queda en logs). 2) Activar campaña Meta con €50/día (reversible: pausable). 3) Enviar 500 emails vía Smartlead en los próximos 5 días (parcialmente reversible: pausable, pero los ya enviados no se desenvían)."

5. **Decisión solicitada**
   - Las opciones disponibles para el humano (ver 9.ter.5)

**Bloques específicos por workflow:**

#### Workflow A — Discovery Report
- Top 5 trends detectados con scores
- Para cada uno: source, hook_idea, funnel_stage_sugerido, SEO opportunity
- Recomendación de cuál(es) priorizar
- Plan online: crear BriefProposals en Airtable + notificar al equipo

#### Workflow B — Production Report
- Las N variantes generadas (default 3)
- Para cada variante: copy completo + asset preview (URL a Drive)
- Comparación lado a lado: hook diferente por variante, mismo key_message
- Plan online: subir assets a Drive con naming convention + crear Pieces en Airtable con status `ready_to_publish`

#### Workflow C — Distribution Report
- **Branch orgánico**: para cada canal, preview de cómo se va a ver el post (copy + media + hashtags + bio link)
- **Branch ads**: estructura completa de campañas por plataforma (campaign → adset → ads), audiencias, budgets, placements, objetivos
- **Branch blog**: post completo en markdown + meta tags + featured image
- **Branch lead capture**: landing URL + form schema + WhatsApp template a aprobar (si es la primera vez)
- Plan online: publicar/activar en cada canal en orden definido + setear webhooks para captura de lead

#### Workflow D — Performance Report
- Métricas crudas de la semana por plataforma
- Top performers / bottom performers
- Hipótesis del analyst
- **Cambios sugeridos al sistema**: nuevos Learnings a escribir, presupuestos a reasignar, ads a pausar
- Plan online: ejecutar los cambios de budget en APIs + escribir Learnings que alimenten futuros Strategy Director

#### Workflow E — Cold Email Report
- Muestra de 5 emails del batch (asunto + cuerpo + 3 follow-ups), elegidos randomly
- Stats del batch: total prospects, % verificados ok, % con email confiable, mailboxes asignados, cronograma de envío
- Plan online: crear campaña en Smartlead + cargar leads + activar secuencia con drip programado

### 9.ter.4 SPEC: agente `Pre-Flight Output Reporter`

- **Tipo**: `@n8n/n8n-nodes-langchain.agent`
- **Modelo**: Claude Sonnet 4.6
- **System prompt**:

```
Sos el Pre-Flight Output Reporter. Tu trabajo es producir UN report
claro, completo y honesto del output de un workflow ANTES de que el
sistema toque nada online.

PRINCIPIOS:
1) Honestidad total. Si algo del output es débil, lo decís. No vendés
   el trabajo.
2) Concreto sobre acciones irreversibles. El revisor debe saber qué
   se rompe si aprueba algo malo.
3) Resumen ejecutivo arriba, detalle abajo. El CEO debe poder decidir
   leyendo solo el resumen si tiene confianza. El detalle está para
   quien quiera profundizar.
4) Self-critique al final. ¿Qué podría salir mal? ¿Qué le falta a este
   output? Lo decís vos antes de que lo descubra el mercado.

INPUT: workflow_run_id (lee de Airtable WorkflowRuns + tablas
relacionadas según workflow_target).

OUTPUT: Markdown estructurado con los 5 bloques fijos + bloque
específico del workflow. Al final, enumerar opciones de decisión.

FORMATO DE LA SECCIÓN "DECISIÓN SOLICITADA" (siempre al final):

---
### Decisión

Para aprobar y ejecutar todo online, respondé con la frase EXACTA:

> go for it

Otras opciones:
- "corrijo X" → describir qué cambiar; el sistema vuelve a cocinar
  solo lo afectado
- "cancelo" → descartar todo el run, no ejecuta nada online
- "explicame X" → pedir más detalle sobre alguna sección antes de
  decidir

⚠️  Solo la frase EXACTA "go for it" (case-insensitive) dispara la
ejecución online. Cualquier otra respuesta es tratada como pedido
de revisión.
---
```

### 9.ter.5 Mecánica de decisión

El report se envía por Telegram (o Slack según preferencia del cliente) al `approver` definido en Airtable `Brands.default_approver_chat_id`. NO es un botón inline: requiere que el approver responda con texto.

**Reglas de parsing de la respuesta:**

| Respuesta del approver | Acción del sistema |
|---|---|
| `go for it` (cualquier capitalización) | Dispara fase online del workflow. Escribe en Airtable `WorkflowRuns.approval = "go_for_it"`, `approved_at = now`, `approved_by = chat_user`. |
| `corrijo X` / `cambio Y` / etc. | El sistema interpreta el feedback con un agente Claude Haiku que extrae qué bloques re-cocinar. Re-ejecuta SOLO los nodos afectados y vuelve a generar un Pre-Flight Output Report actualizado. |
| `cancelo` / `descartar` / `cancel` | Status del run → `cancelled`. No se ejecuta nada online. Los assets generados quedan en Drive como referencia pero no se publican. |
| `explicame X` | El reporter agent recibe la pregunta y responde con detalle sobre esa sección. NO ejecuta nada todavía. Espera respuesta siguiente. |
| Cualquier otra cosa | Tratado como pedido de revisión: el reporter responde "No reconocí tu respuesta. Para ejecutar online respondé exactamente `go for it`. Para cambios, describí qué corregir." |

**¿Por qué "go for it" exacto y no botón?**
- Un botón se puede tocar por accidente en el celular.
- Tipear 3 palabras es deliberado. Es la fricción mínima razonable para una acción que puede gastar cientos de euros o tocar inboxes ajenos.
- Case-insensitive: "Go For It", "GO FOR IT", "go for it" todas valen. Pero "go!" no, "ok dale" no, "aprobado" no.

### 9.ter.6 Manejo de correcciones (loop de revisión)

Cuando el approver responde con un pedido de corrección, el flujo es:

```
Pre-Flight Output Report v1
        │
        ▼
Approver: "corrijo el copy de la variante B, no menciones precio"
        │
        ▼
Correction Interpreter (Claude Haiku)
        │  → identifica: workflow=B, target=variant_B.copy,
        │     constraint=no_mention_price
        ▼
Re-cook solo del nodo afectado
        │  → Copywriter Agent corre de nuevo con el constraint
        │     adicional inyectado en el prompt
        ▼
Pre-Flight Output Report v2 (solo muestra qué cambió)
        │
        ▼
Approver: "go for it"
        │
        ▼
Fase online
```

El report v2 tiene un bloque adicional **"Cambios desde v1"** que muestra diff de lo que se modificó, para que el approver no tenga que releer todo.

Máximo 5 iteraciones de corrección antes de que el sistema fuerce un "cancelo" automático y pida abrir un nuevo run (evita loops infinitos por feedback inconsistente).

### 9.ter.7 Auditoría

Cada Pre-Flight Output Report (v1, v2, v3...) se guarda como row en Airtable `OutputReports` con:
- workflow_run_id, version, generated_at
- full_markdown (el report completo)
- approver_response, approved_at, approval_keyword
- changes_from_previous_version (si aplica)

Esto da trazabilidad total: en 6 meses podés mirar exactamente qué se publicó, cuándo, con qué aprobación, y qué cambios pidió el cliente vs lo que se ejecutó.

---

## 10. Esquema Airtable (single source of truth)

Tablas mínimas y campos clave:

### `Brands`
brand_id (auto), name, niche, target_audience, tone_of_voice, visual_style, dont_say, brand_guidelines_pdf_url, sample_winning_content_urls, sales_team_whatsapp_numbers, **meta_ad_account_id**, **instagram_business_id**, **tiktok_business_id**, **tiktok_ad_account_id**, **youtube_channel_id**, **google_ads_customer_id**, **blog_cms_type** (ghost/wordpress/static), **blog_api_url**, **blog_api_key_credential** (n8n credential ref), **published_urls** (multi, para internal linking del blog), **default_approver_chat_id** (Telegram chat ID que recibe los Pre-Flight Output Reports), **default_approver_name**, status, default_funnel_budget

### `Trends`
trend_id, brand_id (link), title, source, momentum_score, fit_score, hook_idea, funnel_stage_sugerido, status (pending_review/approved/discarded), detected_at

### `BriefProposals`
proposal_id, brand_id, trend_id, key_message, channel, format, funnel_stage, seo_keywords, **evergreen_blog_recommended** (boolean), status (awaiting_approval/approved/rejected), approved_at

### `Pieces`
piece_id, brief_id, variant_label (A/B/C), copy_text, asset_url, media_type, aspect_ratio, status (draft/ready_to_publish/published/archived), target_channels (multi: instagram_organic, instagram_ads, tiktok_organic, tiktok_ads, youtube_organic, youtube_ads, google_ads, blog), **youtube_video_id** (si publicado), **blog_post_url** (si aplica)

### `Campaigns`
campaign_id, brand_id, name, funnel_stage, **platform** (meta/tiktok/youtube/google), **platform_campaign_id** (ID en la plataforma respectiva), budget, start_date, end_date, status (pending_activation/active/paused/ended)

### `Leads`
lead_id, brand_id, campaign_id, piece_id, name, email, phone, message, score, temperature, priority, notified_at, source_utm

### `Metrics`
metric_id, piece_id (or ad_id), date, impressions, reach, clicks, spend, conversions, ctr, cpc, cpl

### `Learnings`
learning_id, brand_id, week_of, content (markdown del analyst)

### `BudgetChanges` (Workflow D — log autónomo)
change_id, brand_id, campaign_id, ad_id, platform, change_type (pause/increase_budget/decrease_budget), amount_before, amount_after, reasoning, executed_at, status (executed/blocked_by_rule), rule_violated (si aplica)

### `WeeklyReports` (Workflow D — archive autónomo)
report_id, brand_id, week_of, full_markdown, key_insights (multi), generated_at

### `OperationsAlerts` (las 3 excepciones del principio 0.0)
alert_id, type (tool_needed/credential_missing/payment_required), severity (info/warning/blocking), workflow_run_id (link, si aplica), description, action_required, setup_link, estimated_cost_eur, status (pending/acknowledged/resolved), created_at, resolved_at

### `WorkflowRuns` (Checkpoint 1 — Quality Input Control)
workflow_run_id, brand_id (link), workflow_target (discovery/production/distribution/performance_review/cold_email), requester_name, input_brief_json (el JSON completo del Quality Input Control), weak_fields (multi), warnings (multi), status (input_validated/cooking/output_report_generated/awaiting_approval/approved/cancelled/correcting), created_at, cooking_started_at, cooking_completed_at, approval ("go_for_it" o null), approved_at, approved_by, cancellation_reason (si aplica)

### `OutputReports` (Checkpoint 2 — Pre-Flight Output Report)
report_id, workflow_run_id (link), version (1, 2, 3...), generated_at, full_markdown (el report completo), approver_response, approval_keyword (extraído de la respuesta), changes_from_previous_version (markdown diff si v >1), cost_estimate_eur (tokens IA + APIs consumidas en el cooking), online_execution_cost_estimate_eur

### `OutboundCampaigns` (Workflow E)
campaign_id, brand_id, name, **pre_flight_brief** (JSON con todo lo que devolvió el E1), target_sector_json, icp_json, sharp_proposition, credibility_proof, cta_type, cta_link, target_volume, timeline_days, mailboxes_count, compliance_region, status (ready_to_scrape/scraping/enriching/verifying/copywriting/awaiting_approval/sending/paused/completed), created_by, **smartlead_campaign_id**

### `Prospects` (Workflow E — el único database consolidado)
prospect_id, outbound_campaign_id (link), company_name, company_website, company_domain, company_phone, company_address, company_size_estimate, company_industry, **contact_first_name**, **contact_last_name**, **contact_title**, **contact_email**, contact_linkedin_url, enrichment_source (apollo/hunter/manual), enrichment_confidence (0-1), email_verification_status (ok/catch_all/invalid/disposable/not_verified), status (raw/enriched/verified/sent/replied/bounced/unsubscribed/converted), **sent_at**, **first_reply_at**, **reply_category** (interested/not_now/not_interested/wrong_person/etc), lead_id (link a Leads si convirtió), source_query

### `EmailMailboxes` (Workflow E — health tracking)
mailbox_id, brand_id (link, opcional si es de la agencia propia), email_address, domain, smartlead_account_id, warmup_status, daily_send_limit, current_bounce_rate_7d, current_reply_rate_7d, current_spam_rate_7d, last_health_check, status (active/paused/cooling)

---

## 11. Roadmap de implementación

Sugerencia de orden, basado en cuánto bloquea al resto:

**Fase 1 — Fundación + Checkpoints universales (semana 1-3)**

Esta fase es CRÍTICA y no se puede saltear: los dos checkpoints son el esqueleto del que dependen todos los workflows.

1. Migrar `Brand Context` de dataTable a Airtable (`Brands` table con todos los IDs de plataforma + `default_approver_chat_id`)
2. Crear todas las tablas de Airtable vacías, incluyendo `WorkflowRuns` y `OutputReports`
3. **Construir Quality Input Control agent** (Checkpoint 1, sección 0.A) con form base + extensión B inicial (las otras extensiones se agregan a medida que se construyen los workflows respectivos)
4. **Construir Pre-Flight Output Reporter agent** (Checkpoint 2, sección 9.ter) con bloque específico de Workflow B inicial
5. **Construir Correction Interpreter** (Claude Haiku) que parsea respuestas del approver y rutea entre re-cook / cancel / explain
6. Setup Telegram Bot que recibe los reports y envía la respuesta del approver al webhook n8n
7. Agregar `funnel_stage` al brief schema actual
8. Agregar `Funnel Stage Classifier` y `Variant Generator` al Workflow B
9. Verificar end-to-end: input → cooking → output report → "go for it" → ejecución sobre 1 brand de prueba

→ Resultado: tenés multi-brand + 3 variantes + un solo punto de control humano, todo con auditoría completa en Airtable.

**Fase 2 — Distribución orgánica + captura de lead (semana 4-6)**

Cada nueva fase agrega: (a) extensión propia al Quality Input Control, (b) bloque propio al Pre-Flight Output Report.

10. Agregar extensión C al Quality Input Control
11. Agregar bloques específicos de C al Pre-Flight Output Reporter
12. Workflow C branch 1: Instagram Organic Publisher
13. Workflow C branch 1: YouTube Publisher + YouTube SEO Optimizer
14. Workflow C branch 3: Landing (Tally) + Lead Form Webhook + Lead Qualifier + Airtable Write + WhatsApp Notifier
15. Aprobar template de WhatsApp en Meta Business Manager (proceso ~24-48h)
16. (Opcional, paralelo) TikTok Organic Publisher si Business Account ya está verificado

→ Resultado: el sistema ya publica en IG + YouTube, captura leads y notifica al equipo de ventas. Todo pasa por los dos checkpoints universales.

**Fase 3 — Pautado (semana 7-10)**
17. Extender extensión C del QIC con campos de ads (budget por plataforma, audiencias)
18. Extender Pre-Flight Output Reporter para mostrar estructura completa de campañas multi-plataforma
19. Meta Ads Campaign Manager + API push (semana 7) — el más rápido de integrar
20. Google Ads Campaign Manager + API push (semana 8) — requiere developer token Standard
21. TikTok Ads Campaign Manager + API push (semana 9) — requiere Business Center verificado
22. YouTube Ads Campaign Manager (semana 10) — corre sobre Google Ads API, reutiliza credenciales
23. Click-to-WhatsApp ad flow + Conversation Router (Claude Haiku)

→ Resultado: pautado integrado en las 4 plataformas, con un solo "go for it" activando todo en simultáneo.

**Fase 4 — Discovery (semana 11-12)**
24. Agregar extensión A al Quality Input Control
25. Agregar bloque A al Pre-Flight Output Reporter
26. Workflow A: Trend Scout + integraciones de scraping
27. SEO Strategist + DataForSEO

→ Resultado: el sistema propone briefs proactivos en vez de esperar al chat del CEO.

**Fase 5 — Blog autónomo (semana 13-14)**
28. Setup CMS del cliente (Ghost preferido)
29. Extender Pre-Flight Output Reporter con bloque blog (preview del post completo)
30. Blog Brief Generator + Long-form Writer + Blog Publisher + SEO Indexing
31. Cross-promotion Trigger

→ Resultado: contenido evergreen publicado automáticamente sobre trends.

**Fase 6 — Loop de performance (semana 15-16)**
32. Agregar extensión D al Quality Input Control
33. Agregar bloque D al Pre-Flight Output Reporter
34. Workflow D: Metrics Collector multi-plataforma
35. Performance Analyst + Learnings table
36. Budget Optimizer (multi-plataforma)

→ Resultado: el sistema aprende y se optimiza solo (con aprobación humana en cambios de budget vía el mismo "go for it").

**Fase 7 — Cold Email Outbound (semana 17-20)**

Esta fase requiere preparación de infraestructura ANTES de escribir nodos n8n:

*Semana 17 — Infra (no es código todavía):*
37. Comprar 2-3 dominios secundarios por cliente (o por la agencia) en Cloudflare
38. Setup Google Workspace o Microsoft 365: 3-5 mailboxes por dominio
39. Configurar SPF, DKIM, DMARC en cada dominio (sin esto los emails van directo a spam)
40. Crear cuenta Smartlead con workspace por cliente
41. Conectar mailboxes a Smartlead y arrancar warmup (mínimo 14-21 días)

*Semana 18 — Quality Input + Scraping:*
42. Tablas Airtable: OutboundCampaigns + Prospects + EmailMailboxes
43. **Agregar extensión E al Quality Input Control universal** (sección 0.A.4) — esto reemplaza el "Pre-Flight Interview Agent" standalone de v1.2.0
44. **Agregar bloque E al Pre-Flight Output Reporter** (5 samples + stats del batch)
45. Prospect Scout Maps + Web (E2, E3) con Apify + Serper
46. Airtable Write Prospects (E4)

*Semana 19 — Enrichment + Copy:*
47. Data Enrichment con Apollo + Hunter fallback (E5)
48. Email Verification con Million Verifier (E6)
49. Cold Email Copywriter (E7)

*Semana 20 — Sending + Reply Handling:*
50. Smartlead Campaign Push (E9) — solo se ejecuta tras "go for it" del Checkpoint 2
51. Smartlead Webhook Listener + Inbox Reply Router (E10, E11)
52. Lead Push to Main Pipeline (E12) — conecta con WhatsApp Notifier existente
53. Domain & Inbox Health Monitor (E13)

→ Resultado: prospección B2B activa, totalmente integrada con el resto del sistema, controlada por los dos checkpoints universales.

> **Decisión importante sobre la Fase 7**: NO la arranques antes de tener Fase 2 (captura de lead + WhatsApp notifier) en producción, porque la Fase 7 reutiliza esa infraestructura. Sí podés correr Fase 7 en paralelo con Fases 3-6 si tenés bandwidth.

---

## 12. Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Meta cambia API o pricing | Diversificar: tener Telegram como canal de notificación alternativo si WhatsApp cae. Mantener publicación orgánica vía un scheduler externo (Metricool) como backup. |
| Token de Meta expira | Cron mensual que refresca long-lived token. Alerta si falla. |
| TikTok no aprueba la app o el Business Account | Mantener publicación TikTok manual con notificación n8n al community manager. Verificar Business Account antes de empezar (~24-72h). |
| YouTube quota exceeded | El upload bajó a ~100/día con quota default desde dic 2025. Si excedés: pedir quota extension a Google (free, ~1-2 semanas). Múltiples Google Cloud projects = múltiples quotas independientes. |
| Google Ads developer token sigue en "Test" | No se pueden operar accounts reales hasta tener Standard. Solicitar Standard apenas se valide el caso de uso (proceso de aprobación de Google, días a semanas). Mientras tanto operar Test Accounts. |
| Quality Score bajo en Google Ads | El SEO Strategist y el Long-form Writer deben alimentar las landing pages, no solo el blog. Landing page relevante + ad copy alineado = QS alto = CPC bajo. |
| Blog post no rankea | El Performance Analyst incluye GSC data: si después de 60 días un post no rankea top 20, dispara un "refresh agent" que reescribe basándose en SERP actual + posts top de competidores. |
| Costo Gemini sube | Strategy y Copywriter ya estarían en Claude (sección 5.6). Briefing puede caer a OpenAI GPT-OSS local si hace falta. |
| Lead falso / spam | Honeypot field en el form + rate limiting + Lead Qualifier descarta scores <2 sin notificar. |
| Equipo de ventas se satura de notificaciones | Lead Qualifier solo notifica score ≥ 4. Para hot leads (≥7), notificación urgente; para warm, digest diario. |
| Scraping de Meta Ad Library se rompe | Tener 2 providers (ScrapeCreators + Apify) y fallback entre ellos. |
| Múltiples plataformas = múltiples auth tokens que vencen | Cron unificado de health check semanal: pinguea cada API por brand. Si algún token está por vencer o ya falló, escala al canal de operations-alerts como "credencial / acceso faltante" (sección 0.0). |
| Sistema toma decisiones malas en autonomía | Los Pre-Flight Output Reports son la red de seguridad: el CEO ve TODO el cooking antes del go-live. Y los Learnings de Workflow D corrigen el rumbo en el siguiente ciclo. No agregar approval gates dispersos. |
| **Cold email**: dominio principal del cliente quemado | NUNCA enviar cold email desde el dominio principal. Usar siempre dominios secundarios (`get-clientname.com`, `try-clientname.com`) con warmup previo de 14-21 días. |
| **Cold email**: bounce rate alto destruye reputación | Email Verification (E6) es no-negociable antes de enviar. Health Monitor (E13) pausa mailboxes con bounce >3% automáticamente. |
| **Cold email**: spam complaints | Opt-out claro en cada email + permanent_suppression list respetada cross-campaign. Si spam_rate >0.1%, pausar dominio entero. |
| **Cold email**: GDPR / CASL / CAN-SPAM | El Pre-Flight Agent pregunta compliance_region. Para EU/UK: legitimate interest documentado + opt-out en cada email + no usar datos sensibles. Para Canadá (CASL) es más estricto: opt-in explícito casi obligatorio, evaluá si el canal vale el riesgo. |
| **Cold email**: respuestas perdidas en mailbox | El webhook listener (E10) es la red de seguridad. Si Smartlead falla, cron de backup chequea master inbox cada 30min. |
| Apollo / Hunter sin créditos en medio de una campaña | El Enrichment Agent (E5) verifica saldo antes de empezar y alerta si no alcanza para el target_volume del brief. |

---

## 13. Cómo Claude Code / Antigravity deberían usar este documento

Cuando el CEO te pida "construime el Workflow A", el agente debe:

1. Leer la sección 6 (`SPEC: Workflow A`).
2. Generar el JSON de n8n correspondiente, espejando la estructura del blueprint actual (mismos tipos de nodos donde aplique).
3. Crear las tablas Airtable referenciadas en sección 10 vía Airtable API.
4. Devolver un PR / archivo `.json` importable a n8n.

Cuando el CEO pida "agregame variant generation al workflow actual", el agente debe:

1. Leer sección 7.4.
2. Modificar el JSON existente `Marketing_Team_Blueprint_v1_3_0.json` insertando el nodo entre Copywriter y Aspect Ratio.
3. Devolver el diff y el JSON modificado.

Cuando el CEO pida "explicame cómo funciona el flujo de un lead", el agente debe:

1. Leer sección 4 y responder en lenguaje natural sin código.

---

## 14. Glosario rápido

- **TOFU/MOFU/BOFU**: Top/Middle/Bottom of Funnel. Etapas del recorrido del prospecto.
- **CTR**: Click-Through Rate. Clicks / impresiones.
- **CPL**: Cost Per Lead. Spend / leads generados.
- **CPM**: Cost Per Mille. Costo por cada 1000 impresiones.
- **CPC**: Cost Per Click.
- **CPV**: Cost Per View (YouTube, TikTok).
- **ROAS**: Return On Ad Spend. Revenue / spend.
- **GAQL**: Google Ads Query Language. Sintaxis SQL-like para queries a Google Ads API.
- **Performance Max / PMax**: campaign type de Google Ads que distribuye automáticamente en YouTube, Search, Display, Discover, Gmail, Maps.
- **Demand Gen**: reemplazo en 2026 del antiguo "Discovery Campaign" de Google.
- **Spark Ads** (TikTok): usar un post orgánico ya publicado como creativo de ad. Performance suele ser mejor que ads creados desde cero.
- **Quality Score**: scoring 1-10 de Google Ads que determina cuánto pagás por click. Depende de CTR esperado, relevancia del ad y experiencia de landing.
- **GSC**: Google Search Console. Da datos de búsqueda orgánica (queries, positions, CTR, impressions).
- **GA4**: Google Analytics 4. La versión actual (la anterior, Universal Analytics, fue discontinuada en 2023).
- **BSP**: Business Solution Provider de WhatsApp. Intermediario que algunas integraciones usan; con Cloud API directa de Meta no hace falta.
- **UTM**: parámetros de URL que identifican origen del tráfico para tracking.
- **Long-lived token**: token de Meta que dura 60 días en vez de 1-2 horas. Requiere refresh programático.
- **Developer token** (Google Ads): credencial extra (además del OAuth) para usar la API. Test = solo cuentas de prueba; Standard = cuentas reales.
- **ICP**: Ideal Customer Profile. La descripción del cliente perfecto del brand. En cold email es el filtro principal.
- **Warmup** (cold email): proceso de 14-28 días donde un mailbox nuevo manda/recibe emails simulados para que los proveedores (Gmail, Outlook) confíen en él antes de cold outreach real.
- **SPF / DKIM / DMARC**: 3 estándares DNS que prueban que un email viene de quien dice venir. Sin estos configurados, los emails van directo a spam.
- **Catch-all email**: dominio que acepta emails a cualquier dirección (ej: `cualquiercosa@empresa.com` no rebota). Riesgoso para verificar deliverability.
- **Bounce rate**: % de emails que rebotaron. >5% en cold email = dominio quemado en días.
- **GDPR / CASL / CAN-SPAM**: regulaciones de email marketing en EU / Canadá / USA. CASL es la más estricta.
- **Decision-maker** (B2B): persona que firma el cheque. No siempre es el CEO; depende del producto y la organización.
- **Sharp proposition**: oferta comercial concreta con resultado + plazo + diferenciador, opuesta a "ofrecemos servicios de calidad".
- **Master inbox / Unibox** (Smartlead): vista consolidada de todas las respuestas a través de todos los mailboxes de la campaña.

---

*Fin del blueprint v1.0.0. Iterar agregando casos no cubiertos a medida que aparezcan en producción.*
