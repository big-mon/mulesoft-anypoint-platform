# Anypoint Platform Client

![](./mulesoft.jpg)

MuleSoft Anypoint Platform の API Manager API と Runtime Manager API を使い、環境単位の情報を取得して JSON ファイルとして出力する Python スクリプトです。

## 概要

- `api_manager.json`: API Manager の一覧と詳細情報
- `cloudhub.json`: Runtime Manager のアプリケーション情報
- `src/main.py` から 2 つのエクスポート処理を並列実行

コードベースは単純な構成を意図しています。各出力は 1 モジュールに分かれており、`API取得 -> 必要項目へ整形 -> JSON出力` の流れで読めるようにしています。

## 主な機能

### API Manager

- API 一覧の取得
- Policies の取得
- Contracts の取得
- Alerts の取得
- Tiers の取得
- 出力用 JSON への整形

### Runtime Manager

- アプリケーション一覧の取得
- 出力用 JSON への整形

## 必要環境

- Python 3.8 以上
- 必要ライブラリ
  - `requests`
  - `aiohttp`
  - `python-dotenv`
  - `pytest`
  - `pytest-asyncio`

## セットアップ

```bash
git clone https://github.com/big-mon/mulesoft-anypoint-platform.git
cd mulesoft-anypoint-platform
pip install -r requirements.txt
cp .env.example .env
```

`.env` に以下を設定してください。

- `ANYPOINT_CLIENT_ID`
- `ANYPOINT_CLIENT_SECRET`
- `ANYPOINT_ORGANIZATION_ID`
- `ANYPOINT_BASE_URL`
- `ANYPOINT_PROXY_URL`
- `ANYPOINT_HTTP_PROXY`
- `ANYPOINT_HTTPS_PROXY`

`ANYPOINT_BASE_URL` を省略した場合は `https://anypoint.mulesoft.com` を使用します。

Proxy が不要な場合は、Proxy 関連の環境変数は未設定のままで構いません。設定されている場合のみ Proxy 経由で通信します。

## 出力設定

`config/output_config.env` で出力可否とファイル名を制御できます。

- `API_MANAGER_ENABLED`
- `API_MANAGER_FILENAME`
- `CLOUDHUB_ENABLED`
- `CLOUDHUB_FILENAME`

## 使い方

```bash
python src/main.py
```

実行すると `output/YYYYMMDD_HHMM/` 配下に以下を出力します。

- `api_manager.json`
- `cloudhub.json`

## 構成

- `src/main.py`
  - 認証、環境一覧取得、出力準備、各処理の起動
- `src/api_manager_export.py`
  - API Manager の取得、整形、詳細付与、出力
- `src/cloudhub_export.py`
  - Runtime Manager の取得、整形、出力
- `src/api/accounts.py`
  - 組織配下の環境一覧取得
- `src/auth/client.py`
  - OAuth トークン取得
- `src/utils/file_output.py`
  - 出力ディレクトリ作成と JSON 書き込み
- `src/utils/output_config.py`
  - 出力設定の読み込み
- `src/utils/proxy.py`
  - Proxy 設定の解決

詳細は [docs/structure.md](docs/structure.md) を参照してください。

## テスト

```bash
python -m pytest tests/
```

## トラブルシュート

### 認証エラー

- `.env` の認証情報が正しいか確認してください。

### ネットワークエラー

- Anypoint Platform へ接続できることを確認してください。
- Proxy が必要な環境では `ANYPOINT_PROXY_URL` または `ANYPOINT_HTTP_PROXY` / `ANYPOINT_HTTPS_PROXY` を設定してください。

## ライセンス

MIT License
