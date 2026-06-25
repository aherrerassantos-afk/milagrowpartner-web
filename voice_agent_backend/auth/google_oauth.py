"""
MILA Voice Agent — Google OAuth Setup
Esegui questo script UNA VOLTA per ottenere il token Google.
Il token viene salvato in ~/.mila/google_token.json e si auto-rinnova.
"""

import os
import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from dotenv import load_dotenv

load_dotenv()

# Permessi richiesti
SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",     # leggi + scrivi email
    "https://www.googleapis.com/auth/calendar",          # calendario completo
    "https://www.googleapis.com/auth/drive",             # Drive completo
]

TOKEN_PATH = Path.home() / ".mila" / "google_token.json"
CREDENTIALS_PATH = Path("auth/google_credentials.json")


def setup_google_auth():
    """
    Setup OAuth 2.0 per Google APIs.

    PREREQUISITI:
    1. Vai su https://console.cloud.google.com
    2. Crea un progetto "MILA Voice Agent"
    3. Attiva: Gmail API, Calendar API, Drive API
    4. Crea credenziali OAuth 2.0 (tipo: App desktop)
    5. Scarica il JSON e salvalo come: auth/google_credentials.json
    6. Esegui questo script: python auth/google_oauth.py
    """

    print("=" * 60)
    print("  MILA Voice Agent — Setup Google OAuth")
    print("=" * 60)

    # Crea la cartella ~/.mila se non esiste
    TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)

    creds = None

    # Controlla se esiste già un token valido
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    # Se non valido o scaduto, autorizza di nuovo
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Aggiornamento token scaduto...")
            creds.refresh(Request())
        else:
            if not CREDENTIALS_PATH.exists():
                print(f"\n❌ File credenziali non trovato: {CREDENTIALS_PATH}")
                print("\nCome ottenerlo:")
                print("1. Vai su: https://console.cloud.google.com")
                print("2. Crea progetto → 'MILA Voice Agent'")
                print("3. API & Services → Enable APIs:")
                print("   - Gmail API")
                print("   - Google Calendar API")
                print("   - Google Drive API")
                print("4. Credentials → Create → OAuth client ID → Desktop App")
                print("5. Download JSON → salva come: auth/google_credentials.json")
                print("6. Riesegui questo script")
                return False

            print("\n🌐 Apertura browser per autorizzazione Google...")
            print("   Seleziona il tuo account Google e concedi i permessi.\n")

            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_PATH),
                SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Salva il token
        TOKEN_PATH.write_text(creds.to_json())
        print(f"\n✅ Token salvato in: {TOKEN_PATH}")

    print("\n✅ Google OAuth configurato correttamente!")
    print("   Permessi attivi:")
    for scope in SCOPES:
        service = scope.split("/")[-1]
        print(f"   • {service}")

    return True


if __name__ == "__main__":
    success = setup_google_auth()
    if success:
        print("\n🚀 Puoi ora avviare MILA: python main.py")
    else:
        print("\n❌ Setup fallito. Segui le istruzioni sopra.")
        exit(1)
