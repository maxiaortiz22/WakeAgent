from voxshell.router.intent import RouteKind
from voxshell.router.router import CommandRouter


def test_router_status() -> None:
    result = CommandRouter().route("what is your status")

    assert result.kind is RouteKind.LOCAL
    assert "status" in result.message.lower()


def test_router_help() -> None:
    result = CommandRouter().route("help me")

    assert result.kind is RouteKind.LOCAL
    assert "ask codex" in result.message.lower()


def test_router_codex_agent_prompt_cleanup() -> None:
    result = CommandRouter().route("ask codex to explain this repo")

    assert result.kind is RouteKind.AGENT
    assert result.agent_cmd == "codex"
    assert result.prompt == "explain this repo"


def test_router_claude_agent() -> None:
    result = CommandRouter().route("claude summarize this file")

    assert result.kind is RouteKind.AGENT
    assert result.agent_cmd == "claude"
    assert result.prompt == "summarize this file"


def test_router_unknown() -> None:
    result = CommandRouter().route("make coffee")

    assert result.kind is RouteKind.UNKNOWN
    assert "do not recognize" in result.message.lower()
