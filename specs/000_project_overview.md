# 000 Project Overview

## Purpose

Define the MVP architecture for WakeAgent, a low-resource background voice assistant prototype that can be developed and tested without production voice dependencies.

## Requirements

- Start from a terminal command named `vox`.
- Support `mock` and `live` modes.
- Model the pipeline as explicit state transitions.
- Keep wake word, audio capture, VAD, STT, TTS, routing, and agent execution replaceable through small interfaces.
- Default to safe dry-run behavior for CLI agent execution.
- Print state transitions and final results to the console.

## Non-goals

- No GUI.
- No daemon or system service.
- No real TTS.
- No mandatory Whisper, OpenWakeWord, Silero, Codex, Claude, or API key.
- No training or bundling model files.

## Interfaces

- `AudioCapture.frames() -> Iterator[AudioFrame]`
- `WakeWordDetector.detect(frame: AudioFrame) -> bool`
- `VoiceActivityDetector.is_speech(frame: AudioFrame) -> bool`
- `SpeechToTextBackend.transcribe(frames: Sequence[AudioFrame]) -> Transcription`
- `CommandRouter.route(transcript: str) -> RouteResult`
- `AgentExecutor.run(prompt: str, agent_cmd: str | None = None) -> AgentResult`
- `Speaker.speak(text: str) -> None`

## Acceptance criteria

- `vox --mode mock` completes one full mock interaction.
- `vox --mode mock --transcript "ask codex to explain this repo" --dry-run` returns an agent dry-run result.
- Tests pass without microphone hardware or optional model dependencies.
- Live mode reports missing dependencies clearly instead of crashing with obscure import errors.

## Test cases

- Full mock pipeline moves through wake detection, listening, transcription, routing, and speaking.
- Dry-run agent execution logs what would be executed.
- Unknown commands return a safe fallback.

## Open questions

- Which wake word should be packaged first?
- Should approvals be interactive terminal prompts or external policy files?
- Which STT backend should be promoted from placeholder to default?
