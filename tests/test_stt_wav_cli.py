from pathlib import Path

from wakeagent.config import AppConfig
from wakeagent.main import transcribe_wav_once


def test_transcribe_wav_once_reports_missing_file(capsys) -> None:
    exit_code = transcribe_wav_once(AppConfig(stt_backend="mock"), Path("missing.wav"))

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "does not exist" in captured.out


def test_transcribe_wav_once_uses_mock_backend(capsys) -> None:
    wav_path = Path("tests/audio/test_1.wav")
    exit_code = transcribe_wav_once(AppConfig(stt_backend="mock", transcript="hello world"), wav_path)

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "backend=mock" in captured.out
    assert "[transcript] hello world" in captured.out
