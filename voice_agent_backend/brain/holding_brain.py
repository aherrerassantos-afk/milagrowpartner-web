"""
MILA Voice Agent — Holding Brain Client
Connette l'agente vocale al MILA HOLDING BRAIN su n8n
"""

import os
import asyncio
import json
import httpx
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from rich.console import Console

load_dotenv()
console = Console()

BRAIN_URL = os.getenv(
    "N8N_BRAIN_URL",
    "https://aherreras.app.n8n.cloud/webhook/mila-holding-brain/chat"
)
TIMEOUT = 45  # secondi


class HoldingBrain:
    """
    Client per il MILA HOLDING BRAIN (n8n).
    Invia messaggi e riceve risposte con contesto holding completo.
    """

    def __init__(
        self,
        brain_url: str = BRAIN_URL,
        session_id: str = "mila-voice-local",
        timeout: int = TIMEOUT
    ):
        self.brain_url = brain_url
        self.session_id = session_id
        self.timeout = timeout

    async def chat(
        self,
        message: str,
        tools: Dict = None,
        conversation_history: List[Dict] = None
    ) -> str:
        """
        Invia un messaggio al Holding Brain e ottieni la risposta.

        Il Brain conosce già tutte le 7 aziende e i loro contesti.
        I tool locali (Gmail, Calendar, Drive) vengono allegati come
        contesto aggiuntivo al messaggio quando rilevanti.

        Args:
            message: Input dell'utente (già trascritto da STT)
            tools: Tool locali disponibili (Gmail, Calendar, Drive, etc.)
            conversation_history: Storia della conversazione

        Returns:
            Risposta testuale del Holding Brain
        """

        # Arricchisci il messaggio con contesto tool se necessario
        enriched_message = await self._enrich_with_tools(message, tools)

        payload = {
            "chatInput": enriched_message,
            "sessionId": self.session_id
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.brain_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                data = response.json()

                # Estrai la risposta testuale
                brain_response = (
                    data.get("output") or
                    data.get("text") or
                    data.get("message") or
                    "Non ho capito. Puoi ripetere?"
                )

                # Controlla se il Brain vuole eseguire un'azione locale
                await self._execute_local_actions(brain_response, tools)

                return brain_response

        except httpx.TimeoutException:
            console.print("[red]⏱️  Brain timeout — risposta troppo lenta[/red]")
            return "Scusa, sto impiegando troppo tempo. Riprova tra un secondo."

        except httpx.HTTPStatusError as e:
            console.print(f"[red]❌ Errore HTTP Brain: {e.response.status_code}[/red]")
            return "Ho avuto un problema di connessione. Riprova."

        except Exception as e:
            console.print(f"[red]❌ Errore Brain: {e}[/red]")
            return "Scusa, ho avuto un problema tecnico."

    async def _enrich_with_tools(self, message: str, tools: Dict) -> str:
        """
        Aggiunge dati live dai tool locali al messaggio se rilevanti.
        Esempio: se chiedi "cosa ho oggi?" → alleghi gli eventi del calendario.
        """
        if not tools:
            return message

        message_lower = message.lower()
        context_parts = []

        # Calendario — se chiedi eventi/riunioni
        if any(kw in message_lower for kw in [
            "oggi", "domani", "calendario", "riunione", "appuntamento",
            "call", "meeting", "settimana", "agenda"
        ]):
            try:
                calendar = tools.get("calendar")
                if calendar:
                    events = await calendar.get_today_events()
                    if events:
                        context_parts.append(f"[CALENDARIO OGGI]\n{events}")
            except Exception:
                pass

        # Email — se chiedi email
        if any(kw in message_lower for kw in [
            "email", "mail", "posta", "inbox", "messaggio", "scritto"
        ]):
            try:
                gmail = tools.get("gmail")
                if gmail:
                    emails = await gmail.get_recent_summary(max_results=5)
                    if emails:
                        context_parts.append(f"[ULTIME EMAIL]\n{emails}")
            except Exception:
                pass

        if context_parts:
            context = "\n\n".join(context_parts)
            return f"{message}\n\n---\n{context}"

        return message

    async def _execute_local_actions(self, response: str, tools: Dict):
        """
        Esegue azioni locali se il Brain le richiede nel JSON di risposta.
        Il Brain può includere un blocco JSON con azioni da eseguire.
        """
        if not tools or "ACTION:" not in response:
            return

        try:
            # Cerca blocco azione nel formato: ACTION: {"type": "...", ...}
            import re
            action_match = re.search(r'ACTION:\s*(\{[^}]+\})', response)
            if not action_match:
                return

            action = json.loads(action_match.group(1))
            action_type = action.get("type")

            if action_type == "create_calendar_event":
                calendar = tools.get("calendar")
                if calendar:
                    await calendar.create_event(
                        title=action.get("title"),
                        start=action.get("start"),
                        end=action.get("end"),
                        description=action.get("description", "")
                    )
                    console.print("[green]📅 Evento creato nel calendario[/green]")

            elif action_type == "send_email":
                gmail = tools.get("gmail")
                if gmail:
                    await gmail.send_email(
                        to=action.get("to"),
                        subject=action.get("subject"),
                        body=action.get("body")
                    )
                    console.print("[green]📧 Email inviata[/green]")

        except Exception as e:
            console.print(f"[yellow]⚠️  Azione locale fallita: {e}[/yellow]")
