import builtins
import sys
import types

import pytest

from wakeagent.config import AppConfig
from wakeagent.main import create_app, create_stt_backend, create_wake_detector, download_stt_model, main
from wakeagent.stt.faster_whisper_backend import FasterWhisperBackend
from wakeagent.stt.mock_stt import MockSTTBackend
from wakeagent.wake.mock_wake import MockWakeWordDetector
from wakeagent.wake.openwakeword_detector import OpenWakeWordDetector


def test_mock_mode_ignores_real_backend_config() -> None:
    app = create_app(
        AppConfig(
            mode="mock",
            wake_backend="openwakeword",
            stt_backend="faster-whisper",
            transcript="status",
        )
    )

    result = app.run_once()

    assert result.transcription is not None
    assert result.transcription.backend == "mock"
    assert "status" in result.final_message.lower()


def test_create_app_uses_fixed_target_agent_in_mock_mode() -> None:
    app = create_app(
        AppConfig(
            mode="mock",
            transcript="abra cursor",
            target_agent="claude",
        )
    )

    result = app.run_once()

    assert result.route is not None
    assert result.route.agent_cmd == "claude"
    assert result.agent_result is not None
    assert result.agent_result.command == ["claude", "abra cursor"]


def test_openwakeword_missing_dependency_error_is_clear(monkeypatch: pytest.MonkeyPatch) -> None:
    real_import = builtins.__import__

    def blocked_import(name: str, *args: object, **kwargs: object) -> object:
        if name.startswith("openwakeword"):
            raise ImportError("blocked for test")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", blocked_import)

    with pytest.raises(RuntimeError, match="openwakeword is not installed"):
        OpenWakeWordDetector()


def test_create_wake_detector_falls_back_when_openwakeword_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    real_import = builtins.__import__

    def blocked_import(name: str, *args: object, **kwargs: object) -> object:
        if name.startswith("openwakeword"):
            raise ImportError("blocked for test")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", blocked_import)

    detector = create_wake_detector(AppConfig(mode="live", wake_backend="openwakeword"))

    assert isinstance(detector, MockWakeWordDetector)


def test_openwakeword_default_model_does_not_pass_none(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, object]] = []

    class FakeModel:
        def __init__(self, **kwargs: object) -> None:
            calls.append(kwargs)

        def predict(self, audio: object) -> dict[str, float]:
            return {"fake": 0.0}

    package_module = types.ModuleType("openwakeword")
    model_module = types.ModuleType("openwakeword.model")
    utils_module = types.ModuleType("openwakeword.utils")
    model_module.Model = FakeModel
    utils_module.download_models = lambda model_names: None
    package_module.model = model_module
    package_module.utils = utils_module
    monkeypatch.setitem(sys.modules, "openwakeword", package_module)
    monkeypatch.setitem(sys.modules, "openwakeword.model", model_module)
    monkeypatch.setitem(sys.modules, "openwakeword.utils", utils_module)

    OpenWakeWordDetector()

    assert calls == [{"inference_framework": "onnx"}]


def test_openwakeword_auto_downloads_missing_named_model(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, object]] = []
    downloads: list[list[str]] = []

    class FakeModel:
        def __init__(self, **kwargs: object) -> None:
            calls.append(kwargs)
            if len(calls) == 1:
                raise RuntimeError("NO_SUCHFILE: File doesn't exist")

        def predict(self, audio: object) -> dict[str, float]:
            return {"fake": 0.0}

    def fake_download_models(model_names: list[str]) -> None:
        downloads.append(model_names)

    package_module = types.ModuleType("openwakeword")
    model_module = types.ModuleType("openwakeword.model")
    utils_module = types.ModuleType("openwakeword.utils")
    model_module.Model = FakeModel
    utils_module.download_models = fake_download_models
    package_module.model = model_module
    package_module.utils = utils_module
    monkeypatch.setitem(sys.modules, "openwakeword", package_module)
    monkeypatch.setitem(sys.modules, "openwakeword.model", model_module)
    monkeypatch.setitem(sys.modules, "openwakeword.utils", utils_module)

    OpenWakeWordDetector(wakeword_name="alexa")

    assert downloads == [["alexa"]]
    assert calls == [
        {"wakeword_models": ["alexa"], "inference_framework": "onnx"},
        {"wakeword_models": ["alexa"], "inference_framework": "onnx"},
    ]


