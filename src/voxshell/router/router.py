from __future__ import annotations

import re

from voxshell.router.intent import RouteKind, RouteResult


class CommandRouter:
    def route(self, transcript: str) -> RouteResult:
        normalized = " ".join(transcript.lower().split())

        if not normalized:
            return RouteResult(
                kind=RouteKind.UNKNOWN,
                message="I did not hear a command clearly enough to route it yet.",
            )

        if "status" in normalized:
            return RouteResult(kind=RouteKind.LOCAL, message="WakeAgent status: mockable pipeline is running.")

        if "help" in normalized:
            return RouteResult(
                kind=RouteKind.LOCAL,
                message="Try: status, help, ask codex to explain this repo, or ask claude to summarize a file.",
            )

        if "ask codex" in normalized or re.search(r"\bcodex\b", normalized):
            return RouteResult(
                kind=RouteKind.AGENT,
                message="Routing command to codex.",
                agent_cmd="codex",
                prompt=self._clean_agent_prompt(transcript, "codex"),
            )

        if "ask claude" in normalized or re.search(r"\bclaude\b", normalized):
            return RouteResult(
                kind=RouteKind.AGENT,
                message="Routing command to claude.",
                agent_cmd="claude",
                prompt=self._clean_agent_prompt(transcript, "claude"),
            )

        return RouteResult(
            kind=RouteKind.UNKNOWN,
            message="I do not recognize that command yet. Say status, help, ask codex, or ask claude.",
        )

    @staticmethod
    def _clean_agent_prompt(transcript: str, agent_name: str) -> str:
        prompt = transcript.strip()
        patterns = [
            rf"^\s*ask\s+{agent_name}\s+to\s+",
            rf"^\s*ask\s+{agent_name}\s+",
            rf"^\s*{agent_name}\s+",
        ]
        for pattern in patterns:
            prompt = re.sub(pattern, "", prompt, flags=re.IGNORECASE)
        return prompt.strip() or transcript.strip()
