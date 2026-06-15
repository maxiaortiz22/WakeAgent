from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


Mode = Literal["mock", "live"]


@dataclass(frozen=True)
class AppConfig:
    mode: Mode = "mock"
    sample_rate: int = 16_000
    frame_duration_ms: int = 80
    wake_timeout_frames: int = 50
    max_recording_frames: int = 80
    end_silence_frames: int = 4
    transcript: str = "status"
    agent_cmd: str = "codex"
    dry_run: bool = True
    timeout_seconds: float = 30.0

    @property
    def frame_size(self) -> int:
        return int(self.sample_rate * self.frame_duration_ms / 1000)
