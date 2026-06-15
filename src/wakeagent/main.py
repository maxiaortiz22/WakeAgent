from __future__ import annotations

import argparse
from pathlib import Path

from wakeagent.agent.executor import AgentExecutor
from wakeagent.audio.capture import SoundDeviceCapture
from wakeagent.audio.mock_capture import MockAudioCapture
from wakeagent.config import AppConfig
from wakeagent.router.router import CommandRouter
from wakeagent.state_machine import VoiceAssistantStateMachine
from wakeagent.stt.faster_whisper_backend import FasterWhisperBackend
from wakeagent.stt.mock_stt import MockSTTBackend
from wakeagent.tts.console_tts import ConsoleSpeaker
from wakeagent.vad.energy_vad import EnergyVAD
from wakeagent.wake.mock_wake import MockWakeWordDetector
from wakeagent.wake.openwakeword_detector import OpenWakeWordDetector


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="WakeAgent voice assistant MVP")
    parser.add_argument("--mode", choices=["mock", "live"], default="mock")
    parser.add_argument("--wake-backend", choices=["mock", "openwakeword"], default="mock")
    parser.add_argument("--wake-threshold", type=float, default=0.5)
    parser.add_argument("--wake-model-path", default=None)
    parser.add_argument("--wakeword-name", default=None)
    parser.add_argument("--wake-inference-framework", choices=["onnx", "tflite"], default="onnx")
    parser.add_argument("--no-wake-auto-download", action="store_false", dest="wake_auto_download")
    parser.set_defaults(wake_auto_download=True)
    parser.add_argument("--wake-timeout-seconds", type=float, default=20.0)
    parser.add_argument("--max-recording-seconds", type=float, default=12.0)
    parser.add_argument("--min-recording-seconds", type=float, default=1.6)
    parser.add_argument("--end-silence-ms", type=float, default=800.0)
    parser.add_argument("--vad-threshold", type=float, default=0.02)
    parser.add_argument("--stt-backend", choices=["mock", "faster-whisper"], default="mock")
    parser.add_argument("--stt-model-size", default="base")
    parser.add_argument("--stt-device", default="cpu")
    parser.add_argument("--stt-compute-type", default="int8")
    parser.add_argument("--stt-language", default=None)
    parser.add_argument("--stt-wav", default=None, help="Transcribe a WAV file directly and exit.")
    parser.add_argument("--agent-cmd", default="codex")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--no-dry-run", action="store_false", dest="dry_run")
    parser.add_argument("--transcript", default="status")
    parser.add_argument("--timeout", type=float, default=30.0)
    return parser


def create_app(config: AppConfig) -> VoiceAssistantStateMachine:
    if config.mode == "mock":
        capture = MockAudioCapture(
            sample_rate=config.sample_rate,
            frame_duration_ms=config.frame_duration_ms,
        )
        wake_detector = MockWakeWordDetector(trigger_after_frames=1)
        stt = MockSTTBackend(transcript=config.transcript)
    else:
        capture = SoundDeviceCapture(
            sample_rate=config.sample_rate,
            frame_duration_ms=config.frame_duration_ms,
        )
        wake_detector = create_wake_detector(config)
        stt = create_stt_backend(config, allow_fallback=True)

    vad = EnergyVAD(threshold=config.vad_threshold, end_silence_frames=config.end_silence_frames)
    executor = AgentExecutor(
        agent_cmd=config.agent_cmd,
        dry_run=config.dry_run,
        timeout_seconds=config.timeout_seconds,
    )
    return VoiceAssistantStateMachine(
        config=config,
        capture=capture,
        wake_detector=wake_detector,
        vad=vad,
        stt=stt,
        router=CommandRouter(),
        executor=executor,
        speaker=ConsoleSpeaker(),
    )


