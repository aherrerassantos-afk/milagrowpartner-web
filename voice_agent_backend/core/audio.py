"""
MILA Voice Agent — Audio Manager
Gestisce la registrazione dal microfono e il rilevamento del silenzio
"""

import asyncio
import io
import wave
import numpy as np
from rich.console import Console

console = Console()

# Costanti
SAMPLE_RATE = 16000       # Hz
CHANNELS = 1              # mono
CHUNK_SIZE = 1024         # frame per chunk
SILENCE_THRESHOLD = 500   # ampiezza RMS sotto cui considera silenzio
SILENCE_DURATION = 1.5    # secondi di silenzio per terminare la registrazione
MIN_RECORDING_DURATION = 0.5  # minimo secondi di audio


class AudioManager:
    """Gestisce l'acquisizione audio dal microfono."""

    def __init__(
        self,
        sample_rate: int = SAMPLE_RATE,
        silence_threshold: float = SILENCE_THRESHOLD,
        silence_duration: float = SILENCE_DURATION
    ):
        self.sample_rate = sample_rate
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        self._stream = None

    async def record_until_silence(self) -> bytes | None:
        """
        Registra audio dal microfono fino a quando rileva silenzio.

        Returns:
            Dati audio WAV come bytes, o None se nessun audio rilevato
        """
        import sounddevice as sd

        loop = asyncio.get_event_loop()
        frames = []
        silent_chunks = 0
        speaking_started = False

        silent_chunks_threshold = int(
            self.silence_duration * self.sample_rate / CHUNK_SIZE
        )

        def callback(indata, frames_count, time, status):
            nonlocal silent_chunks, speaking_started
            audio_chunk = indata[:, 0].copy()
            rms = np.sqrt(np.mean(audio_chunk ** 2)) * 32768

            if rms > self.silence_threshold:
                speaking_started = True
                silent_chunks = 0
                frames.append(audio_chunk)
            elif speaking_started:
                frames.append(audio_chunk)
                silent_chunks += 1

        # Registra con sounddevice
        def _record():
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=CHANNELS,
                callback=callback,
                blocksize=CHUNK_SIZE,
                dtype="float32"
            ):
                # Aspetta che la registrazione finisca (silenzio rilevato)
                import time
                max_wait = 30  # max 30 secondi per frase
                start = time.time()

                while (
                    not speaking_started or
                    silent_chunks < silent_chunks_threshold
                ):
                    time.sleep(0.05)
                    if time.time() - start > max_wait:
                        break

        await loop.run_in_executor(None, _record)

        if not frames or not speaking_started:
            return None

        # Controlla durata minima
        total_duration = len(frames) * CHUNK_SIZE / self.sample_rate
        if total_duration < MIN_RECORDING_DURATION:
            return None

        # Converti in WAV bytes
        audio_data = np.concatenate(frames)
        return self._to_wav_bytes(audio_data)

    def _to_wav_bytes(self, audio_np: np.ndarray) -> bytes:
        """Converte numpy array float32 in WAV bytes PCM int16."""
        # Converti float32 → int16
        audio_int16 = (audio_np * 32767).astype(np.int16)

        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav_file:
            wav_file.setnchannels(CHANNELS)
            wav_file.setsampwidth(2)  # 16-bit = 2 bytes
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(audio_int16.tobytes())

        buffer.seek(0)
        return buffer.read()

    async def play_beep(self, frequency: float = 880, duration: float = 0.15):
        """Suona un beep di conferma (feedback visivo sonoro)."""
        import sounddevice as sd

        t = np.linspace(0, duration, int(self.sample_rate * duration))
        beep = np.sin(2 * np.pi * frequency * t) * 0.3

        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: (sd.play(beep.astype(np.float32), self.sample_rate), sd.wait())
        )
