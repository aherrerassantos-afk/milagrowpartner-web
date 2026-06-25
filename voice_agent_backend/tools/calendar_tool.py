"""
MILA Voice Agent — Google Calendar Tool
Legge e crea eventi nel calendario
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path


class CalendarTool:
    """Interfaccia Google Calendar per il Voice Agent."""

    def __init__(self):
        self._service = None

    def _get_service(self):
        if self._service is None:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            from google.auth.transport.requests import Request

            token_path = Path.home() / ".mila" / "google_token.json"
            if not token_path.exists():
                raise FileNotFoundError("Google token non trovato.")

            creds = Credentials.from_authorized_user_file(str(token_path))
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                token_path.write_text(creds.to_json())

            self._service = build("calendar", "v3", credentials=creds)
        return self._service

    async def get_today_events(self) -> str:
        """Ritorna gli eventi di oggi come stringa leggibile."""
        loop = asyncio.get_event_loop()

        def _fetch():
            service = self._get_service()
            now = datetime.utcnow()
            start_of_day = now.replace(hour=0, minute=0, second=0).isoformat() + "Z"
            end_of_day = now.replace(hour=23, minute=59, second=59).isoformat() + "Z"

            events_result = service.events().list(
                calendarId="primary",
                timeMin=start_of_day,
                timeMax=end_of_day,
                singleEvents=True,
                orderBy="startTime"
            ).execute()

            events = events_result.get("items", [])
            if not events:
                return "Nessun evento oggi."

            lines = []
            for event in events:
                start = event["start"].get("dateTime", event["start"].get("date", ""))
                if "T" in start:
                    time_str = datetime.fromisoformat(start.replace("Z", "+00:00")).strftime("%H:%M")
                else:
                    time_str = "tutto il giorno"

                lines.append(f"• {time_str} — {event.get('summary', 'Senza titolo')}")

            return "\n".join(lines)

        return await loop.run_in_executor(None, _fetch)

    async def get_week_events(self) -> str:
        """Ritorna gli eventi della settimana."""
        loop = asyncio.get_event_loop()

        def _fetch():
            service = self._get_service()
            now = datetime.utcnow()
            week_end = now + timedelta(days=7)

            events_result = service.events().list(
                calendarId="primary",
                timeMin=now.isoformat() + "Z",
                timeMax=week_end.isoformat() + "Z",
                singleEvents=True,
                orderBy="startTime",
                maxResults=20
            ).execute()

            events = events_result.get("items", [])
            if not events:
                return "Nessun evento questa settimana."

            lines = []
            for event in events:
                start = event["start"].get("dateTime", event["start"].get("date", ""))
                if "T" in start:
                    dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
                    date_str = dt.strftime("%a %d/%m %H:%M")
                else:
                    date_str = start

                lines.append(f"• {date_str} — {event.get('summary', 'Senza titolo')}")

            return "\n".join(lines)

        return await loop.run_in_executor(None, _fetch)

    async def create_event(
        self,
        title: str,
        start: str,
        end: str,
        description: str = "",
        attendees: List[str] = None
    ) -> str:
        """Crea un nuovo evento nel calendario."""
        loop = asyncio.get_event_loop()

        def _create():
            service = self._get_service()
            event_body = {
                "summary": title,
                "description": description,
                "start": {"dateTime": start, "timeZone": "Europe/Rome"},
                "end": {"dateTime": end, "timeZone": "Europe/Rome"},
            }

            if attendees:
                event_body["attendees"] = [{"email": e} for e in attendees]

            event = service.events().insert(
                calendarId="primary",
                body=event_body
            ).execute()

            return event.get("htmlLink", "Evento creato")

        return await loop.run_in_executor(None, _create)
