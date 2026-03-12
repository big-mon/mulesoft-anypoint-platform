"""Tests for safe exception formatting."""

from src.utils.error_formatting import redact_url_userinfo


def test_redact_url_userinfo_hides_credentials_only():
    """It preserves the URL while removing userinfo credentials."""
    message = "proxy failed via http://user:pass@proxy.local:8080/path?x=1"

    result = redact_url_userinfo(message)

    assert result == "proxy failed via http://***:***@proxy.local:8080/path?x=1"
