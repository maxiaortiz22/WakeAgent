from voxshell.agent.executor import AgentExecutor
from voxshell.audio.mock_capture import MockAudioCapture
from voxshell.config import AppConfig
from voxshell.router.router import CommandRouter
from voxshell.state_machine import State, VoiceAssistantStateMachine
from voxshell.stt.mock_stt import MockSTTBackend
from voxshell.tts.console_tts import ConsoleSpeaker
from voxshell.vad.energy_vad import EnergyVAD
from voxshell.wake.mock_wake import MockWakeWordDetector


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
