"""
MILA Voice Agent — Google Drive Tool
Cerca, crea e condivide file su Google Drive
"""

import asyncio
from pathlib import Path
from typing import List, Optional


class DriveTool:
    """Interfaccia Google Drive per il Voice Agent."""

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

            self._service = build("drive", "v3", credentials=creds)
        return self._service

    async def search(self, query: str, max_results: int = 5) -> str:
        """Cerca file su Drive e ritorna i risultati come stringa."""
        loop = asyncio.get_event_loop()

        def _search():
            service = self._get_service()
            results = service.files().list(
                q=f"name contains '{query}' and trashed=false",
                pageSize=max_results,
                fields="files(id, name, mimeType, modifiedTime, webViewLink)"
            ).execute()

            files = results.get("files", [])
            if not files:
                return f"Nessun file trovato per: {query}"

            lines = []
            for f in files:
                name = f.get("name", "?")
                link = f.get("webViewLink", "#")
                modified = f.get("modifiedTime", "")[:10]
                lines.append(f"• {name} (modificato: {modified})\n  Link: {link}")

            return "\n\n".join(lines)

        return await loop.run_in_executor(None, _search)

    async def create_folder(self, name: str, parent_id: str = None) -> str:
        """Crea una nuova cartella su Drive."""
        loop = asyncio.get_event_loop()

        def _create():
            service = self._get_service()
            folder_metadata = {
                "name": name,
                "mimeType": "application/vnd.google-apps.folder"
            }
            if parent_id:
                folder_metadata["parents"] = [parent_id]

            folder = service.files().create(
                body=folder_metadata,
                fields="id, webViewLink"
            ).execute()

            return folder.get("webViewLink", "Cartella creata")

        return await loop.run_in_executor(None, _create)

    async def share_file(self, file_id: str, email: str, role: str = "reader") -> bool:
        """Condivide un file con un indirizzo email."""
        loop = asyncio.get_event_loop()

        def _share():
            service = self._get_service()
            permission = {"type": "user", "role": role, "emailAddress": email}
            service.permissions().create(
                fileId=file_id,
                body=permission
            ).execute()
            return True

        return await loop.run_in_executor(None, _share)

    async def upload_file(self, local_path: str, folder_id: str = None) -> str:
        """Carica un file locale su Drive."""
        loop = asyncio.get_event_loop()
        path = Path(local_path)

        def _upload():
            from googleapiclient.http import MediaFileUpload

            service = self._get_service()
            file_metadata = {"name": path.name}
            if folder_id:
                file_metadata["parents"] = [folder_id]

            media = MediaFileUpload(str(path), resumable=True)
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields="id, webViewLink"
            ).execute()

            return file.get("webViewLink", "File caricato")

        return await loop.run_in_executor(None, _upload)
