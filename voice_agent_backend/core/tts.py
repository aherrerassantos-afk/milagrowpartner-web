"""
MILA Voice Agent — Text to Speech
Converte testo in audio usando ElevenLabs (voce italiana naturale)
"""

import os
import asyncio
import io
from dotenv import load_dotenv

load_dotenv()


class TextToSpeech:
    """
    Gestisce la sintesi vocale (testo → voce).
    Provider: elevenlabs (qualità premium) | openai (backup)
    """

    def __init__(
        self,
        provider: str = "elevenlabs",
        voice_id: str = None,
        speed: float = 1.05
    ):
        self.provider = provider
        self.voice_id = voice_id or os.getenv("ELEVENLABS_VOICE_ID", "")
        self.speed = speed
        self._eleven_client = None

    def _get_elevenlabs_client(self):
        if self._eleven_client is None:
            from elevenlabs.client import ElevenLabs
            self._eleven_client = ElevenLabs(
                api_key=os.getenv("ELEVENLABS_API_KEY", "")
            )
        return self._eleven_client

    async def speak(self, text: str):
        """
        Sintetizza testo in voce e riproduce l'audio.

        Args:
            text: Testo da pronunciare
        """
        if not text or not text.strip():
            return

        # Pulizia testo (rimuovi markdown per il TTS)
        clean_text = self._clean_for_speech(text)

        if self.provider == "elevenlabs" and os.getenv("ELEVENLABS_API_KEY"):
            await self._speak_elevenlabs(clean_text)
        else:
            # Fallback: macOS say (offline, voce sintetica)
            await self._speak_macos(clean_text)

    async def _speak_elevenlabs(self, text: str):
        """Riproduce voce con ElevenLabs (streaming per bassa latenza)."""
        import sounddevice as sd
        import numpy as np

        client = self._get_elevenlabs_client()

        loop = asyncio.get_event_loop()

        def _generate():
            audio_stream = client.text_to_speech.convert(
                voice_id=self.voice_id,
                text=text,
                model_id="eleven_multilingual_v2",
                voice_settings={
                    "stability": 0.65,
                    "similarity_boost": 0.80,
                    "style": 0.10,
                    "use_speaker_boost": True
                },
                output_format="pcm_22050"  # 22kHz per bassa latenza
            )
            return b"".join(audio_stream)

        audio_bytes = await loop.run_in_executor(None, _generate)

        # Converti PCM in numpy e riproduci
        audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        sd.play(audio_np, samplerate=22050)
        sd.wait()

    async def _speak_macos(self, text: str):
        """
        Fallback: usa il TTS nativo di macOS (say).
        Funziona offline senza API key — voce 'Alice' italiano.
        """
        proc = await asyncio.create_subprocess_exec(
            "say",
            "-v", "Alice",    # voce italiana macOS
            "-r", "170",      # velocità parole al minuto
            text,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        await proc.wait()

    def _clean_for_speech(self, text: str) -> str:
        """Rimuove markdown e simboli non adatti al TTS."""
        import re
        # Rimuovi markdown
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)   # **bold**
        text = re.sub(r'\*(.+?)\*', r'\1', text)        # *italic*
        text = re.sub(r'`(.+?)`', r'\1', text)          # `code`
        text = re.sub(r'#{1,6}\s', '', text)             # # titoli
        text = re.sub(r'\|.+\|', '', text)               # | tabelle |
        text = re.sub(r'[-─═]+', '', text)               # linee
        text = re.sub(r'\n{2,}', '. ', text)             # doppi a capo → pausa
        text = re.sub(r'\n', ' ', text)                  # singoli a capo
        text = re.sub(r'  +', ' ', text)                 # spazi multipli
        # Emoji → niente
        text = re.sub(r'[^\x00-\x7F\xC0-\xFF\u00C0-\u024F\u1E00-\u1EFF]', '', text)
        return text.strip()
