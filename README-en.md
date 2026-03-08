# Anypoint Platform Client

![](./mulesoft.jpg)

A Python tool that fetches environment-level data from MuleSoft Anypoint Platform and writes the results as JSON files.

## Overview

- `api_manager.json`: API Manager list plus policy, contract, alert, and tier details
- `cloudhub.json`: Runtime Manager application data
- `python -m src.main` runs both export flows concurrently
- All outbound HTTP traffic is now handled by one shared `aiohttp` transport

## Features

### API Manager

- Fetch API list per environment
- Fetch policies, contracts, alerts, and tiers per API
- Flatten and enrich the payload for JSON output

### Runtime Manager

- Fetch application list per environment
- Preserve the Runtime Manager payload shape in JSON output

## Requirements

- Python 3.8+
- Required libraries
  - `aiohttp`
  - `python-dotenv`
  - `pytest`
  - `pytest-asyncio`

## Setup

```bash
git clone https://github.com/big-mon/mulesoft-anypoint-platform.git
cd mulesoft-anypoint-platform
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
cp .env.example .env
```

Set the following values in `.env`:

- `ANYPOINT_CLIENT_ID`: Anypoint Platform client ID
- `ANYPOINT_CLIENT_SECRET`: Anypoint Platform client secret
- `ANYPOINT_ORGANIZATION_ID`: organization ID
- `ANYPOINT_BASE_URL`: control plane base URL, defaults to `https://anypoint.mulesoft.com`

Optional proxy settings:

- `ANYPOINT_PROXY_URL`: shared proxy for all HTTP and HTTPS requests
- `ANYPOINT_HTTP_PROXY`: HTTP-only proxy override
- `ANYPOINT_HTTPS_PROXY`: HTTPS-only proxy override

Optional HTTP safety settings:

- `ANYPOINT_HTTP_MAX_CONCURRENCY`: max concurrent outbound requests, default `5`
- `ANYPOINT_HTTP_MIN_INTERVAL_MS`: minimum delay between requests, default `200`
- `ANYPOINT_HTTP_MAX_RETRIES`: retry count for `429` and `503`, default `5`
- `ANYPOINT_HTTP_BACKOFF_BASE_MS`: retry backoff base, default `500`
- `ANYPOINT_HTTP_BACKOFF_MAX_MS`: retry backoff ceiling, default `10000`
- `ANYPOINT_HTTP_TIMEOUT_SECONDS`: total request timeout, default `30`

## Rate Limiting and Retry

- All API calls share one `aiohttp` transport instance.
- Requests are paced with a conservative minimum interval to avoid burst traffic.
- Retries are applied only to retryable responses: `429` and `503`.
- `Retry-After` is honored when present.
- When `Retry-After` is absent, the client uses exponential backoff with jitter.

## Output Configuration

Use `config/output_config.env` to control whether each file is written and what filename is used.

- `API_MANAGER_ENABLED`
- `API_MANAGER_FILENAME`
- `CLOUDHUB_ENABLED`
- `CLOUDHUB_FILENAME`

## Usage

```bash
.venv\Scripts\python -m src.main
```

The script writes output files under `output/YYYYMMDD_HHMM/`.

- `api_manager.json`
- `cloudhub.json`

## Configuration Example

```env
ANYPOINT_PROXY_URL=http://proxy.local:8080
ANYPOINT_HTTP_MAX_CONCURRENCY=3
ANYPOINT_HTTP_MIN_INTERVAL_MS=300
ANYPOINT_HTTP_MAX_RETRIES=4
```

## Structure

- `src/main.py`
  - loads configuration, creates the shared transport, authenticates, and starts both exports
- `src/export_common.py`
  - shares export setup, auth headers, owned client handling, and output writing
- `src/auth/client.py`
  - retrieves and caches the OAuth access token
- `src/api/accounts.py`
  - fetches organization environments
- `src/api_manager_export.py`
  - exports API Manager data
- `src/cloudhub_export.py`
  - exports Runtime Manager data
- `src/utils/http_client.py`
  - shared `aiohttp` transport, proxy handling, retry, and rate limiting
- `src/utils/proxy.py`
  - resolves proxy settings from environment variables
- `src/utils/output_config.py`
  - controls file output

See [docs/structure.md](docs/structure.md) for more detail.

## Testing

```bash
.venv\Scripts\python -m pytest tests
```

## Troubleshooting

### Authentication errors

- Verify the credentials in `.env`.

### Network errors

- Verify connectivity to Anypoint Platform.
- If your environment requires a proxy, set `ANYPOINT_PROXY_URL` or the scheme-specific proxy variables.
- If you still hit remote throttling, lower `ANYPOINT_HTTP_MAX_CONCURRENCY` and increase `ANYPOINT_HTTP_MIN_INTERVAL_MS`.

## License

MIT License
