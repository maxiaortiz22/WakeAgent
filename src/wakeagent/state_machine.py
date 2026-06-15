from __future__ import annotations

from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from enum import Enum

from wakeagent.agent.executor import AgentExecutor, AgentResult
from wakeagent.audio.capture import AudioCapture
from wakeagent.audio.frames import AudioFrame
from wakeagent.config import AppConfig
from wakeagent.router.intent import RouteKind, RouteResult
from wakeagent.router.router import CommandRouter
from wakeagent.stt.base import SpeechToTextBackend, Transcription
from wakeagent.tts.base import Speaker
from wakeagent.utils.logging import log_state
from wakeagent.vad.base import VoiceActivityDetector
from wakeagent.wake.base import WakeWordDetector


class State(str, Enum):
    IDLE = "IDLE"
    WAKE_DETECTED = "WAKE_DETECTED"
    LISTENING = "LISTENING"
    TRANSCRIBING = "TRANSCRIBING"
    ROUTING = "ROUTING"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    EXECUTING = "EXECUTING"
    SPEAKING = "SPEAKING"
    ERROR = "ERROR"


@dataclass(frozen=True)
class PipelineResult:
    states: list[State]
    transcription: Transcription | None
    route: RouteResult | None
    agent_result: AgentResult | None
    final_message: str


class VoiceAssistantStateMachine:
    def __init__(
        self,
        config: AppConfig,
        capture: AudioCapture,
        wake_detector: WakeWordDetector,
        vad: VoiceActivityDetector,
        stt: SpeechToTextBackend,
        router: CommandRouter,
        executor: AgentExecutor,
        speaker: Speaker,
    ) -> None:
        self.config = config
        self.capture = capture
        self.wake_detector = wake_detector
        self.vad = vad
        self.stt = stt
        self.router = router
        self.executor = executor
        self.speaker = speaker
        self.states: list[State] = []

    def run_once(self) -> PipelineResult:
        frame_iter = iter(self.capture.frames())
        try:
            self._transition(State.IDLE, "waiting for wake word")
            self._wait_for_wake(frame_iter)
            self._transition(State.WAKE_DETECTED)
            self._transition(
                State.LISTENING,
                (
                    f"recording command; min={self._frames_to_seconds(self.config.min_recording_frames):.1f}s "
                    f"end_silence={self._frames_to_seconds(self.config.end_silence_frames):.1f}s "
                    f"max={self._frames_to_seconds(self.config.max_recording_frames):.1f}s"
                ),
            )
            command_frames = self._record_command(frame_iter)
            self._transition(State.TRANSCRIBING, f"{len(command_frames)} frames ({self._frames_to_seconds(len(command_frames)):.1f}s)")
            transcription = self.stt.transcribe(command_frames)
            self._transition(State.ROUTING, transcription.text)
            route = self.router.route(transcription.text)
            agent_result = None
            final_message = route.message

            if route.kind is RouteKind.AGENT:
                self._transition(State.WAITING_APPROVAL, "dry-run enabled" if self.config.dry_run else "approved by config")
                self._transition(State.EXECUTING, route.agent_cmd or self.config.agent_cmd)
                agent_result = self.executor.run(
                    route.prompt or transcription.text,
                    agent_cmd=route.agent_cmd or self.config.agent_cmd,
                )
                if agent_result.blocked:
                    final_message = f"Agent command blocked: {agent_result.reason}"
                else:
                    final_message = agent_result.stdout or route.message

            self._transition(State.SPEAKING)
            self.speaker.speak(final_message)
            return PipelineResult(
                states=list(self.states),
                transcription=transcription,
                route=route,
                agent_result=agent_result,
                final_message=final_message,
            )
        except Exception as exc:
            self._transition(State.ERROR, str(exc))
            self.speaker.speak(f"WakeAgent error: {exc}")
            return PipelineResult(
                states=list(self.states),
                transcription=None,
                route=None,
                agent_result=None,
                final_message=f"WakeAgent error: {exc}",
            )

    def _wait_for_wake(self, frame_iter: Iterator[AudioFrame]) -> None:
        for index, frame in enumerate(frame_iter, start=1):
            if self.wake_detector.detect(frame):
                return
            if index >= self.config.wake_timeout_frames:
                raise TimeoutError("Wake word was not detected before timeout.")
        raise RuntimeError("Audio source ended before wake word detection.")

    def _record_command(self, frame_iter: Iterator[AudioFrame]) -> Sequence[AudioFrame]:
        self.vad.reset()
        recorded: list[AudioFrame] = []
        speech_started = False
        trailing_silence = 0

        for frame in frame_iter:
            is_speech = self.vad.is_speech(frame)
            if is_speech:
                speech_started = True
                trailing_silence = 0
                recorded.append(frame)
            elif speech_started:
                trailing_silence += 1
                recorded.append(frame)
                if (
                    trailing_silence >= self.config.end_silence_frames
                    and len(recorded) >= self.config.min_recording_frames
                ):
                    break

            if len(recorded) >= self.config.max_recording_frames:
                break

        if not recorded:
            raise RuntimeError("No command speech was recorded after wake detection.")
        return recorded

    def _transition(self, state: State, detail: str = "") -> None:
        self.states.append(state)
        log_state(state.value, detail)

    def _frames_to_seconds(self, frames: int) -> float:
        return frames * self.config.frame_duration_ms / 1000
