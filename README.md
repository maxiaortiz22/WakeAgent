# WakeAgent

WakeAgent is an MVP for a low-resource, terminal-first voice assistant. It listens for a wake word, records a command, transcribes it, routes the command, and can optionally hand the prompt to a local CLI agent such as `codex` or `claude`.

The project is built with Specification Driven Development (SDD): every feature starts with a spec, acceptance criteria, test expectations, and mockable interfaces. The first usable path is intentionally mock-first so the project can be tested without a microphone, wake word model, speech-to-text model, API key, or CLI agent installed.

## Setup

```powershell
conda env create -f environment.yml
conda activate wakeagent
pip install -e .
```

## Run Tests

```powershell
pytest
```

## Run Mock Mode

```powershell
vox --mode mock
vox --mode mock --transcript "ask codex to explain this repo" --dry-run
vox --mode mock --agent-cmd codex
```

Mock mode simulates the full wake-word-to-result pipeline and is the supported MVP path.

## Run Live Mode

```powershell
vox --mode live --dry-run
```

Live mode attempts to use optional microphone and backend integrations. If a dependency such as `sounddevice` or `openwakeword` is missing, WakeAgent fails gracefully with a clear console message. The live path is intentionally conservative in this MVP.

## Known Limitations

- Wake word detection uses a mock detector by default; the `openwakeword` adapter is a best-effort placeholder.
- STT uses `MockSTTBackend` unless a future backend is wired in.
- VAD supports a simple energy-based implementation, not a production speech segmentation model.
- TTS is console-only.
- Agent execution defaults to dry-run and should remain that way while developing.
- This is not a daemon, service, GUI, or secure sandbox.

## Next Steps

- Complete and test a real `openwakeword` detector path.
- Add a real STT backend using `whisper.cpp` or `faster-whisper`.
- Add Silero VAD behind the existing VAD interface.
- Add approval prompts for non-dry-run execution.
- Add structured logging and persistent run traces.
- Add platform-specific microphone setup documentation.
