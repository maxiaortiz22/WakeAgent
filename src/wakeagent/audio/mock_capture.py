from __future__ import annotations

from typing import Iterator

import numpy as np

from wakeagent.audio.frames import AudioFrame


class MockAudioCapture:
    def __init__(
        self,
        sample_rate: int = 16_000,
        frame_duration_ms: int = 80,
        prewake_silence_frames: int = 1,
        speech_frames: int = 8,
        trailing_silence_frames: int = 6,
    ) -> None:
        self.sample_rate = sample_rate
        self.frame_duration_ms = frame_duration_ms
        self.frame_size = int(sample_rate * frame_duration_ms / 1000)
        self.prewake_silence_frames = prewake_silence_frames
        self.speech_frames = speech_frames
        self.trailing_silence_frames = trailing_silence_frames

    def frames(self) -> Iterator[AudioFrame]:
        timestamp = 0.0
        step = self.frame_duration_ms / 1000
        total = self.prewake_silence_frames + self.speech_frames + self.trailing_silence_frames
        for index in range(total):
            if self.prewake_silence_frames <= index < self.prewake_silence_frames + self.speech_frames:
                data = np.full(self.frame_size, 0.15, dtype=np.float32)
            else:
                data = np.zeros(self.frame_size, dtype=np.float32)
            yield AudioFrame(data=data, sample_rate=self.sample_rate, timestamp=timestamp)
            timestamp += step
