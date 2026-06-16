# WakeAgent

WakeAgent is an MVP for a low-resource, terminal-first voice assistant. It listens for a wake word, records a command, transcribes it, routes the command, and can optionally hand the prompt to a local CLI agent such as `codex` or `claude`.

The project is built with Specification Driven Development (SDD): every feature starts with a spec, acceptance criteria, test expectations, and mockable interfaces. The first usable path is intentionally mock-first so the project can be tested without a microphone, wake word model, speech-to-text model, API key, or CLI agent installed.

## Setup

```powershell
conda env create -f environment.yml
conda activate wakeagent
pip install -e .
```

`environment.yml` installs the live audio/STT/wake dependencies too: `sounddevice`, `openwakeword`, `faster-whisper`, and `silero-vad`.

If you are installing with pip instead of conda, use the live extra:

```powershell
pip install -e ".[live]"
```

For development plus all optional live backends:

```powershell
pip install -e ".[all]"
```

To update an existing conda environment after dependency changes:

```powershell
conda activate wakeagent
conda env update -f environment.yml --prune
pip install -e .
```

## Run Tests

```powershell
pytest
```

## Useful Commands

```powershell
wakeagent --mode mock
wakeagent --mode mock --transcript "ask codex to explain this repo" --dry-run
wakeagent --stt-backend faster-whisper --stt-model-size tiny --stt-language es --stt-wav tests\audio\test_1.wav
wakeagent --mode live --wake-backend openwakeword --stt-backend faster-whisper --stt-model-size tiny
wakeagent --mode live --wake-backend openwakeword --wakeword-name alexa --wake-inference-framework onnx --stt-backend faster-whisper --stt-model-size tiny --stt-language es
wakeagent --mode live --wake-backend openwakeword --wakeword-name alexa --wake-inference-framework onnx --stt-backend faster-whisper --stt-model-size base --stt-language es --wake-timeout-seconds 30 --min-recording-seconds 2.5 --end-silence-ms 1200 --max-recording-seconds 12
wakeagent --download-stt-model --stt-model-size medium --stt-language es --stt-model-dir .\.models\faster-whisper
wakeagent --download-stt-model --stt-model-size medium --stt-language en --stt-model-dir .\.models\faster-whisper
wakeagent --mode live --target-agent codex --wake-backend openwakeword --wakeword-name alexa --wake-inference-framework onnx --stt-backend faster-whisper --stt-model-size medium --stt-model-dir .\.models\faster-whisper --stt-local-files-only --stt-language es --wake-timeout-seconds 30 --min-recording-seconds 2.5 --end-silence-ms 1200 --max-recording-seconds 12
```

## Run Mock Mode First

```powershell
wakeagent --mode mock
wakeagent --mode mock --transcript "ask codex to explain this repo" --dry-run
wakeagent --mode mock --agent-cmd codex
```

Mock mode simulates the full wake-word-to-result pipeline and is the safest first run. It does not require a microphone, OpenWakeWord, Whisper, Codex, Claude, or an API key.

## Test STT Directly

Use a short 16 kHz mono WAV file if you have one:

```powershell
wakeagent --stt-backend faster-whisper --stt-model-size tiny --stt-wav .\samples\command.wav
wakeagent --stt-backend faster-whisper --stt-model-size tiny --stt-language es --stt-wav tests\audio\test_1.wav
```

The first run may download or initialize the selected local model. Use `tiny` first because it is the fastest sanity check on CPU. Add `--stt-language es` for Spanish audio or `--stt-language en` for English audio. If `faster-whisper` is not installed or the model cannot load, WakeAgent prints a clear `[stt]` error and exits without starting the microphone pipeline.

### Preload STT Models

You can download/load a faster-whisper model before live testing:

```powershell
wakeagent --download-stt-model --stt-model-size medium --stt-language es
```

To keep the model files inside the repo workspace instead of the default Hugging Face cache:

```powershell
wakeagent --download-stt-model --stt-model-size medium --stt-language es --stt-model-dir .\.models\faster-whisper
```

Then use the same model directory in live mode. Add `--stt-local-files-only` when you want WakeAgent to fail fast if the model is not already available locally:

```powershell
wakeagent --mode live --wake-backend openwakeword --wakeword-name alexa --wake-inference-framework onnx --stt-backend faster-whisper --stt-model-size medium --stt-model-dir .\.models\faster-whisper --stt-local-files-only --stt-language es
```

Notes:

- `--download-stt-model` forces `faster-whisper`, initializes the selected model, prints where it is ready, and exits before microphone capture.
- `--stt-model-dir` is passed to faster-whisper as its download/cache root for this run.
- `--stt-local-files-only` prevents network-backed model resolution. It is useful after preloading, but it will fail if the selected model is not already in the configured cache.
- Hugging Face warnings can still be printed while the library checks cache metadata; they do not necessarily mean the model is being downloaded again.

For live English commands such as `ask codex to describe this repo`, pass the language explicitly:

```powershell
wakeagent --mode live --wake-backend openwakeword --stt-backend faster-whisper --stt-model-size tiny --stt-language en
```

Without `--stt-language`, faster-whisper uses automatic language detection. Short recordings, background noise, or clipped speech can be misdetected as another language.

