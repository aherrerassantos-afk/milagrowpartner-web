"""
MILA Voice Agent — Gmail Tool
Legge, scrive e gestisce email tramite Gmail API
"""

import os
import base64
import asyncio
from email.mime.text import MIMEText
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()


class GmailTool:
    """Interfaccia Gmail per il Voice Agent."""

    def __init__(self):
        self._service = None

    def _get_service(self):
        """Inizializza il client Gmail (lazy loading)."""
        if self._service is None:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            from google.auth.transport.requests import Request
            import json
            from pathlib import Path

            token_path = Path.home() / ".mila" / "google_token.json"

            if not token_path.exists():
                raise FileNotFoundError(
                    "Google token non trovato. Esegui: python auth/google_oauth.py"
                )

            creds = Credentials.from_authorized_user_file(str(token_path))

            # Auto-refresh se scaduto
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                # Salva token aggiornato
                token_path.write_text(creds.to_json())

            self._service = build("gmail", "v1", credentials=creds)
        return self._service

    async def get_recent_summary(self, max_results: int = 5) -> str:
        """
        Ritorna un sommario delle ultime email non lette.

        Returns:
            Stringa con le ultime email (mittente + oggetto)
        """
        loop = asyncio.get_event_loop()

        def _fetch():
            service = self._get_service()
            results = service.users().messages().list(
                userId="me",
                q="is:unread in:inbox",
                maxResults=max_results
            ).execute()

            messages = results.get("messages", [])
            summaries = []

            for msg_ref in messages:
                msg = service.users().messages().get(
                    userId="me",
                    id=msg_ref["id"],
                    format="metadata",
                    metadataHeaders=["From", "Subject", "Date"]
                ).execute()

                headers = {
                    h["name"]: h["value"]
                    for h in msg["payload"]["headers"]
                }
                summaries.append(
                    f"Da: {headers.get('From', 'Sconosciuto')}\n"
                    f"Oggetto: {headers.get('Subject', '(nessun oggetto)')}"
                )

            return "\n\n".join(summaries) if summaries else "Nessuna email non letta."

        return await loop.run_in_executor(None, _fetch)

    async def get_email_body(self, message_id: str) -> str:
        """Legge il corpo di una specifica email."""
        loop = asyncio.get_event_loop()

        def _fetch():
            service = self._get_service()
            msg = service.users().messages().get(
                userId="me",
                id=message_id,
                format="full"
            ).execute()

            # Estrai testo dalla struttura MIME
            payload = msg["payload"]
            body = self._extract_body(payload)
            return body[:2000]  # Limita a 2000 chars per il TTS

        return await loop.run_in_executor(None, _fetch)

    def _extract_body(self, payload: dict) -> str:
        """Estrae il testo plain dall'email."""
        if "parts" in payload:
            for part in payload["parts"]:
                if part["mimeType"] == "text/plain":
                    data = part["body"].get("data", "")
                    return base64.urlsafe_b64decode(data).decode("utf-8")
        elif payload.get("mimeType") == "text/plain":
            data = payload["body"].get("data", "")
            return base64.urlsafe_b64decode(data).decode("utf-8")
        return "(impossibile leggere il corpo dell'email)"

    async def send_email(self, to: str, subject: str, body: str) -> bool:
        """Invia un'email."""
        loop = asyncio.get_event_loop()

        def _send():
            service = self._get_service()
            message = MIMEText(body)
            message["to"] = to
            message["subject"] = subject

            raw = base64.urlsafe_b64encode(
                message.as_bytes()
            ).decode("utf-8")

            service.users().messages().send(
                userId="me",
                body={"raw": raw}
            ).execute()
            return True

        return await loop.run_in_executor(None, _send)

    async def search_emails(self, query: str, max_results: int = 5) -> str:
        """Cerca email con query Gmail."""
        loop = asyncio.get_event_loop()

        def _search():
            service = self._get_service()
            results = service.users().messages().list(
                userId="me",
                q=query,
                maxResults=max_results
            ).execute()

            messages = results.get("messages", [])
            if not messages:
                return f"Nessuna email trovata per: {query}"

            summaries = []
            for msg_ref in messages[:max_results]:
                msg = service.users().messages().get(
                    userId="me",
                    id=msg_ref["id"],
                    format="metadata",
                    metadataHeaders=["From", "Subject", "Date"]
                ).execute()
                headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}
                summaries.append(
                    f"Da: {headers.get('From', '?')} — {headers.get('Subject', '?')}"
                )

            return "\n".join(summaries)

        return await loop.run_in_executor(None, _search)
