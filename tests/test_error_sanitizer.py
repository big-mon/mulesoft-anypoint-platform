"""Tests for secret-safe error logging helpers."""

from src.utils.error_sanitizer import sanitize_error_message


def test_sanitize_error_message_masks_url_userinfo():
    """It redacts credentials while keeping the host visible."""
    message = (
        "proxy http://user:pass@proxy.local:8080 refused "
        "https://anypoint.mulesoft.com/accounts"
    )

    sanitized = sanitize_error_message(message)

    assert sanitized == (
        "proxy http://***@proxy.local:8080 refused "
        "https://anypoint.mulesoft.com/accounts"
    )


def test_sanitize_error_message_leaves_urls_without_userinfo_unchanged():
    """It preserves unrelated URLs so failures stay understandable."""
    message = "request failed for https://anypoint.mulesoft.com/accounts"

    assert sanitize_error_message(message) == message
