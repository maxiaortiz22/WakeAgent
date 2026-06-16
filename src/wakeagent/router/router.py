from __future__ import annotations

import re
import unicodedata

from wakeagent.router.intent import RouteKind, RouteResult


class CommandRouter:
    def __init__(self, target_agent: str = "auto") -> None:
        if target_agent not in {"auto", "codex", "claude"}:
            raise ValueError("target_agent must be one of: auto, codex, claude")
        self.target_agent = target_agent

    def route(self, transcript: str) -> RouteResult:
        normalized = " ".join(transcript.lower().split())
        folded = self._fold(normalized)

        if not normalized:
            return RouteResult(
                kind=RouteKind.UNKNOWN,
                message="I did not hear a command clearly enough to route it yet.",
            )

        if "status" in folded:
            return RouteResult(kind=RouteKind.LOCAL, message="WakeAgent status: mockable pipeline is running.")

        if "estado" in folded:
            return RouteResult(kind=RouteKind.LOCAL, message="WakeAgent status: mockable pipeline is running.")

        if "help" in folded or "ayuda" in folded:
            return RouteResult(
                kind=RouteKind.LOCAL,
                message=(
                    "Try: status, help, ask codex to explain this repo, "
                    "or in Spanish: estado, ayuda, pedile a codex que describa este repo."
                ),
            )

        if self.target_agent != "auto":
            return self._agent_route(transcript, self.target_agent)

        if "ask codex" in folded or re.search(r"\bcodex\b", folded) or self._looks_like_codex(folded):
            return self._agent_route(transcript, "codex")

        if "ask claude" in folded or re.search(r"\bclaude\b", folded) or self._looks_like_claude(folded):
            return self._agent_route(transcript, "claude")

        return RouteResult(
            kind=RouteKind.UNKNOWN,
            message="I do not recognize that command yet. Say status, help, ask codex, or ask claude.",
        )

    def _agent_route(self, transcript: str, agent_name: str) -> RouteResult:
        return RouteResult(
            kind=RouteKind.AGENT,
            message=f"Routing command to {agent_name}.",
            agent_cmd=agent_name,
            prompt=self._clean_agent_prompt(transcript, agent_name),
        )

    @staticmethod
    def _clean_agent_prompt(transcript: str, agent_name: str) -> str:
        prompt = transcript.strip()
        agent_aliases = {
            "codex": r"(?:codex|codigos|codigo|colegos)",
            "claude": r"(?:claude|claud|clod|cloud)",
        }
        agent_pattern = agent_aliases.get(agent_name, re.escape(agent_name))
        patterns = [
            rf"^\s*ask\s+{agent_pattern}\s+to\s+",
            rf"^\s*ask\s+{agent_pattern}\s+",
            rf"^\s*ask\s+to\s+",
            rf"^\s*p(?:e|i)d(?:e|i)le\s+a\s+{agent_pattern}\s+que\s+",
            rf"^\s*p(?:e|i)d(?:e|i)le\s+que\s+",
            rf"^\s*pide\s+a\s+{agent_pattern}\s+que\s+",
            rf"^\s*pide\s+que\s+",
            rf"^\s*preguntale\s+a\s+{agent_pattern}\s+que\s+",
            rf"^\s*preguntale\s+que\s+",
            rf"^\s*decile\s+a\s+{agent_pattern}\s+que\s+",
            rf"^\s*decile\s+que\s+",
            rf"^\s*y\s+la\s+{agent_pattern}\s+que\s+",
            rf"^\s*{agent_pattern}\s+",
            rf"^.*?\b{agent_pattern}\b\s+(?:que|to)\s+",
        ]
        for pattern in patterns:
            prompt = CommandRouter._sub_folded(pattern, "", prompt)
        prompt = CommandRouter._normalize_common_stt_errors(prompt)
        return prompt.strip() or transcript.strip()

    @staticmethod
    def _normalize_common_stt_errors(prompt: str) -> str:
        replacements = {
            r"\bpeint\b": "paint",
            r"\bveint\b": "paint",
            r"\bbaint\b": "paint",
            r"\bhabra\s+": "abra ",
            r"\bahora\s+paint\b": "abra paint",
            r"\bripple\b": "repo",
            r"\brobocitoria\b": "repositorio",
            r"^.*?\b(?:colegos|codigos)\b\s+que\s+": "",
        }
        normalized = prompt
        for pattern, replacement in replacements.items():
            normalized = CommandRouter._sub_folded(pattern, replacement, normalized)
        return normalized

    @staticmethod
    def _looks_like_codex(folded: str) -> bool:
        return bool(re.search(r"\b(colegos|codigos|codigo|codex)\b", folded))

    @staticmethod
    def _looks_like_claude(folded: str) -> bool:
        return bool(re.search(r"\b(claud|clod|cloud|claude)\b", folded))

    @staticmethod
    def _fold(value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value)
        ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
        return ascii_only.lower()

    @staticmethod
    def _sub_folded(pattern: str, replacement: str, value: str) -> str:
        folded = CommandRouter._fold(value)
        match = re.search(pattern, folded, flags=re.IGNORECASE)
        if not match:
            return value
        return value[: match.start()] + replacement + value[match.end() :]
