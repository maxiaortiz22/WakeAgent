from __future__ import annotations

from typing import Iterable

import numpy as np

from voxshell.audio.frames import AudioFrame


class OpenWakeWordDetector:
    def __init__(self, model_names: Iterable[str] | None = None, threshold: float = 0.5) -> None:
        try:
            from openwakeword.model import Model
        except ImportError as exc:
            raise RuntimeError(
                "openwakeword is not installed. Install the optional dependency or run --mode mock."
            ) from exc

        self._model = Model(wakeword_models=list(model_names) if model_names else None)
        self.threshold = threshold

    def detect(self, frame: AudioFrame) -> bool:
        int16_audio = np.clip(frame.data, -1.0, 1.0)
        int16_audio = (int16_audio * 32767).astype(np.int16)
        scores = self._model.predict(int16_audio)
        return any(score >= self.threshold for score in scores.values())
