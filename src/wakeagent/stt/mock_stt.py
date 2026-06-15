from __future__ import annotations

from pathlib import Path
from typing import Sequence

from wakeagent.audio.frames import AudioFrame
from wakeagent.stt.base import Transcription


class MockSTTBackend:
    def __init__(self, transcript: str = "status") -> None:
        self.transcript = transcript

    def transcribe(self, frames: Sequence[AudioFrame]) -> Transcription:
        return Transcription(text=self.transcript, confidence=1.0, backend="mock")

    def transcribe_wav(self, wav_path: Path) -> Transcription:
        return Transcription(text=self.transcript, confidence=1.0, backend="mock")
