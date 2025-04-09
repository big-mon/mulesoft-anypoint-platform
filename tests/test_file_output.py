"""FileOutputのテスト"""

import os
import json
import pytest
from src.utils.file_output import FileOutput


@pytest.fixture
def output_dir(tmp_path):
    """出力ディレクトリのフィクスチャ"""
    output_path = tmp_path / "output"
    return str(output_path)


@pytest.fixture
def file_output():
    """FileOutputのフィクスチャ"""
    return FileOutput()


def test_prepare_output_folder(file_output):
    """出力ディレクトリ作成のテスト"""
    file_output.prepare_output_folder()
    assert os.path.exists("output")
    assert file_output._output_folder is not None


def test_output_json(file_output):
    """JSON出力のテスト"""
    test_data = {
        "test": "data",
        "number": 1
    }
    filename = "test.json"
    
    file_output.prepare_output_folder()
    output_path = file_output.output_json(test_data, filename)
    
    assert os.path.exists(output_path)
    
    with open(output_path, "r", encoding="utf-8") as f:
        saved_data = json.load(f)
    
    assert saved_data == test_data


def test_output_json_error(file_output):
    """出力フォルダ未準備時のエラーテスト"""
    test_data = {
        "test": "data"
    }
    filename = "test.json"
    
    with pytest.raises(RuntimeError):
        file_output.output_json(test_data, filename)
