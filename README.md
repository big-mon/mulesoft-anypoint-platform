# Anypoint Platform Client

![](./mulesoft.jpg)

MuleSoft Anypoint Platform の環境単位データを取得し、JSON ファイルとして出力する Python ツールです。

## 概要

- `api_manager.json`: API Manager の API 一覧と詳細情報
- `cloudhub.json`: Runtime Manager のアプリケーション情報
- `src/main.py` から 2 つの export 処理を並列実行
- 外部 API 呼び出しは共有 `aiohttp` transport で一元管理

## 主な機能

### API Manager

- 環境ごとの API 一覧取得
- API ごとの policies / contracts / alerts / tiers 取得
- JSON 出力向けの整形と統合

### Runtime Manager

- 環境ごとのアプリケーション一覧取得
- Runtime Manager のレスポンス形状を維持した JSON 出力

## 必要条件

- Python 3.8 以上
- 使用ライブラリ
  - `aiohttp`
  - `python-dotenv`
  - `pytest`
  - `pytest-asyncio`

## セットアップ

```bash
git clone https://github.com/big-mon/mulesoft-anypoint-platform.git
cd mulesoft-anypoint-platform
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
cp .env.example .env
```

`.env` に次の値を設定します。

- `ANYPOINT_CLIENT_ID`: Anypoint Platform の client ID
- `ANYPOINT_CLIENT_SECRET`: Anypoint Platform の client secret
- `ANYPOINT_ORGANIZATION_ID`: organization ID
- `ANYPOINT_BASE_URL`: control plane の base URL。未設定時は `https://anypoint.mulesoft.com`

任意の proxy 設定:

- `ANYPOINT_PROXY_URL`: HTTP / HTTPS 共通 proxy
- `ANYPOINT_HTTP_PROXY`: HTTP 専用 proxy
- `ANYPOINT_HTTPS_PROXY`: HTTPS 専用 proxy

任意の HTTP 安全設定:

- `ANYPOINT_HTTP_MAX_CONCURRENCY`: 同時実行数。既定値 `5`
- `ANYPOINT_HTTP_MIN_INTERVAL_MS`: リクエスト間の最小待機時間。既定値 `200`
- `ANYPOINT_HTTP_MAX_RETRIES`: `429` / `503` の再試行回数。既定値 `5`
- `ANYPOINT_HTTP_BACKOFF_BASE_MS`: バックオフ基準値。既定値 `500`
- `ANYPOINT_HTTP_BACKOFF_MAX_MS`: バックオフ上限。既定値 `10000`
- `ANYPOINT_HTTP_TIMEOUT_SECONDS`: 総タイムアウト秒数。既定値 `30`

## レート制限と再試行

- すべての API 呼び出しは 1 つの共有 `aiohttp` transport を通ります。
- 短時間バーストを避けるため、最小送信間隔を守ってリクエストします。
- 再試行対象は `429` と `503` のみです。
- `Retry-After` が返る場合はその値を優先します。
- `Retry-After` が無い場合はジッター付き指数バックオフを使います。

## 出力設定

`config/output_config.env` で出力有無とファイル名を制御できます。

- `API_MANAGER_ENABLED`
- `API_MANAGER_FILENAME`
- `CLOUDHUB_ENABLED`
- `CLOUDHUB_FILENAME`

## 実行方法

```bash
.venv\Scripts\python src/main.py
```

出力ファイルは `output/YYYYMMDD_HHMM/` に保存されます。

- `api_manager.json`
- `cloudhub.json`

## 設定例

```env
ANYPOINT_PROXY_URL=http://proxy.local:8080
ANYPOINT_HTTP_MAX_CONCURRENCY=3
ANYPOINT_HTTP_MIN_INTERVAL_MS=300
ANYPOINT_HTTP_MAX_RETRIES=4
```

## 構成

- `src/main.py`
  - 設定読み込み、共有 transport 作成、認証、環境取得、export 起動
- `src/auth/client.py`
  - OAuth アクセストークンの取得とキャッシュ
- `src/api/accounts.py`
  - organization environments の取得
- `src/api_manager_export.py`
  - API Manager 情報の export
- `src/cloudhub_export.py`
  - Runtime Manager 情報の export
- `src/utils/http_client.py`
  - 共有 `aiohttp` transport、proxy、retry、rate limit
- `src/utils/proxy.py`
  - proxy 設定の解決
- `src/utils/output_config.py`
  - 出力設定の読み込み

詳しくは [docs/structure.md](docs/structure.md) を参照してください。

## テスト

```bash
.venv\Scripts\python -m pytest tests
```

## トラブルシューティング

### 認証エラー

- `.env` の認証情報を確認してください。

### ネットワークエラー

- Anypoint Platform への疎通を確認してください。
- proxy が必要な環境では `ANYPOINT_PROXY_URL` または scheme 別 proxy を設定してください。
- レート制限に近い場合は `ANYPOINT_HTTP_MAX_CONCURRENCY` を下げ、`ANYPOINT_HTTP_MIN_INTERVAL_MS` を上げてください。

## ライセンス

MIT License
