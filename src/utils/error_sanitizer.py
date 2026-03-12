"""Helpers for removing secrets from error messages before logging."""

import re
from urllib.parse import urlsplit, urlunsplit


_URL_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*://[^\s'\"<>]+")


def sanitize_error_message(error):
    """Mask credentials embedded in URL-like text within an error message."""
    return _URL_PATTERN.sub(_sanitize_url_match, str(error))


def _sanitize_url_match(match):
    return sanitize_url(match.group(0))


def sanitize_url(url):
    """Return a copy of the URL with any userinfo replaced."""
    try:
        parts = urlsplit(url)
    except ValueError:
        return url

    if not parts.netloc or "@" not in parts.netloc:
        return url

    host = parts.netloc.rsplit("@", 1)[1]
    return urlunsplit(parts._replace(netloc=f"***@{host}"))