For a Spanish live test with the built-in OpenWakeWord `alexa` wake word, say "Alexa" first, then speak the command in Spanish:

```powershell
wakeagent --mode live --wake-backend openwakeword --wakeword-name alexa --stt-backend faster-whisper --stt-model-size tiny --stt-language es
```

If `--wake-backend openwakeword` is used without `--wakeword-name`, WakeAgent defaults to `alexa`. WakeAgent also defaults OpenWakeWord to ONNX inference on Windows-friendly installs:

```powershell
wakeagent --mode live --wake-backend openwakeword --wakeword-name alexa --wake-inference-framework onnx --stt-backend faster-whisper --stt-model-size tiny --stt-language es
```

Useful Spanish commands for the current router:

- `estado`
- `ayuda`
- `pedile a codex que describa este repo`
- `pedile a codex que abra paint`

### Fixed Agent Selection

By default, WakeAgent uses `--target-agent auto`, so the router tries to infer `codex` or `claude` from the transcript. This is fragile with short Spanish commands because STT can hear names as `codigos`, `cloud`, or similar.

Use `--target-agent codex` or `--target-agent claude` to choose the CLI agent outside the voice command. Local commands still work, but every other transcript goes to the selected agent:

```powershell
wakeagent --mode live --target-agent codex --wake-backend openwakeword --wakeword-name alexa --wake-inference-framework onnx --stt-backend faster-whisper --stt-model-size medium --stt-language es --wake-timeout-seconds 30 --min-recording-seconds 2.5 --end-silence-ms 1200 --max-recording-seconds 12
```

With that command you can say:

- `Alexa, abrí cursor`
- `Alexa, explicame este repositorio`
- `Alexa, estado`

For Claude:

```powershell
wakeagent --mode live --target-agent claude --wake-backend openwakeword --wakeword-name alexa --wake-inference-framework onnx --stt-backend faster-whisper --stt-model-size medium --stt-language es --wake-timeout-seconds 30 --min-recording-seconds 2.5 --end-silence-ms 1200 --max-recording-seconds 12
```

For live microphone testing, this more patient configuration is usually better than the fastest defaults:

```powershell
wakeagent --mode live --wake-backend openwakeword --wakeword-name alexa --wake-inference-framework onnx --stt-backend faster-whisper --stt-model-size base --stt-language es --wake-timeout-seconds 30 --min-recording-seconds 2.5 --end-silence-ms 1200 --max-recording-seconds 12
```

Tuning notes:

- `--wake-timeout-seconds`: how long to wait for "Alexa" before giving up.
- `--min-recording-seconds`: minimum command audio captured after wake detection.
- `--end-silence-ms`: trailing silence required before stopping.
- `--max-recording-seconds`: hard cap so listening cannot run forever.
- `--vad-threshold`: lower values are more sensitive; try `0.01` if speech is missed, `0.03` if background noise keeps recording.
- `--target-agent`: `auto` detects the agent from speech; `codex` or `claude` routes non-local commands directly to that agent.
- `--stt-model-size`: larger models are usually more accurate but take longer to load and transcribe.
- `--stt-model-dir`: optional faster-whisper model cache/download directory.
- `--stt-local-files-only`: use only already-downloaded model files.
- `--stt-beam-size`: decoding search width; `5` is the default balance.
- `--stt-initial-prompt` and `--stt-hotwords`: optional hints for domain words such as `Codex`, `Claude`, and `Cursor`.

Recommended audio format for predictable local testing:

- WAV
- Mono
- 16 kHz sample rate
- 16-bit PCM

## Run Live Mode

```powershell
wakeagent --mode live --dry-run
wakeagent --mode live --wake-backend openwakeword --stt-backend faster-whisper
wakeagent --mode live --wake-backend openwakeword --stt-backend faster-whisper --stt-model-size tiny
```

Live mode attempts to use the microphone and optional backend integrations. If a dependency such as `sounddevice`, `openwakeword`, or `faster-whisper` is missing, WakeAgent prints a clear console message and falls back to mock components where possible so the process does not fail with an obscure import error.

On Windows, `sounddevice` may not resolve as a conda package in every channel setup, so `environment.yml` installs it through `pip` inside the conda environment.

## Known Limitations

- Wake word detection uses a mock detector by default; `--wake-backend openwakeword` enables the optional OpenWakeWord backend.
- STT uses `MockSTTBackend` by default; `--stt-backend faster-whisper` enables the optional faster-whisper backend.
- VAD supports a simple energy-based implementation, not a production speech segmentation model.
- TTS is console-only.
- Agent execution defaults to dry-run and should remain that way while developing.
- This is not a daemon, service, GUI, or secure sandbox.
- Live mode currently handles one interaction per process, so larger STT models are loaded again each time you restart `wakeagent`.

## Next Steps

- Add a broader live-audio integration test harness with recorded fixtures.
- Add continuous live mode so wake/STT models stay loaded across multiple commands.
- Add a real `whisper.cpp` backend around a local `whisper-cli` binary.
- Add Silero VAD behind the existing VAD interface.
- Add approval prompts for non-dry-run execution.
- Add structured logging and persistent run traces.
- Add platform-specific microphone setup documentation.
