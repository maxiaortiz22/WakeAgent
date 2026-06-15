from __future__ import annotations

from collections.abc import Iterable

from wakeagent.audio.frames import AudioFrame


class MockVAD:
    def __init__(self, speech_pattern: Iterable[bool] | None = None) -> None:
        self._pattern = list(speech_pattern or [True, True, True, False, False, False])
        self._index = 0

    def is_speech(self, frame: AudioFrame) -> bool:
        if self._index >= len(self._pattern):
            return False
        value = self._pattern[self._index]
        self._index += 1
        return value

    def reset(self) -> None:
        self._index = 0
