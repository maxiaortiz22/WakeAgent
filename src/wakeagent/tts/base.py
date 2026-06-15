from __future__ import annotations

from typing import Protocol


class Speaker(Protocol):
    def speak(self, text: str) -> None:
        """Render assistant output to the user."""
