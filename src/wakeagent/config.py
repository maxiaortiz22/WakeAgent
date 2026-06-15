from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


Mode = Literal["mock", "live"]
WakeBackend = Literal["mock", "openwakeword"]
WakeInferenceFramework = Literal["onnx", "tflite"]
SttBackend = Literal["mock", "faster-whisper"]


@dataclass(frozen=True)
class AppConfig:
    mode: Mode = "mock"
    sample_rate: int = 16_000
    frame_duration_ms: int = 80
    wake_timeout_frames: int = 250
    wake_backend: WakeBackend = "mock"
    wake_threshold: float = 0.5
    wake_model_path: str | None = None
    wakeword_name: str | None = None
    wake_inference_framework: WakeInferenceFramework = "onnx"
    wake_auto_download: bool = True
    max_recording_frames: int = 150
    min_recording_frames: int = 20
    end_silence_frames: int = 10
    vad_threshold: float = 0.02
    stt_backend: SttBackend = "mock"
    stt_model_size: str = "base"
    stt_device: str = "cpu"
    stt_compute_type: str = "int8"
    stt_language: str | None = None
    transcript: str = "status"
    agent_cmd: str = "codex"
    dry_run: bool = True
    timeout_seconds: float = 30.0

    @property
    def frame_size(self) -> int:
        return int(self.sample_rate * self.frame_duration_ms / 1000)
