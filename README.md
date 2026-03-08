# Anypoint Platform Client

![](./mulesoft.jpg)

MuleSoft Anypoint Platform の API Manager API と Runtime Manager API を使い、環境ごとの情報を取得して JSON として出力する Python スクリプトです。

## 概要

- `api_manager.json`: API Manager の一覧と詳細情報を出力
- `cloudhub.json`: Runtime Manager のアプリケーション情報を出力
- `src/main.py` から 2 系統の処理を並列実行

このリポジトリでは、出力物ごとに処理を 1 モジュールへまとめています。各モジュールは `API呼び出し -> 必要項目へ整形 -> JSON出力` の順で読める構造です。

## 主な機能

### API Manager

- API 一覧取得
- Policies 取得
- Contracts 取得
- Alerts 取得
- Tiers 取得
- 出力用 JSON への整形

### Runtime Manager

- アプリケーション一覧取得
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

`ANYPOINT_BASE_URL` を省略した場合は `https://anypoint.mulesoft.com` を使用します。

## 出力設定

`config/output_config.env` で出力有無とファイル名を制御できます。

- `API_MANAGER_ENABLED`
- `API_MANAGER_FILENAME`
- `CLOUDHUB_ENABLED`
- `CLOUDHUB_FILENAME`

## 実行方法

```bash
python src/main.py
```

実行すると `output/YYYYMMDD_HHMM/` 配下に以下を出力します。

- `api_manager.json`
- `cloudhub.json`

## 構成

- `src/main.py`
  - 認証、環境一覧取得、出力準備、2 系統の処理起動
- `src/api_manager_export.py`
  - API Manager の取得、整形、詳細反映、出力
- `src/cloudhub_export.py`
  - Runtime Manager の取得、整形、出力
- `src/api/accounts.py`
  - 組織配下の環境一覧取得
- `src/auth/client.py`
  - OAuth トークン取得
- `src/utils/file_output.py`
  - 出力ディレクトリ作成と JSON 出力
- `src/utils/output_config.py`
  - 出力設定読み込み

詳細は [docs/structure.md](docs/structure.md) を参照してください。

## テスト

```bash
python -m pytest tests/
```

## よくある問題

### 認証エラー

- `.env` の認証情報が正しいか確認してください。

### ネットワークエラー

- Anypoint Platform へ接続できるか確認してください。
- プロキシが必要な環境では環境変数で設定してください。

## ライセンス

MIT License
