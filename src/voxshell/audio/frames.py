from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True)
class AudioFrame:
    data: NDArray[np.float32]
    sample_rate: int
    timestamp: float

    @property
    def duration_seconds(self) -> float:
        return float(len(self.data) / self.sample_rate)

    @property
    def rms(self) -> float:
        if len(self.data) == 0:
            return 0.0
        return float(np.sqrt(np.mean(np.square(self.data.astype(np.float32)))))