def create_wake_detector(config: AppConfig) -> MockWakeWordDetector | OpenWakeWordDetector:
    if config.wake_backend == "mock":
        return MockWakeWordDetector(trigger_after_frames=1)

    wakeword_name = config.wakeword_name or "alexa"
    print(
        "[live] Initializing openwakeword wake backend. "
        f"wakeword={wakeword_name} framework={config.wake_inference_framework}"
    )
    try:
        return OpenWakeWordDetector(
            threshold=config.wake_threshold,
            model_path=config.wake_model_path,
            wakeword_name=wakeword_name,
            inference_framework=config.wake_inference_framework,
            auto_download=config.wake_auto_download,
        )
    except RuntimeError as exc:
        print(f"[live] {exc}")
        print("[live] Falling back to mock wake detector so the process can still start.")
        return MockWakeWordDetector(trigger_after_frames=1)


def create_stt_backend(config: AppConfig, allow_fallback: bool = True) -> MockSTTBackend | FasterWhisperBackend:
    if config.stt_backend == "mock":
        return MockSTTBackend(transcript=config.transcript)

    language = config.stt_language or "auto"
    print(f"[live] Initializing faster-whisper STT backend. language={language}")
    try:
        return FasterWhisperBackend(
            model_size=config.stt_model_size,
            device=config.stt_device,
            compute_type=config.stt_compute_type,
            language=config.stt_language,
        )
    except RuntimeError as exc:
        if not allow_fallback:
            raise
        print(f"[live] {exc}")
        print("[live] Falling back to mock STT backend so the process can still start.")
        return MockSTTBackend(transcript=config.transcript)


def transcribe_wav_once(config: AppConfig, wav_path: Path) -> int:
    if not wav_path.exists():
        print(f"[stt] WAV file does not exist: {wav_path}")
        return 1

    try:
        stt = create_stt_backend(config, allow_fallback=False)
        transcription = stt.transcribe_wav(wav_path)
    except RuntimeError as exc:
        print(f"[stt] {exc}")
        return 1

    language = transcription.language or config.stt_language or "auto"
    print(f"[stt] backend={transcription.backend} language={language} confidence={transcription.confidence:.3f}")
    print(f"[transcript] {transcription.text}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = AppConfig(
        mode=args.mode,
        wake_timeout_frames=_frames_from_seconds(args.wake_timeout_seconds, frame_duration_ms=AppConfig().frame_duration_ms),
        wake_backend=args.wake_backend,
        wake_threshold=args.wake_threshold,
        wake_model_path=args.wake_model_path,
        wakeword_name=args.wakeword_name,
        wake_inference_framework=args.wake_inference_framework,
        wake_auto_download=args.wake_auto_download,
        max_recording_frames=_frames_from_seconds(args.max_recording_seconds, frame_duration_ms=AppConfig().frame_duration_ms),
        min_recording_frames=_frames_from_seconds(args.min_recording_seconds, frame_duration_ms=AppConfig().frame_duration_ms),
        end_silence_frames=_frames_from_ms(args.end_silence_ms, frame_duration_ms=AppConfig().frame_duration_ms),
        vad_threshold=args.vad_threshold,
        stt_backend=args.stt_backend,
        stt_model_size=args.stt_model_size,
        stt_device=args.stt_device,
        stt_compute_type=args.stt_compute_type,
        stt_language=args.stt_language,
        transcript=args.transcript,
        agent_cmd=args.agent_cmd,
        dry_run=args.dry_run,
        timeout_seconds=args.timeout,
    )
    if args.stt_wav:
        return transcribe_wav_once(config, Path(args.stt_wav))

    app = create_app(config)
    result = app.run_once()
    print(f"[result] {result.final_message}")
    return 1 if result.transcription is None else 0


def _frames_from_seconds(seconds: float, frame_duration_ms: int) -> int:
    return max(1, round(seconds * 1000 / frame_duration_ms))


def _frames_from_ms(milliseconds: float, frame_duration_ms: int) -> int:
    return max(1, round(milliseconds / frame_duration_ms))


if __name__ == "__main__":
    raise SystemExit(main())
