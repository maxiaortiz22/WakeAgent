from __future__ import annotations

import argparse

from voxshell.agent.executor import AgentExecutor
from voxshell.audio.capture import SoundDeviceCapture
from voxshell.audio.mock_capture import MockAudioCapture
from voxshell.config import AppConfig, Mode
from voxshell.router.router import CommandRouter
from voxshell.state_machine import VoiceAssistantStateMachine
from voxshell.stt.mock_stt import MockSTTBackend
from voxshell.tts.console_tts import ConsoleSpeaker
from voxshell.vad.energy_vad import EnergyVAD
from voxshell.wake.mock_wake import MockWakeWordDetector
from voxshell.wake.openwakeword_detector import OpenWakeWordDetector


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="WakeAgent voice assistant MVP")
    parser.add_argument("--mode", choices=["mock", "live"], default="mock")
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
        try:
            wake_detector = OpenWakeWordDetector()
        except RuntimeError as exc:
            print(f"[live] {exc}")
            print("[live] Falling back to mock wake detector so the process can still start.")
            wake_detector = MockWakeWordDetector(trigger_after_frames=1)
        stt = MockSTTBackend(transcript=config.transcript)

    vad = EnergyVAD(end_silence_frames=config.end_silence_frames)
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


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = AppConfig(
        mode=args.mode,
        transcript=args.transcript,
        agent_cmd=args.agent_cmd,
        dry_run=args.dry_run,
        timeout_seconds=args.timeout,
    )
    app = create_app(config)
    result = app.run_once()
    print(f"[result] {result.final_message}")
    return 1 if result.transcription is None else 0


if __name__ == "__main__":
    raise SystemExit(main())
