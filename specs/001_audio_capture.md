# 001 Audio Capture

## Purpose

Specify how WakeAgent obtains low-overhead audio frames from either a real microphone or a deterministic mock source.

## Requirements

- Use 16 kHz mono frames for voice processing.
- Prefer `sounddevice` for live capture when available.
- Provide a mock capture source for deterministic tests.
- Represent frames with sample rate, timestamp, and NumPy audio data.
- Fail gracefully when live capture dependencies are unavailable.

## Non-goals

- No device selection UI.
- No advanced resampling pipeline.
- No multi-channel processing.
- No persistent audio recording files.

## Interfaces

- `AudioFrame(data, sample_rate, timestamp)`
- `AudioCapture.frames()`
- `SoundDeviceCapture(sample_rate, frame_duration_ms)`
- `MockAudioCapture(sample_rate, frame_duration_ms, pattern)`

## Acceptance criteria

- Mock capture produces finite deterministic frames.
- Live capture imports `sounddevice` lazily.
- Missing `sounddevice` raises a clear runtime error.
- Frame energy can be computed consistently by downstream components.

## Test cases

- Mock frames can drive the state machine.
- Energy VAD can distinguish silent and voiced mock frames.

## Open questions

- What frame duration gives the best CPU/latency tradeoff on target hardware?
- Should captured command audio be persisted for debugging?
