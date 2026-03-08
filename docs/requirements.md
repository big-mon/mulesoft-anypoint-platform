# Requirements

## Functional Requirements

- Use MuleSoft Anypoint Platform APIs to export:
  - API Manager API list and detail data
  - Runtime Manager application data
- Write results as JSON files under `output/YYYYMMDD_HHMM/`
- Support optional proxy configuration for outbound requests
- Keep the current output file controls through `config/output_config.env`

## Technical Requirements

- Use Python 3.8+
- Use `aiohttp` for all outbound HTTP traffic
- Use `python-dotenv` for environment loading
- Keep the main workflow asynchronous end-to-end

## Non-Functional Requirements

- Share one HTTP transport across authentication, environment lookup, and export flows
- Apply conservative rate limiting to avoid burst traffic
- Limit concurrent requests with a global semaphore
- Enforce a minimum interval between requests
- Retry only retryable responses: `429` and `503`
- Honor `Retry-After` when present
- Fall back to exponential backoff with jitter when `Retry-After` is absent
- Keep retry and pacing settings configurable through `.env`
- Preserve existing proxy behavior for HTTP and HTTPS targets

## Default HTTP Safety Settings

- `ANYPOINT_HTTP_MAX_CONCURRENCY=5`
- `ANYPOINT_HTTP_MIN_INTERVAL_MS=200`
- `ANYPOINT_HTTP_MAX_RETRIES=5`
- `ANYPOINT_HTTP_BACKOFF_BASE_MS=500`
- `ANYPOINT_HTTP_BACKOFF_MAX_MS=10000`
- `ANYPOINT_HTTP_TIMEOUT_SECONDS=30`

## Test Requirements

- Validate export formatting for both API Manager and Runtime Manager
- Validate proxy resolution for shared and scheme-specific proxies
- Validate auth and Accounts API requests after async migration
- Validate retry behavior for:
  - `429` with `Retry-After`
  - `503` without `Retry-After`
  - non-retryable `4xx`
- Validate concurrency limiting behavior
