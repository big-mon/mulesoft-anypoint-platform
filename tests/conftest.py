"""テスト設定"""

import pytest


@pytest.fixture
def event_loop():
    """非同期テスト用のイベントループフィクスチャ"""
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
