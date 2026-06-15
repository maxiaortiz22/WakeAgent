from __future__ import annotations

from typing import Sequence

from voxshell.audio.frames import AudioFrame
from voxshell.stt.base import Transcription


class WhisperBackend:
    def __init__(self, model_name: str = "base") -> None:
        self.model_name = model_name

    def transcribe(self, frames: Sequence[AudioFrame]) -> Transcription:
        raise NotImplementedError(
            "WhisperBackend is a placeholder. Wire faster-whisper or whisper.cpp behind this interface."
        )
