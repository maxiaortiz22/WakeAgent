# 002 Wake Word

## Purpose

Specify wake word detection behavior and the boundary between WakeAgent and wake word libraries.

## Requirements

- Prefer an existing wake word library such as `openwakeword` when it installs cleanly.
- Provide a mock wake detector for tests.
- Keep the detector interface frame-based and replaceable.
- Live mode must continue with a clear error if the real backend cannot initialize.
- Support `wake_backend`, `wake_threshold`, `wake_model_path`, and `wakeword_name` config options.

## Non-goals

- No custom wake word training.
- No bundled model management.
- No multi-wake-word UI.

## Interfaces

- `WakeWordDetector.detect(frame: AudioFrame) -> bool`
- `MockWakeWordDetector(trigger_after_frames: int)`
- `OpenWakeWordDetector(threshold, model_path, wakeword_name)`

## Acceptance criteria

- Mock detector can deterministically trigger after a known number of frames.
- OpenWakeWord adapter imports optional dependencies lazily.
- OpenWakeWord adapter reports missing packages or model-load failures with clear `RuntimeError` messages.
- Tests do not require OpenWakeWord.

## Test cases

- Mock wake detector triggers the mock pipeline.
- Selecting `openwakeword` falls back cleanly when the optional package is unavailable.
- State machine transitions from `IDLE` to `WAKE_DETECTED`.

## Open questions

- Which default wake phrase should the MVP use?
- Should wake scores be exposed in logs?
