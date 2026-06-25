"""
MILA Voice Agent — Speech to Text
Trascrive audio in testo usando Whisper (locale) o Deepgram (cloud)
"""

import os
import io
import asyncio
import tempfile
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class SpeechToText:
    """
    Gestisce la trascrizione voce → testo.
    Provider: whisper (locale, privacy totale) | deepgram (cloud, più veloce)
    """

    def __init__(self, provider: str = "whisper", model_size: str = "small"):
        self.provider = provider
        self.model_size = model_size
        self._whisper_model = None
        self._deepgram_client = None

    def _load_whisper(self):
        """Carica il modello Whisper (lazy loading — solo al primo uso)."""
        if self._whisper_model is None:
            import whisper
            from rich.console import Console
            Console().print(f"[dim]📥 Caricamento Whisper '{self.model_size}'...[/dim]")
            self._whisper_model = whisper.load_model(self.model_size)
            Console().print("[dim]✅ Whisper pronto[/dim]")
        return self._whisper_model

    def _load_deepgram(self):
        """Inizializza client Deepgram."""
        if self._deepgram_client is None:
            from deepgram import DeepgramClient
            self._deepgram_client = DeepgramClient(os.getenv("DEEPGRAM_API_KEY", ""))
        return self._deepgram_client

    async def transcribe(self, audio_data: bytes, language: str = "it") -> str:
        """
        Trascrive audio bytes → stringa testo.

        Args:
            audio_data: Dati audio WAV raw
            language: Codice lingua (it, es, en)

        Returns:
            Testo trascritto
        """
        if self.provider == "whisper":
            return await self._transcribe_whisper(audio_data, language)
        elif self.provider == "deepgram":
            return await self._transcribe_deepgram(audio_data, language)
        else:
            raise ValueError(f"Provider STT non supportato: {self.provider}")

    async def _transcribe_whisper(self, audio_data: bytes, language: str) -> str:
        """Trascrizione locale con Whisper (privacy totale)."""
        loop = asyncio.get_event_loop()

        def _run():
            model = self._load_whisper()
            # Salva audio temporaneo su disco
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(audio_data)
                tmp_path = tmp.name

            try:
                result = model.transcribe(
                    tmp_path,
                    language=language,
                    fp16=False,
                    condition_on_previous_text=False
                )
                return result["text"].strip()
            finally:
                Path(tmp_path).unlink(missing_ok=True)

        # Esegui in thread separato (Whisper è CPU-bound)
        text = await loop.run_in_executor(None, _run)
        return text

    async def _transcribe_deepgram(self, audio_data: bytes, language: str) -> str:
        """Trascrizione cloud con Deepgram (più veloce, ~300ms)."""
        from deepgram import PrerecordedOptions

        client = self._load_deepgram()

        lang_map = {"it": "it", "es": "es", "en": "en-US"}
        dg_language = lang_map.get(language, "it")

        options = PrerecordedOptions(
            model="nova-2",
            language=dg_language,
            smart_format=True,
            punctuate=True,
        )

        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: client.listen.prerecorded.v("1").transcribe_file(
                {"buffer": audio_data, "mimetype": "audio/wav"},
                options
            )
        )

        try:
            return response.results.channels[0].alternatives[0].transcript
        except (IndexError, AttributeError):
            return ""
