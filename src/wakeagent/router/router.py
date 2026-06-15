from __future__ import annotations

import re

from wakeagent.router.intent import RouteKind, RouteResult


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

        if "estado" in normalized:
            return RouteResult(kind=RouteKind.LOCAL, message="WakeAgent status: mockable pipeline is running.")

        if "help" in normalized or "ayuda" in normalized:
            return RouteResult(
                kind=RouteKind.LOCAL,
                message=(
                    "Try: status, help, ask codex to explain this repo, "
                    "or in Spanish: estado, ayuda, pedile a codex que describa este repo."
                ),
            )

        if "ask codex" in normalized or re.search(r"\bcodex\b", normalized) or self._looks_like_codex(normalized):
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
            rf"^\s*p[eí]d(?:e|i)le\s+a\s+{agent_name}\s+que\s+",
            rf"^\s*preg[uú]ntale\s+a\s+{agent_name}\s+que\s+",
            rf"^\s*decile\s+a\s+{agent_name}\s+que\s+",
            rf"^\s*{agent_name}\s+",
            rf"^.*?\b{agent_name}\b\s+(?:que|to)\s+",
        ]
        for pattern in patterns:
            prompt = re.sub(pattern, "", prompt, flags=re.IGNORECASE)
        prompt = CommandRouter._normalize_common_stt_errors(prompt)
        return prompt.strip() or transcript.strip()

    @staticmethod
    def _normalize_common_stt_errors(prompt: str) -> str:
        replacements = {
            r"\bpeint\b": "paint",
            r"\bveint\b": "paint",
            r"\bbaint\b": "paint",
            r"\bhabr[aá]\s+paint\b": "abra paint",
            r"\bahora\s+paint\b": "abra paint",
            r"\bripple\b": "repo",
            r"^.*?\b(?:colegos|c[oó]digos)\b\s+que\s+": "",
        }
        normalized = prompt
        for pattern, replacement in replacements.items():
            normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
        return normalized

    @staticmethod
    def _looks_like_codex(normalized: str) -> bool:
        return bool(re.search(r"\b(colegos|c[oó]digos|c[oó]dex)\b", normalized))