def test_create_wake_detector_defaults_openwakeword_to_alexa(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class FakeOpenWakeWordDetector:
        def __init__(self, **kwargs: object) -> None:
            captured.update(kwargs)

    monkeypatch.setattr("wakeagent.main.OpenWakeWordDetector", FakeOpenWakeWordDetector)

    detector = create_wake_detector(AppConfig(mode="live", wake_backend="openwakeword"))

    assert isinstance(detector, FakeOpenWakeWordDetector)
    assert captured["wakeword_name"] == "alexa"
    assert captured["inference_framework"] == "onnx"
    assert captured["auto_download"] is True


def test_faster_whisper_missing_dependency_error_is_clear(monkeypatch: pytest.MonkeyPatch) -> None:
    real_import = builtins.__import__

    def blocked_import(name: str, *args: object, **kwargs: object) -> object:
        if name.startswith("faster_whisper"):
            raise ImportError("blocked for test")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", blocked_import)

    with pytest.raises(RuntimeError, match="faster-whisper is not installed"):
        FasterWhisperBackend()


def test_create_stt_backend_falls_back_when_faster_whisper_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    real_import = builtins.__import__

    def blocked_import(name: str, *args: object, **kwargs: object) -> object:
        if name.startswith("faster_whisper"):
            raise ImportError("blocked for test")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", blocked_import)

    backend = create_stt_backend(AppConfig(mode="live", stt_backend="faster-whisper"))

    assert isinstance(backend, MockSTTBackend)


def test_create_stt_backend_passes_faster_whisper_options(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class FakeFasterWhisperBackend:
        def __init__(self, **kwargs: object) -> None:
            captured.update(kwargs)

    monkeypatch.setattr("wakeagent.main.FasterWhisperBackend", FakeFasterWhisperBackend)

    backend = create_stt_backend(
        AppConfig(
            mode="live",
            stt_backend="faster-whisper",
            stt_model_size="medium",
            stt_model_dir=".models/faster-whisper",
            stt_local_files_only=True,
            stt_beam_size=3,
            stt_initial_prompt="custom prompt",
            stt_hotwords="Codex Cursor",
        )
    )

    assert isinstance(backend, FakeFasterWhisperBackend)
    assert captured["model_size"] == "medium"
    assert captured["model_dir"] == ".models/faster-whisper"
    assert captured["local_files_only"] is True
    assert captured["beam_size"] == 3
    assert captured["initial_prompt"] == "custom prompt"
    assert captured["hotwords"] == "Codex Cursor"


def test_download_stt_model_requires_faster_whisper(capsys) -> None:
    exit_code = download_stt_model(AppConfig(stt_backend="mock"))

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "requires --stt-backend faster-whisper" in captured.out


def test_main_download_stt_model_forces_faster_whisper(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    captured_config: dict[str, object] = {}

    def fake_create_stt_backend(config: AppConfig, allow_fallback: bool = True) -> MockSTTBackend:
        captured_config["config"] = config
        captured_config["allow_fallback"] = allow_fallback
        return MockSTTBackend()

    monkeypatch.setattr("wakeagent.main.create_stt_backend", fake_create_stt_backend)

    exit_code = main(["--download-stt-model", "--stt-model-size", "medium"])

    captured = capsys.readouterr()
    config = captured_config["config"]
    assert exit_code == 0
    assert isinstance(config, AppConfig)
    assert config.stt_backend == "faster-whisper"
    assert config.stt_model_size == "medium"
    assert captured_config["allow_fallback"] is False
    assert "model ready" in captured.out
