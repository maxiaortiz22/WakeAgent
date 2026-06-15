from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Sequence

import numpy as np
from scipy.io import wavfile

from wakeagent.audio.frames import AudioFrame
from wakeagent.stt.base import Transcription


class FasterWhisperBackend:
    def __init__(
        self,
        model_size: str = "base",
        device: str = "cpu",
        compute_type: str = "int8",
        language: str | None = None,
    ) -> None:
        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            raise RuntimeError(
                "faster-whisper is not installed. Install the optional dependency or use --stt-backend mock."
            ) from exc

        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.language = language
        try:
            self._model = WhisperModel(model_size, device=device, compute_type=compute_type)
        except Exception as exc:
            raise RuntimeError(f"faster-whisper could not load model '{model_size}': {exc}") from exc

    def transcribe(self, frames: Sequence[AudioFrame]) -> Transcription:
        if not frames:
            return Transcription(text="", confidence=0.0, backend="faster-whisper")

        sample_rate = frames[0].sample_rate
        audio = np.concatenate([frame.data.astype(np.float32) for frame in frames])
        int16_audio = np.clip(audio, -1.0, 1.0)
        int16_audio = (int16_audio * 32767).astype(np.int16)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_path = Path(temp_file.name)

        try:
            wavfile.write(temp_path, sample_rate, int16_audio)
            return self.transcribe_wav(temp_path)
        finally:
            temp_path.unlink(missing_ok=True)

    def transcribe_wav(self, wav_path: Path) -> Transcription:
        if not wav_path.exists():
            raise RuntimeError(f"WAV file does not exist: {wav_path}")

        try:
            segments, info = self._model.transcribe(str(wav_path), language=self.language)
            text = " ".join(segment.text.strip() for segment in segments).strip()
        except Exception as exc:
            raise RuntimeError(f"faster-whisper transcription failed: {exc}") from exc

        language_probability = getattr(info, "language_probability", 0.0)
        language = getattr(info, "language", self.language)
        return Transcription(
            text=text,
            confidence=float(language_probability or 0.0),
            backend="faster-whisper",
            language=language,
        )
