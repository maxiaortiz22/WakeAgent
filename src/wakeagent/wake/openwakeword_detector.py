from __future__ import annotations

from pathlib import Path

import numpy as np

from wakeagent.audio.frames import AudioFrame


class OpenWakeWordDetector:
    def __init__(
        self,
        threshold: float = 0.5,
        model_path: str | None = None,
        wakeword_name: str | None = None,
        inference_framework: str = "onnx",
        auto_download: bool = True,
    ) -> None:
        try:
            from openwakeword.model import Model
            from openwakeword.utils import download_models
        except ImportError as exc:
            raise RuntimeError(
                "openwakeword is not installed. Install the optional dependency or run --mode mock."
            ) from exc

        wakeword_models = self._resolve_models(model_path=model_path, wakeword_name=wakeword_name)
        try:
            if wakeword_models is None:
                self._model = Model(inference_framework=inference_framework)
            else:
                self._model = Model(wakeword_models=wakeword_models, inference_framework=inference_framework)
        except Exception as exc:
            if auto_download and wakeword_name and model_path is None and self._looks_like_missing_model(exc):
                try:
                    print(f"[live] Downloading openwakeword model assets for '{wakeword_name}'.")
                    download_models([wakeword_name])
                    self._model = Model(wakeword_models=wakeword_models, inference_framework=inference_framework)
                except Exception as download_exc:
                    raise RuntimeError(
                        "openwakeword model assets are missing and automatic download failed: "
                        f"{download_exc}"
                    ) from download_exc
            else:
                raise RuntimeError(f"openwakeword could not load the requested model: {exc}") from exc

        self.threshold = threshold
        self.model_path = model_path
        self.wakeword_name = wakeword_name
        self.inference_framework = inference_framework
        self.auto_download = auto_download

    def detect(self, frame: AudioFrame) -> bool:
        int16_audio = np.clip(frame.data, -1.0, 1.0)
        int16_audio = (int16_audio * 32767).astype(np.int16)
        try:
            scores = self._model.predict(int16_audio)
        except Exception as exc:
            raise RuntimeError(f"openwakeword prediction failed: {exc}") from exc
        return any(score >= self.threshold for score in scores.values())

    @staticmethod
    def _resolve_models(model_path: str | None, wakeword_name: str | None) -> list[str] | None:
        if model_path:
            path = Path(model_path)
            if not path.exists():
                raise RuntimeError(f"openwakeword model path does not exist: {model_path}")
            return [str(path)]
        if wakeword_name:
            return [wakeword_name]
        return None

    @staticmethod
    def _looks_like_missing_model(exc: Exception) -> bool:
        message = str(exc).lower()
        return "no_suchfile" in message or "file doesn't exist" in message or "could not find pretrained model" in message
