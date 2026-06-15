from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, Sequence

from wakeagent.audio.frames import AudioFrame


@dataclass(frozen=True)
class Transcription:
    text: str
    confidence: float
    backend: str
    language: str | None = None


class SpeechToTextBackend(Protocol):
    def transcribe(self, frames: Sequence[AudioFrame]) -> Transcription:
        """Transcribe recorded command frames."""

    def transcribe_wav(self, wav_path: Path) -> Transcription:
        """Transcribe a recorded WAV file when the backend supports file input."""
