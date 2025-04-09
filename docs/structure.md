# アプリケーション構造設計書

## 1. ディレクトリ構造

```
src/
├── __init__.py
├── main.py                     # エントリーポイント
├── auth/
│   ├── __init__.py
│   └── client.py              # 認証関連の処理
├── api/
│   ├── __init__.py
│   ├── api_manager.py         # API Manager関連の処理
│   └── runtime_manager.py     # Runtime Manager関連の処理
└── utils/
    ├── __init__.py
    ├── exceptions.py          # カスタム例外クラス
    ├── file_output.py         # ファイル出力処理
    └── output_config.py       # 出力設定管理

config/                        # 設定ファイル
└── output_config.env          # 出力設定

tests/                         # テストコード
├── __init__.py
├── test_auth.py
├── test_api_manager.py
├── test_file_output.py
├── test_output_config.py
└── test_runtime_manager.py
```

## 2. モジュール説明

### 2.1 auth/client.py
- 認証関連の処理を集約
- アクセストークンの取得と管理
- トークンのキャッシュ機能

### 2.2 utils/file_output.py
- JSONファイルの出力処理
- タイムスタンプベースの出力フォルダ管理

### 2.3 utils/output_config.py
- 出力設定の管理
- 設定ファイル（output_config.env）の読み込み
- 出力要否や出力ファイル名の制御

### 2.4 config/output_config.env
- 出力設定を管理する環境変数ファイル
- アプリケーション情報などの出力制御
- 各設定項目にコメントで説明を付与

### 2.2 api/api_manager.py
- API Manager APIとの通信処理
- アプリケーション情報の取得
- ポリシー設定の取得

### 2.3 api/runtime_manager.py
- Runtime Manager APIとの通信処理
- デプロイメント情報の取得
- アプリケーションステータスの取得

### 2.4 utils/config.py
- 環境変数の読み込みと管理
- 設定値の一元管理
- デフォルト値の定義

### 2.5 utils/exceptions.py
- カスタム例外クラスの定義
- エラーハンドリングの統一

## 3. クラス設計

### 3.1 AuthClient
```python
class AuthClient:
    def __init__(self)
    def get_access_token()
    def refresh_token()
    def is_token_valid()
```

### 3.2 APIManagerClient
```python
class APIManagerClient:
    def __init__(self, auth_client)
    def get_applications()
    def get_policies()
```

### 3.3 RuntimeManagerClient
```python
class RuntimeManagerClient:
    def __init__(self, auth_client)
    def get_deployments()
    def get_status()
```

## 4. 実装方針

1. 各機能を適切なモジュールに分割し、責務を明確化
2. 依存性注入を活用し、テスト容易性を確保
3. エラーハンドリングを統一的に実装
4. ログ出力を適切に実装
5. 非同期処理の導入検討
6. キャッシュ機能の実装検討
