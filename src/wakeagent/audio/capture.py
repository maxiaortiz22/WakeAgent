from __future__ import annotations

import queue
import time
from typing import Iterator, Protocol

import numpy as np

from wakeagent.audio.frames import AudioFrame


class AudioCapture(Protocol):
    def frames(self) -> Iterator[AudioFrame]:
        """Yield audio frames until the source is exhausted or stopped."""


class SoundDeviceCapture:
    def __init__(self, sample_rate: int = 16_000, frame_duration_ms: int = 80) -> None:
        self.sample_rate = sample_rate
        self.frame_duration_ms = frame_duration_ms
        self.frame_size = int(sample_rate * frame_duration_ms / 1000)

    def frames(self) -> Iterator[AudioFrame]:
        try:
            import sounddevice as sd
        except ImportError as exc:
            raise RuntimeError(
                "Live audio requires sounddevice. Install the conda environment or run --mode mock."
            ) from exc

        audio_queue: queue.Queue[np.ndarray] = queue.Queue()

        def callback(indata: np.ndarray, frames: int, time_info: object, status: object) -> None:
            if status:
                print(f"[audio] {status}")
            audio_queue.put(indata[:, 0].astype(np.float32).copy())

        with sd.InputStream(
            channels=1,
            samplerate=self.sample_rate,
            blocksize=self.frame_size,
            dtype="float32",
            callback=callback,
        ):
            while True:
                data = audio_queue.get()
                yield AudioFrame(data=data, sample_rate=self.sample_rate, timestamp=time.time())
