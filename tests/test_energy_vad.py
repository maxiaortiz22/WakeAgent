import numpy as np

from voxshell.audio.frames import AudioFrame
from voxshell.vad.energy_vad import EnergyVAD


def test_energy_vad_detects_silence() -> None:
    frame = AudioFrame(data=np.zeros(160, dtype=np.float32), sample_rate=16_000, timestamp=0.0)

    assert not EnergyVAD(threshold=0.01).is_speech(frame)


def test_energy_vad_detects_voice_energy() -> None:
    frame = AudioFrame(data=np.full(160, 0.2, dtype=np.float32), sample_rate=16_000, timestamp=0.0)

    assert EnergyVAD(threshold=0.01).is_speech(frame)


def test_energy_vad_respects_min_speech_frames() -> None:
    vad = EnergyVAD(threshold=0.01, min_speech_frames=2)
    frame = AudioFrame(data=np.full(160, 0.2, dtype=np.float32), sample_rate=16_000, timestamp=0.0)

    assert not vad.is_speech(frame)
    assert vad.is_speech(frame)
