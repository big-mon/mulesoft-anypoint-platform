# Structure

## Directory Layout

```text
mulesoft-anypoint-platform/
├── config/
├── docs/
├── output/
├── src/
│   ├── api/
│   │   └── accounts.py
│   ├── auth/
│   │   └── client.py
│   ├── utils/
│   │   ├── config.py
│   │   ├── file_output.py
│   │   ├── http_client.py
│   │   ├── output_config.py
│   │   └── proxy.py
│   ├── export_common.py
│   ├── api_manager_export.py
│   ├── cloudhub_export.py
│   └── main.py
└── tests/
```

## Runtime Flow

1. `python -m src.main` loads configuration and creates a shared `AsyncHTTPClient`.
2. `src/auth/client.py` retrieves the OAuth access token.
3. `src/api/accounts.py` fetches organization environments.
4. `src/export_common.py` resolves shared export context.
5. `src/api_manager_export.py` and `src/cloudhub_export.py` run concurrently.
6. Each export module transforms the payload and writes JSON output when enabled.

## Module Responsibilities

### `src/main.py`

- Loads `.env` and output configuration
- Creates the shared async transport
- Orchestrates authentication, environment lookup, and both exports

### `src/export_common.py`

- Resolves the export config, base URL, and auth header
- Creates an owned transport only when a caller did not inject one
- Handles shared output writing for export modules

### `src/auth/client.py`

- Fetches and caches the OAuth access token
- Uses the shared transport for outbound HTTP

### `src/api/accounts.py`

- Fetches the organization environment list
- Uses the shared transport for outbound HTTP

### `src/api_manager_export.py`

- Fetches API Manager API lists per environment
- Fetches policies, contracts, alerts, and tiers per API
- Flattens and enriches the final payload
- Writes `api_manager.json` when enabled

### `src/cloudhub_export.py`

- Fetches Runtime Manager applications per environment
- Preserves the Runtime Manager payload shape
- Writes `cloudhub.json` when enabled

### `src/utils/http_client.py`

- Owns the shared `aiohttp` session
- Applies proxy selection through `ProxyConfig`
- Enforces global concurrency and minimum request spacing
- Retries `429` and `503` responses
- Honors `Retry-After` and otherwise applies exponential backoff with jitter

### `src/utils/proxy.py`

- Resolves `ANYPOINT_PROXY_URL`
- Resolves `ANYPOINT_HTTP_PROXY`
- Resolves `ANYPOINT_HTTPS_PROXY`
- Returns `aiohttp` request kwargs for a target URL

### `src/utils/config.py`

- Loads required credentials and base URL
- Loads HTTP pacing, retry, and timeout settings

### `src/utils/output_config.py`

- Loads `config/output_config.env`
- Controls output enable flags and output filenames

## Test Strategy

- Export modules are tested by injecting a fake transport from `tests/conftest.py`
- The shared HTTP client is tested directly for retry, proxy, and concurrency behavior
- Auth and Accounts API modules are tested independently from the export modules
