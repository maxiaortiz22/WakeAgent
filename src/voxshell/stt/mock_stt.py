from __future__ import annotations

from typing import Sequence

from voxshell.audio.frames import AudioFrame
from voxshell.stt.base import Transcription


class MockSTTBackend:
    def __init__(self, transcript: str = "status") -> None:
        self.transcript = transcript

    def transcribe(self, frames: Sequence[AudioFrame]) -> Transcription:
        return Transcription(text=self.transcript, confidence=1.0, backend="mock")
