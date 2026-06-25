"""
MILA Voice Agent — Local Server
Server Flask locale che connette l'interfaccia web al MILA HOLDING BRAIN (n8n)
Avvia con: python3 server.py
Apri: http://localhost:3333
"""

import os
import subprocess
import json
import urllib.request
import urllib.error
import threading
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder=".")
CORS(app)

# ── Config ──────────────────────────────────────────────────────
N8N_BRAIN_URL       = "https://aherreras.app.n8n.cloud/webhook/mila-holding-brain/chat"
SESSION_ID          = "mila-voice-local-app"
PORT                = 3333
ELEVENLABS_API_KEY  = "sk_6850414ef429e3c774d739434599ee66d2f04850182e9e0a"
ELEVENLABS_VOICE_ID = "TgSKipUvZrUHVPv7imoO"   # la sapa voice — voce ufficiale Mila ✅
ADAM_MP3_PATH       = os.path.join(os.path.dirname(__file__), "voice_adam_normal.mp3")
OPENAI_API_KEY      = os.getenv("OPENAI_API_KEY", "")


@app.route("/")
def index():
    """Serve l'interfaccia principale."""
    return send_from_directory(".", "index.html")


@app.route("/chat", methods=["POST"])
def chat():
    """
    Riceve il testo dell'utente, lo manda al MILA HOLDING BRAIN,
    restituisce la risposta testuale.
    """
    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Messaggio vuoto"}), 400

    print(f"\n👤 Utente: {user_message}")

    # Chiama il MILA HOLDING BRAIN su n8n
    payload = json.dumps({
        "chatInput": user_message,
        "sessionId": SESSION_ID
    }).encode("utf-8")

    req = urllib.request.Request(
        N8N_BRAIN_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            result = json.loads(resp.read())
            brain_response = (
                result.get("output") or
                result.get("text") or
                result.get("message") or
                "Non ho capito, puoi ripetere?"
            )
            print(f"🧠 Mila: {brain_response[:150]}...")
            return jsonify({"response": brain_response})

    except urllib.error.URLError as e:
        print(f"❌ Errore connessione Brain: {e}")
        return jsonify({
            "response": "Scusa, ho problemi di connessione al cervello centrale. Riprova tra un secondo."
        })
    except Exception as e:
        print(f"❌ Errore: {e}")
        return jsonify({"response": "Ho avuto un errore tecnico. Riprova."})


@app.route("/preventivi", methods=["GET"])
def get_preventivi():
    """
    Chiama il workflow n8n PBA preventivi e restituisce i dati a Mila.
    Mila può usare questo endpoint per rispondere a domande sui preventivi PBA.
    """
    try:
        req = urllib.request.Request(
            "https://aherreras.app.n8n.cloud/webhook/mila-preventivi",
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/speak", methods=["POST"])
def speak():
    """
    TTS con priorità:
    1. ElevenLabs API (Adam) — se crediti disponibili
    2. OpenAI TTS (alloy/nova) — se API key disponibile
    3. macOS say -v Alice — fallback offline gratuito
    """
    data = request.get_json()
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"ok": False})

    import re
    clean = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    clean = re.sub(r'\*(.+?)\*', r'\1', clean)
    clean = re.sub(r'`(.+?)`', r'\1', clean)
    clean = re.sub(r'#{1,6}\s?', '', clean)
    clean = re.sub(r'\|[^\n]+\|', '', clean)
    clean = re.sub(r'[-─═•]+\s*', ' ', clean)
    clean = re.sub(r'\n+', '. ', clean)
    clean = re.sub(r'\s+', ' ', clean).strip()
    if len(clean) > 700:
        clean = clean[:697] + "..."

    # Lancia TTS in thread separato (non blocca la risposta HTTP)
    threading.Thread(target=_speak_async, args=(clean,), daemon=True).start()
    return jsonify({"ok": True})


def _speak_async(text: str):
    """Esegue TTS con fallback automatico."""
    # ── Tentativo 1: ElevenLabs (Adam) ──────────────────────────
    if _try_elevenlabs(text):
        return
    # ── Tentativo 2: OpenAI TTS ─────────────────────────────────
    if OPENAI_API_KEY and _try_openai_tts(text):
        return
    # ── Fallback: macOS Alice ────────────────────────────────────
    _speak_macos(text)


def _try_elevenlabs(text: str) -> bool:
    """Genera e riproduce audio con ElevenLabs. Ritorna True se OK."""
    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
        payload = json.dumps({
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.60, "similarity_boost": 0.85},
            "speed": 1.5
        }).encode()
        req = urllib.request.Request(url, data=payload, headers={
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg"
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            audio = resp.read()
        tmp = "/tmp/mila_eleven.mp3"
        with open(tmp, "wb") as f:
            f.write(audio)
        subprocess.run(["afplay", tmp], check=True)
        print("🔊 ElevenLabs Adam OK")
        return True
    except Exception as e:
        print(f"⚠️  ElevenLabs non disponibile ({e}) — fallback")
        return False


def _try_openai_tts(text: str) -> bool:
    """Genera e riproduce audio con OpenAI TTS. Ritorna True se OK."""
    try:
        url = "https://api.openai.com/v1/audio/speech"
        payload = json.dumps({
            "model": "tts-1",
            "input": text,
            "voice": "nova",    # voce femminile naturale
            "speed": 1.05
        }).encode()
        req = urllib.request.Request(url, data=payload, headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            audio = resp.read()
        tmp = "/tmp/mila_openai.mp3"
        with open(tmp, "wb") as f:
            f.write(audio)
        subprocess.run(["afplay", tmp], check=True)
        print("🔊 OpenAI TTS OK")
        return True
    except Exception as e:
        print(f"⚠️  OpenAI TTS non disponibile ({e}) — fallback")
        return False


def _speak_macos(text: str):
    """Fallback offline: macOS say con voce Alice (italiano)."""
    subprocess.run(
        ["say", "-v", "Alice", "-r", "243", text],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    print("🔊 macOS Alice OK")


@app.route("/stop-speech", methods=["POST"])
def stop_speech():
    """Interrompe la voce in corso."""
    try:
        subprocess.run(["pkill", "-f", "say"], capture_output=True)
        return jsonify({"ok": True})
    except Exception:
        return jsonify({"ok": False})


if __name__ == "__main__":
    print("\n" + "═" * 55)
    print("  🧠  MILA VOICE AGENT — Server Locale")
    print("═" * 55)
    print(f"  URL:    http://localhost:{PORT}")
    print(f"  Brain:  {N8N_BRAIN_URL[:50]}...")
    print(f"  Voce:   ElevenLabs La Sapa (cloned) → macOS Alice (fallback)")
    print("═" * 55)
    print("  Premi Ctrl+C per fermare\n")

    # Saluto vocale di avvio con file Adam scaricato
    def _greet():
        import time; time.sleep(1.5)
        if os.path.exists(ADAM_MP3_PATH):
            subprocess.Popen(["afplay", ADAM_MP3_PATH],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            _speak_macos("Sistema inizializzato. Sono Mila, pronta.")
    threading.Thread(target=_greet, daemon=True).start()

    app.run(host="0.0.0.0", port=PORT, debug=False)
