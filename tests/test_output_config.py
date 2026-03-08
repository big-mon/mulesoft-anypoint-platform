"""Tests for OutputConfig."""

import pytest

from src.utils.output_config import OutputConfig


@pytest.fixture
def test_config_file(tmp_path):
    """Create a temporary config file."""
    config_content = """API_MANAGER_ENABLED=true
API_MANAGER_FILENAME=api-manager-full.json
"""
    config_file = tmp_path / "output_config.env"
    config_file.write_text(config_content, encoding="utf-8")
    return config_file


def test_get_output_setting(monkeypatch, test_config_file):
    """It reads enabled flags from configuration."""
    monkeypatch.setattr(
        "src.utils.output_config.OutputConfig._load_config",
        lambda self: {"API_MANAGER_ENABLED": "true"},
    )
    config = OutputConfig()
    assert config.get_output_setting("api_manager") is True


def test_get_output_filename(monkeypatch, test_config_file):
    """It reads output filenames from configuration."""
    monkeypatch.setattr(
        "src.utils.output_config.OutputConfig._load_config",
        lambda self: {"API_MANAGER_FILENAME": "api-manager-full.json"},
    )
    config = OutputConfig()
    assert config.get_output_filename("api_manager") == "api-manager-full.json"


def test_is_output_required(monkeypatch, test_config_file):
    """It reports whether any output is enabled."""
    monkeypatch.setattr(
        "src.utils.output_config.OutputConfig._load_config",
        lambda self: {"CLOUDHUB_ENABLED": "true"},
    )
    config = OutputConfig()
    assert config.is_output_required is True
