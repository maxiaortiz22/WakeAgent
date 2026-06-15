# 003 VAD Recording

## Purpose

Specify recording after wake detection using voice activity detection and end-of-speech detection.

## Requirements

- Provide a simple energy-based VAD fallback.
- Provide a mock VAD for tests.
- Record command frames until enough trailing silence is observed.
- Use bounded recording limits to avoid infinite listening.
- Keep Silero VAD as a future optional implementation.

## Non-goals

- No diarization.
- No noise suppression.
- No production-grade segmentation.

## Interfaces

- `VoiceActivityDetector.is_speech(frame: AudioFrame) -> bool`
- `VoiceActivityDetector.reset() -> None`
- `EnergyVAD(threshold, min_speech_frames, end_silence_frames)`
- `MockVAD(speech_pattern)`

## Acceptance criteria

- Energy VAD detects high-energy frames as speech.
- Recording stops after configured trailing silence.
- Tests can simulate speech/silence without audio hardware.

## Test cases

- Silent frame returns `False`.
- Loud frame returns `True`.
- Mock pipeline records speech frames and reaches transcription.

## Open questions

- What thresholds are appropriate across laptop microphones?
- Should endpointing be owned by the VAD or the state machine?
