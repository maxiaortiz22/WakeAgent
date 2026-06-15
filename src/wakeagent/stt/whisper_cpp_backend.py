from __future__ import annotations

from pathlib import Path
from typing import Sequence

from wakeagent.audio.frames import AudioFrame
from wakeagent.stt.base import Transcription


class WhisperCppBackend:
    """Placeholder for a future whisper.cpp integration.

    A complete implementation would write command audio to a WAV file and call a
    local binary such as:

        whisper-cli -m path/to/model.gguf -f command.wav -l en

    The subprocess wrapper should use shell=False, capture output, enforce a
    timeout, and parse the generated text into a Transcription.
    """

    def __init__(self, whisper_cli_path: str = "whisper-cli", model_path: str | None = None) -> None:
        self.whisper_cli_path = whisper_cli_path
        self.model_path = model_path

    def transcribe(self, frames: Sequence[AudioFrame]) -> Transcription:
        raise NotImplementedError("WhisperCppBackend is a placeholder for a future whisper.cpp integration.")

    def transcribe_wav(self, wav_path: Path) -> Transcription:
        raise NotImplementedError("WhisperCppBackend is a placeholder for a future whisper.cpp integration.")
