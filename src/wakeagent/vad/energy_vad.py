from __future__ import annotations

from dataclasses import dataclass

from wakeagent.audio.frames import AudioFrame


@dataclass
class EnergyVAD:
    threshold: float = 0.02
    min_speech_frames: int = 1
    end_silence_frames: int = 4

    def __post_init__(self) -> None:
        self._speech_count = 0

    def is_speech(self, frame: AudioFrame) -> bool:
        if frame.rms >= self.threshold:
            self._speech_count += 1
            return self._speech_count >= self.min_speech_frames
        return False

    def reset(self) -> None:
        self._speech_count = 0
