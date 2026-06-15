from __future__ import annotations

from voxshell.audio.frames import AudioFrame


class MockWakeWordDetector:
    def __init__(self, trigger_after_frames: int = 1) -> None:
        self.trigger_after_frames = trigger_after_frames
        self._seen = 0

    def detect(self, frame: AudioFrame) -> bool:
        self._seen += 1
        return self._seen >= self.trigger_after_frames
