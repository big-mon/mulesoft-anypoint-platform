"""Application configuration helpers."""

import os

from dotenv import load_dotenv


DEFAULT_BASE_URL = "https://anypoint.mulesoft.com"
DEFAULT_HTTP_MAX_CONCURRENCY = 5
DEFAULT_HTTP_MIN_INTERVAL_MS = 200
DEFAULT_HTTP_MAX_RETRIES = 5
DEFAULT_HTTP_BACKOFF_BASE_MS = 500
DEFAULT_HTTP_BACKOFF_MAX_MS = 10000
DEFAULT_HTTP_TIMEOUT_SECONDS = 30


class Config:
    """Load runtime configuration from the environment."""

    def __init__(self):
        load_dotenv()
        self.__client_id = os.getenv("ANYPOINT_CLIENT_ID")
        self.__client_secret = os.getenv("ANYPOINT_CLIENT_SECRET")
        self._organization_id = os.getenv("ANYPOINT_ORGANIZATION_ID")
        self._base_url = os.getenv("ANYPOINT_BASE_URL", DEFAULT_BASE_URL)
        self._http_max_concurrency = self._read_int(
            "ANYPOINT_HTTP_MAX_CONCURRENCY",
            DEFAULT_HTTP_MAX_CONCURRENCY,
            minimum=1,
        )
        self._http_min_interval_ms = self._read_int(
            "ANYPOINT_HTTP_MIN_INTERVAL_MS",
            DEFAULT_HTTP_MIN_INTERVAL_MS,
            minimum=0,
        )
        self._http_max_retries = self._read_int(
            "ANYPOINT_HTTP_MAX_RETRIES",
            DEFAULT_HTTP_MAX_RETRIES,
            minimum=0,
        )
        self._http_backoff_base_ms = self._read_int(
            "ANYPOINT_HTTP_BACKOFF_BASE_MS",
            DEFAULT_HTTP_BACKOFF_BASE_MS,
            minimum=1,
        )
        self._http_backoff_max_ms = self._read_int(
            "ANYPOINT_HTTP_BACKOFF_MAX_MS",
            DEFAULT_HTTP_BACKOFF_MAX_MS,
            minimum=1,
        )
        self._http_timeout_seconds = self._read_int(
            "ANYPOINT_HTTP_TIMEOUT_SECONDS",
            DEFAULT_HTTP_TIMEOUT_SECONDS,
            minimum=1,
        )

    @staticmethod
    def _read_int(env_key, default, minimum):
        value = os.getenv(env_key)
        if value is None:
            return default
        try:
            parsed = int(value)
        except ValueError:
            return default
        return parsed if parsed >= minimum else default

    def get_client_id(self):
        """Return the configured client ID."""
        return self.__client_id

    def get_client_secret(self):
        """Return the configured client secret."""
        return self.__client_secret

    def get_organization_id(self):
        """Return the configured organization ID."""
        if self._organization_id is None:
            return None
        return self._organization_id.strip()

    def get_base_url(self):
        """Return the configured Anypoint base URL."""
        if self._base_url is None:
            return None
        return self._base_url.rstrip("/")

    def get_http_max_concurrency(self):
        """Return the maximum concurrent outbound requests."""
        return self._http_max_concurrency

    def get_http_min_interval_ms(self):
        """Return the minimum delay between outbound requests."""
        return self._http_min_interval_ms

    def get_http_max_retries(self):
        """Return the number of retry attempts for retryable responses."""
        return self._http_max_retries

    def get_http_backoff_base_ms(self):
        """Return the retry backoff base in milliseconds."""
        return self._http_backoff_base_ms

    def get_http_backoff_max_ms(self):
        """Return the retry backoff ceiling in milliseconds."""
        return self._http_backoff_max_ms

    def get_http_timeout_seconds(self):
        """Return the total HTTP timeout in seconds."""
        return self._http_timeout_seconds

    @property
    def is_valid(self):
        """Return True when the required configuration is present."""
        return all(
            [
                self.__client_id,
                self.__client_secret,
                self._organization_id,
                self._base_url,
            ]
        )
