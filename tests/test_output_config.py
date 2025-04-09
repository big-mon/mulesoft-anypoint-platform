"""OutputConfigのテスト"""

import os
import pytest
from src.utils.output_config import OutputConfig


@pytest.fixture
def test_config_file(tmp_path):
    """テスト用の設定ファイルを作成する"""
    config_content = """# APIマネージャーから取得したアプリケーション一覧情報の出力設定
APPLICATIONS_ENABLED=true
APPLICATIONS_FILENAME=applications-full.json
"""
    config_file = tmp_path / "output_config.env"
    config_file.write_text(config_content, encoding="utf-8")
    return config_file


def test_get_output_setting(monkeypatch, test_config_file):
    """出力設定の取得をテスト"""
    monkeypatch.setattr("src.utils.output_config.OutputConfig._load_config", 
                       lambda self: {"APPLICATIONS_ENABLED": "true"})
    config = OutputConfig()
    assert config.get_output_setting("applications") is True


def test_get_output_filename(monkeypatch, test_config_file):
    """出力ファイル名の取得をテスト"""
    monkeypatch.setattr("src.utils.output_config.OutputConfig._load_config",
                       lambda self: {"APPLICATIONS_FILENAME": "applications-full.json"})
    config = OutputConfig()
    assert config.get_output_filename("applications") == "applications-full.json"


def test_is_output_required(monkeypatch, test_config_file):
    """出力要否の判定をテスト"""
    monkeypatch.setattr("src.utils.output_config.OutputConfig._load_config",
                       lambda self: {"APPLICATIONS_ENABLED": "true"})
    config = OutputConfig()
    assert config.is_output_required is True
