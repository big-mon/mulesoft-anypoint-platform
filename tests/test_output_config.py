"""Tests for OutputConfig."""

from src.utils.output_config import OutputConfig


def test_get_output_setting(monkeypatch):
    """It reads enabled flags from configuration."""
    monkeypatch.setattr(
        "src.utils.output_config.OutputConfig._load_config",
        lambda self: {"API_MANAGER_ENABLED": "true"},
    )
    config = OutputConfig()
    assert config.get_output_setting("api_manager") is True


def test_get_output_setting_disabled(monkeypatch):
    """It returns False when the enabled flag is false."""
    monkeypatch.setattr(
        "src.utils.output_config.OutputConfig._load_config",
        lambda self: {"API_MANAGER_ENABLED": "false"},
    )
    config = OutputConfig()
    assert config.get_output_setting("api_manager") is False


def test_get_output_filename(monkeypatch):
    """It reads output filenames from configuration."""
    monkeypatch.setattr(
        "src.utils.output_config.OutputConfig._load_config",
        lambda self: {"API_MANAGER_FILENAME": "api-manager-full.json"},
    )
    config = OutputConfig()
    assert config.get_output_filename("api_manager") == "api-manager-full.json"


def test_is_output_required(monkeypatch):
    """It reports whether any output is enabled."""
    monkeypatch.setattr(
        "src.utils.output_config.OutputConfig._load_config",
        lambda self: {"CLOUDHUB_ENABLED": "true"},
    )
    config = OutputConfig()
    assert config.is_output_required is True
