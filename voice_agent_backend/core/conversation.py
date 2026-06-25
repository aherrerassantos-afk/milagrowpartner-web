"""
MILA Voice Agent — Conversation Manager
Gestisce la memoria e il contesto della conversazione
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict


@dataclass
class Message:
    role: str           # "user" | "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)


class ConversationManager:
    """
    Gestisce la storia della conversazione locale.
    Mantiene le ultime N interazioni in memoria.
    """

    def __init__(self, max_history: int = 20):
        self.max_history = max_history
        self._messages: List[Message] = []
        self.session_start = datetime.now()

    @property
    def history(self) -> List[Dict[str, str]]:
        """Ritorna la storia in formato lista di dict."""
        return [
            {"role": msg.role, "content": msg.content}
            for msg in self._messages
        ]

    def add(self, user: str, assistant: str):
        """Aggiunge uno scambio user/assistant alla storia."""
        self._messages.append(Message(role="user", content=user))
        self._messages.append(Message(role="assistant", content=assistant))

        # Mantieni solo gli ultimi max_history messaggi
        if len(self._messages) > self.max_history * 2:
            self._messages = self._messages[-(self.max_history * 2):]

    def clear(self):
        """Svuota la storia della conversazione."""
        self._messages = []

    def summary(self) -> str:
        """Restituisce un riassunto della sessione."""
        duration = datetime.now() - self.session_start
        n_exchanges = len(self._messages) // 2
        return (
            f"Sessione iniziata alle {self.session_start.strftime('%H:%M')} · "
            f"{n_exchanges} scambi · "
            f"Durata: {int(duration.total_seconds() // 60)} minuti"
        )
