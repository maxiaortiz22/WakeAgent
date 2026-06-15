from __future__ import annotations

from typing import Protocol

from voxshell.audio.frames import AudioFrame


class VoiceActivityDetector(Protocol):
    def is_speech(self, frame: AudioFrame) -> bool:
        """Return True when the frame appears to contain speech."""

    def reset(self) -> None:
        """Reset any detector state before a new command recording."""
