"""Tests for Config."""

from src.utils.config import (
    Config,
    DEFAULT_HTTP_BACKOFF_BASE_MS,
    DEFAULT_HTTP_BACKOFF_MAX_MS,
    DEFAULT_HTTP_MAX_CONCURRENCY,
    DEFAULT_HTTP_MAX_RETRIES,
    DEFAULT_HTTP_MIN_INTERVAL_MS,
    DEFAULT_HTTP_TIMEOUT_SECONDS,
)


def test_config_uses_default_http_settings(monkeypatch):
    """It falls back to conservative defaults when env vars are missing."""
    monkeypatch.setenv("ANYPOINT_CLIENT_ID", "client-id")
    monkeypatch.setenv("ANYPOINT_CLIENT_SECRET", "client-secret")
    monkeypatch.setenv("ANYPOINT_ORGANIZATION_ID", "org-id")
    monkeypatch.delenv("ANYPOINT_HTTP_MAX_CONCURRENCY", raising=False)
    monkeypatch.delenv("ANYPOINT_HTTP_MIN_INTERVAL_MS", raising=False)
    monkeypatch.delenv("ANYPOINT_HTTP_MAX_RETRIES", raising=False)
    monkeypatch.delenv("ANYPOINT_HTTP_BACKOFF_BASE_MS", raising=False)
    monkeypatch.delenv("ANYPOINT_HTTP_BACKOFF_MAX_MS", raising=False)
    monkeypatch.delenv("ANYPOINT_HTTP_TIMEOUT_SECONDS", raising=False)

    config = Config()

    assert config.get_http_max_concurrency() == DEFAULT_HTTP_MAX_CONCURRENCY
    assert config.get_http_min_interval_ms() == DEFAULT_HTTP_MIN_INTERVAL_MS
    assert config.get_http_max_retries() == DEFAULT_HTTP_MAX_RETRIES
    assert config.get_http_backoff_base_ms() == DEFAULT_HTTP_BACKOFF_BASE_MS
    assert config.get_http_backoff_max_ms() == DEFAULT_HTTP_BACKOFF_MAX_MS
    assert config.get_http_timeout_seconds() == DEFAULT_HTTP_TIMEOUT_SECONDS


def test_config_reads_http_settings_from_env(monkeypatch):
    """It uses configured overrides for HTTP behavior."""
    monkeypatch.setenv("ANYPOINT_CLIENT_ID", "client-id")
    monkeypatch.setenv("ANYPOINT_CLIENT_SECRET", "client-secret")
    monkeypatch.setenv("ANYPOINT_ORGANIZATION_ID", "org-id")
    monkeypatch.setenv("ANYPOINT_HTTP_MAX_CONCURRENCY", "7")
    monkeypatch.setenv("ANYPOINT_HTTP_MIN_INTERVAL_MS", "300")
    monkeypatch.setenv("ANYPOINT_HTTP_MAX_RETRIES", "2")
    monkeypatch.setenv("ANYPOINT_HTTP_BACKOFF_BASE_MS", "750")
    monkeypatch.setenv("ANYPOINT_HTTP_BACKOFF_MAX_MS", "1500")
    monkeypatch.setenv("ANYPOINT_HTTP_TIMEOUT_SECONDS", "45")

    config = Config()

    assert config.get_http_max_concurrency() == 7
    assert config.get_http_min_interval_ms() == 300
    assert config.get_http_max_retries() == 2
    assert config.get_http_backoff_base_ms() == 750
    assert config.get_http_backoff_max_ms() == 1500
    assert config.get_http_timeout_seconds() == 45
