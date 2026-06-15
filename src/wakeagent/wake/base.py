from __future__ import annotations

from typing import Protocol

from wakeagent.audio.frames import AudioFrame


class WakeWordDetector(Protocol):
    def detect(self, frame: AudioFrame) -> bool:
        """Return True when the wake word has been detected."""
