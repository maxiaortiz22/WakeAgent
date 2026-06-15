from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence

from voxshell.audio.frames import AudioFrame


@dataclass(frozen=True)
class Transcription:
    text: str
    confidence: float
    backend: str


class SpeechToTextBackend(Protocol):
    def transcribe(self, frames: Sequence[AudioFrame]) -> Transcription:
        """Transcribe recorded command frames."""
