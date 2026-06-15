from __future__ import annotations


def log_state(state: str, detail: str = "") -> None:
    suffix = f" - {detail}" if detail else ""
    print(f"[state] {state}{suffix}")
