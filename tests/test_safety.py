from voxshell.agent.executor import AgentExecutor
from voxshell.agent.safety import SafetyPolicy


def test_policy_allows_benign_prompt() -> None:
    decision = SafetyPolicy().check("explain this repo", dry_run=True)

    assert decision.allowed


def test_policy_blocks_rm_rf() -> None:
    decision = SafetyPolicy().check("please run rm -rf /", dry_run=True)

    assert not decision.allowed
    assert "destructive" in decision.reason


def test_policy_blocks_secret_file_access() -> None:
    decision = SafetyPolicy().check("open .env and summarize it", dry_run=True)

    assert not decision.allowed
    assert "secret" in decision.reason


def test_agent_dry_run_returns_command_without_execution() -> None:
    result = AgentExecutor(agent_cmd="codex", dry_run=True).run("explain this repo")

    assert result.command == ["codex", "explain this repo"]
    assert result.dry_run
    assert result.returncode == 0
    assert "DRY RUN" in result.stdout


def test_agent_blocks_destructive_prompt() -> None:
    result = AgentExecutor(agent_cmd="codex", dry_run=True).run("delete with rm -rf /")

    assert result.blocked
    assert result.returncode is None
