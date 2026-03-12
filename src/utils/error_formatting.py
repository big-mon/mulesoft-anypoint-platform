"""Helpers for safe exception display."""

import re
from urllib.parse import urlsplit, urlunsplit


_URL_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9+.\-]*://[^\s'\"<>]+")


def format_exception_message(exc):
    """Return an exception message with URL userinfo redacted."""
    return redact_url_userinfo(str(exc))


def redact_url_userinfo(text):
    """Replace credentials in URL userinfo segments while keeping the host visible."""

    def _replace(match):
        candidate = match.group(0)
        split_result = urlsplit(candidate)
        if "@" not in split_result.netloc:
            return candidate

        redacted_netloc = re.sub(r"^[^@]+@", "***:***@", split_result.netloc, count=1)
        return urlunsplit(
            (
                split_result.scheme,
                redacted_netloc,
                split_result.path,
                split_result.query,
                split_result.fragment,
            )
        )

    return _URL_PATTERN.sub(_replace, text)
