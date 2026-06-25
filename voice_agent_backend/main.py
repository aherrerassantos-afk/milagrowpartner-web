#!/usr/bin/env python3
"""
MILA VOICE AGENT — Entry Point
Avvia l'assistente vocale IA della holding Mila Collective SAS
"""

import asyncio
import signal
import sys
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from core.audio import AudioManager
from core.stt import SpeechToText
from core.tts import TextToSpeech
from core.conversation import ConversationManager
from brain.holding_brain import HoldingBrain
from tools.gmail_tool import GmailTool
from tools.calendar_tool import CalendarTool
from tools.drive_tool import DriveTool

console = Console()

BANNER = """
╔══════════════════════════════════════════════════════════════╗
║           MILA VOICE AGENT v1.0                              ║
║           Holding Mila Collective SAS                        ║
║                                                              ║
║  🏛️  Palazzo Blue Arroyo    📅  Smartsbookings              ║
║  🏗️  Toscan Costruzioni     🚀  Mila Grow Partner            ║
║  💻  IT Assistance          🫒  Tavola dei Santi             ║
║  🧹  Blue Cleaning                                           ║
╚══════════════════════════════════════════════════════════════╝
"""


class MilaVoiceAgent:
    """Agente vocale principale — coordina tutti i componenti."""

    def __init__(self):
        self.running = False
        self.audio = AudioManager()
        self.stt = SpeechToText()
        self.tts = TextToSpeech()
        self.brain = HoldingBrain()
        self.conversation = ConversationManager()

        # Tool disponibili
        self.tools = {
            "gmail": GmailTool(),
            "calendar": CalendarTool(),
            "drive": DriveTool(),
        }

    async def start(self):
        """Avvia l'agente vocale."""
        console.print(BANNER, style="bold blue")
        console.print(Panel(
            "[green]✅ MILA è pronta. Parla o premi Ctrl+Shift+M[/green]",
            title="Stato",
            border_style="green"
        ))

        self.running = True

        # Saluto iniziale
        await self.tts.speak(
            "Ciao! Sono Mila, il tuo assistente della holding. "
            "Cosa posso fare per te oggi?"
        )

        # Loop principale
        await self._main_loop()

    async def _main_loop(self):
        """Loop principale di ascolto e risposta."""
        while self.running:
            try:
                # 1. Ascolta input vocale
                console.print("\n[dim]🎙️  In ascolto...[/dim]")
                audio_data = await self.audio.record_until_silence()

                if audio_data is None:
                    continue

                # 2. Trascrivi voce → testo
                console.print("[dim]⚙️  Trascrizione in corso...[/dim]")
                text = await self.stt.transcribe(audio_data)

                if not text or len(text.strip()) < 2:
                    continue

                console.print(f"\n[bold cyan]Tu:[/bold cyan] {text}")

                # 3. Invia al Holding Brain
                console.print("[dim]🧠  Il Brain sta ragionando...[/dim]")
                response = await self.brain.chat(
                    message=text,
                    tools=self.tools,
                    conversation_history=self.conversation.history
                )

                if not response:
                    response = "Scusa, ho avuto un problema. Riprova."

                # 4. Aggiorna storia conversazione
                self.conversation.add(user=text, assistant=response)

                # 5. Rispondi con voce
                console.print(f"\n[bold magenta]Mila:[/bold magenta] {response}\n")
                await self.tts.speak(response)

            except KeyboardInterrupt:
                await self.stop()
                break
            except Exception as e:
                console.print(f"[red]Errore: {e}[/red]")
                await self.tts.speak("Scusa, ho avuto un piccolo problema tecnico.")

    async def stop(self):
        """Ferma l'agente."""
        self.running = False
        await self.tts.speak("Arrivederci! A presto.")
        console.print("\n[yellow]👋 MILA spenta.[/yellow]")


def handle_shutdown(signum, frame):
    """Gestisce Ctrl+C in modo pulito."""
    console.print("\n[yellow]Spegnimento in corso...[/yellow]")
    sys.exit(0)


async def main():
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    agent = MilaVoiceAgent()
    await agent.start()


if __name__ == "__main__":
    asyncio.run(main())
