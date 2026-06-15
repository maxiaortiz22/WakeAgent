from wakeagent.main import create_app
from wakeagent.config import AppConfig
from wakeagent.state_machine import State


def test_full_mock_pipeline_from_wake_to_agent_dry_run() -> None:
    app = create_app(AppConfig(mode="mock", transcript="ask codex to explain this repo", dry_run=True))

    result = app.run_once()

    assert result.transcription is not None
    assert result.transcription.text == "ask codex to explain this repo"
    assert result.agent_result is not None
    assert result.agent_result.command == ["codex", "explain this repo"]
    assert "DRY RUN" in result.final_message
    assert result.states[-1] is State.SPEAKING
