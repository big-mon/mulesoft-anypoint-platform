# 構成メモ

## 1. ディレクトリ構成

```text
mulesoft-anypoint-platform/
├── config/               # 出力設定
├── docs/                 # ドキュメント
├── output/               # JSON 出力先
├── src/
│   ├── api/              # 補助 API 呼び出し
│   ├── auth/             # 認証
│   ├── utils/            # 共通ユーティリティ
│   ├── api_manager_export.py
│   ├── cloudhub_export.py
│   └── main.py
└── tests/                # テスト
```

## 2. 現在の設計方針

このアプリケーションは単純な取得・整形・出力ツールとして設計しています。

- 出力物ごとに 1 モジュール
- 不要な service 層や client 層は作らない
- 共通化は認証、環境一覧取得、出力処理だけに限定

読み順は以下です。

1. `src/main.py` で設定読み込み、認証、環境一覧取得
2. `src/api_manager_export.py` で API Manager 情報を出力
3. `src/cloudhub_export.py` で Runtime Manager 情報を出力

## 3. モジュール一覧

### `src/main.py`

- エントリーポイント
- `AuthClient` でアクセストークン取得
- `AccountsAPI` で環境一覧取得
- 出力ディレクトリ準備
- API Manager / Runtime Manager の 2 処理を `asyncio.gather()` で実行

### `src/api_manager_export.py`

- API Manager の一覧取得
- API 一覧を出力用に整形
- API ごとの詳細情報取得
  - policies
  - contracts
  - alerts
  - tiers
- 詳細情報を API 単位で反映
- `api_manager.json` 出力

### `src/cloudhub_export.py`

- Runtime Manager のアプリケーション一覧取得
- 出力用に整形
- `cloudhub.json` 出力

### `src/api/accounts.py`

- 組織配下の環境一覧取得

### `src/auth/client.py`

- OAuth クライアントクレデンシャルでアクセストークン取得

### `src/utils/file_output.py`

- 出力ディレクトリ作成
- JSON ファイル書き込み

### `src/utils/output_config.py`

- `config/output_config.env` の読み込み
- 出力有無とファイル名の参照

### `src/utils/config.py`

- `.env` の読み込み
- 必須設定値の検証

## 4. 処理フロー

### API Manager

1. 環境ごとに API 一覧を取得
2. 出力に必要な項目へ整形
3. 各 API の詳細情報を並列取得
4. API ID 単位で詳細を反映
5. 設定が有効なら `api_manager.json` を出力

### Runtime Manager

1. 環境ごとにアプリケーション一覧を取得
2. 出力に必要な構造へ整形
3. 設定が有効なら `cloudhub.json` を出力

## 5. テスト方針

- 公開入口単位でテストする
  - `export_api_manager_info(...)`
  - `export_cloudhub_info(...)`
- HTTP 層は `aiohttp.ClientSession.get` をモックして検証する
- 出力有無は `FileOutput` と `OutputConfig` をモックして確認する
