# Anypoint Platform Client

![](./mulesoft.jpg)

A Python script that uses MuleSoft Anypoint Platform APIs to fetch environment-level data from API Manager and Runtime Manager, then writes the results as JSON files.

## Overview

- `api_manager.json`: API Manager list and detail data
- `cloudhub.json`: Runtime Manager application data
- `src/main.py` starts both export flows concurrently

The codebase is intentionally simple. Each output has one module, and each module follows the same readable flow: `fetch API data -> transform required fields -> write JSON`.

## Features

### API Manager

- Fetch API list
- Fetch policies
- Fetch contracts
- Fetch alerts
- Fetch tiers
- Transform data for JSON output

### Runtime Manager

- Fetch application list
- Transform data for JSON output

## Requirements

- Python 3.8+
- Required libraries
  - `requests`
  - `aiohttp`
  - `python-dotenv`
  - `pytest`
  - `pytest-asyncio`

## Setup

```bash
git clone https://github.com/big-mon/mulesoft-anypoint-platform.git
cd mulesoft-anypoint-platform
pip install -r requirements.txt
cp .env.example .env
```

Set the following values in `.env`:

- `ANYPOINT_CLIENT_ID`: Anypoint Platform Client ID
- `ANYPOINT_CLIENT_SECRET`: Anypoint Platform Client Secret
- `ANYPOINT_ORGANIZATION_ID`: Organization ID
- `ANYPOINT_BASE_URL`: Anypoint Platform Base URL (optional)
- `ANYPOINT_PROXY_URL`: Shared proxy URL for all requests (optional)
- `ANYPOINT_HTTP_PROXY`: HTTP proxy override (optional)
- `ANYPOINT_HTTPS_PROXY`: HTTPS proxy override (optional)

If `ANYPOINT_BASE_URL` is omitted, the default is `https://anypoint.mulesoft.com`.

## Output Configuration

Use `config/output_config.env` to control whether each file is written and what filename is used.

- `API_MANAGER_ENABLED`
- `API_MANAGER_FILENAME`
- `CLOUDHUB_ENABLED`
- `CLOUDHUB_FILENAME`

## Usage

```bash
python src/main.py
```

The script writes output files under `output/YYYYMMDD_HHMM/`.

- `api_manager.json`
- `cloudhub.json`

## Structure

- `src/main.py`
  - Authentication, environment lookup, output preparation, and task startup
- `src/api_manager_export.py`
  - API Manager fetch, transform, detail enrichment, and output
- `src/cloudhub_export.py`
  - Runtime Manager fetch, transform, and output
- `src/api/accounts.py`
  - Organization environment lookup
- `src/auth/client.py`
  - OAuth token retrieval
- `src/utils/file_output.py`
  - Output directory creation and JSON writing
- `src/utils/output_config.py`
  - Output configuration loading

See [docs/structure.md](docs/structure.md) for more detail.

## Testing

```bash
python -m pytest tests/
```

## Troubleshooting

### Authentication errors

- Verify the credentials in `.env`.

### Network errors

- Verify connectivity to Anypoint Platform.
- If your environment requires a proxy, set `ANYPOINT_PROXY_URL` or the scheme-specific proxy variables.

## License

MIT License
