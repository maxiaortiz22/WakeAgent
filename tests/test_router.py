from wakeagent.router.intent import RouteKind
from wakeagent.router.router import CommandRouter


def test_router_status() -> None:
    result = CommandRouter().route("what is your status")

    assert result.kind is RouteKind.LOCAL
    assert "status" in result.message.lower()


def test_router_help() -> None:
    result = CommandRouter().route("help me")

    assert result.kind is RouteKind.LOCAL
    assert "ask codex" in result.message.lower()


def test_router_spanish_local_commands() -> None:
    status = CommandRouter().route("estado")
    help_result = CommandRouter().route("ayuda")

    assert status.kind is RouteKind.LOCAL
    assert help_result.kind is RouteKind.LOCAL


def test_router_codex_agent_prompt_cleanup() -> None:
    result = CommandRouter().route("ask codex to explain this repo")

    assert result.kind is RouteKind.AGENT
    assert result.agent_cmd == "codex"
    assert result.prompt == "explain this repo"


def test_router_spanish_codex_prompt_cleanup() -> None:
    result = CommandRouter().route("pedile a codex que abra paint")

    assert result.kind is RouteKind.AGENT
    assert result.agent_cmd == "codex"
    assert result.prompt == "abra paint"


def test_router_cleans_common_stt_errors() -> None:
    result = CommandRouter().route("y la codex que habrá peint.")

    assert result.kind is RouteKind.AGENT
    assert result.prompt == "abra paint."


def test_router_routes_spanish_stt_codex_aliases() -> None:
    result = CommandRouter().route("de ir a colegos que ahora veint.")

    assert result.kind is RouteKind.AGENT
    assert result.agent_cmd == "codex"
    assert result.prompt == "abra paint."


def test_router_claude_agent() -> None:
    result = CommandRouter().route("claude summarize this file")

    assert result.kind is RouteKind.AGENT
    assert result.agent_cmd == "claude"
    assert result.prompt == "summarize this file"


def test_router_unknown() -> None:
    result = CommandRouter().route("make coffee")

    assert result.kind is RouteKind.UNKNOWN
    assert "do not recognize" in result.message.lower()
