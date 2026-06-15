from wakeagent.agent.executor import AgentExecutor
from wakeagent.audio.mock_capture import MockAudioCapture
from wakeagent.config import AppConfig
from wakeagent.router.router import CommandRouter
from wakeagent.state_machine import State, VoiceAssistantStateMachine
from wakeagent.stt.mock_stt import MockSTTBackend
from wakeagent.stt.base import Transcription
from wakeagent.tts.console_tts import ConsoleSpeaker
from wakeagent.vad.energy_vad import EnergyVAD
from wakeagent.wake.mock_wake import MockWakeWordDetector


def build_mock_app(transcript: str = "status") -> VoiceAssistantStateMachine:
    config = AppConfig(mode="mock", transcript=transcript, end_silence_frames=2)
    return VoiceAssistantStateMachine(
        config=config,
        capture=MockAudioCapture(trailing_silence_frames=4),
        wake_detector=MockWakeWordDetector(trigger_after_frames=1),
        vad=EnergyVAD(end_silence_frames=2),
        stt=MockSTTBackend(transcript=transcript),
        router=CommandRouter(),
        executor=AgentExecutor(dry_run=True),
        speaker=ConsoleSpeaker(),
    )


def test_mock_state_transitions_for_local_command() -> None:
    result = build_mock_app("status").run_once()

    assert result.states == [
        State.IDLE,
        State.WAKE_DETECTED,
        State.LISTENING,
        State.TRANSCRIBING,
        State.ROUTING,
        State.SPEAKING,
    ]
    assert "status" in result.final_message.lower()


def test_mock_state_transitions_for_agent_command() -> None:
    result = build_mock_app("ask codex to explain this repo").run_once()

    assert State.WAITING_APPROVAL in result.states
    assert State.EXECUTING in result.states
    assert result.agent_result is not None
    assert result.agent_result.dry_run


def test_recording_respects_minimum_duration_before_endpoint() -> None:
    class CapturingSTT:
        def __init__(self) -> None:
            self.frame_count = 0

        def transcribe(self, frames) -> Transcription:
            self.frame_count = len(frames)
            return Transcription(text="status", confidence=1.0, backend="capturing")

    stt = CapturingSTT()
    config = AppConfig(
        mode="mock",
        transcript="status",
        end_silence_frames=2,
        min_recording_frames=5,
        max_recording_frames=20,
    )
    app = VoiceAssistantStateMachine(
        config=config,
        capture=MockAudioCapture(speech_frames=1, trailing_silence_frames=10),
        wake_detector=MockWakeWordDetector(trigger_after_frames=1),
        vad=EnergyVAD(end_silence_frames=2),
        stt=stt,
        router=CommandRouter(),
        executor=AgentExecutor(dry_run=True),
        speaker=ConsoleSpeaker(),
    )

    result = app.run_once()

    assert result.transcription is not None
    assert stt.frame_count == 5
    assert State.TRANSCRIBING in result.states
