# プロジェクト構造

## 1. ディレクトリ構造

```
anypoint-platform-client/
├── docs/               # ドキュメント
├── src/               # ソースコード
│   ├── api/          # API クライアント
│   ├── services/     # サービス層
│   └── utils/        # ユーティリティ
├── tests/            # テストコード
└── output/           # 出力ファイル
```

## 2. モジュール構成

### 2.1 api/api_manager.py
- API Manager API クライアント
- API 情報の取得
- ポリシー、コントラクト、アラート、ティア情報の取得

### 2.2 api/cloudhub.py
- CloudHub API クライアント
- アプリケーション情報の取得
- デプロイメント情報の取得

### 2.3 services/api_manager_service.py
- API Manager 情報の取得と整理
- 非同期処理の制御
- 出力制御

### 2.4 services/cloudhub_service.py
- CloudHub 情報の取得と整理
- 非同期処理の制御
- 出力制御

### 2.5 utils/config.py
- 環境変数の読み込みと管理
- 設定値の一元管理
- デフォルト値の定義

### 2.6 utils/exceptions.py
- カスタム例外クラスの定義
- エラーハンドリングの統一

### 2.7 utils/file_output.py
- ファイル出力の制御
- JSON形式での出力
- 出力ディレクトリの管理

### 2.8 utils/output_config.py
- 出力設定の管理
- ファイル名の設定
- 出力要否の制御

## 3. クラス設計

### 3.1 APIManagerClient
```python
class APIManagerClient:
    def __init__(self, token, environments)
    async def get_applications()
    async def get_applications_async(self, session, env)
    def compact_applications(self, applications)
    async def get_policies_async(self, session, org_id, env_id, api_id)
    async def get_contracts_async(self, session, org_id, env_id, api_id)
    async def get_alerts_async(self, session, org_id, env_id, api_id)
    async def get_tiers_async(self, session, org_id, env_id, api_id)
```

### 3.2 CloudHubClient
```python
class CloudHubClient:
    def __init__(self, token, environments)
    async def get_applications()
    async def fetch_env_applications(session, env)
```

### 3.3 APIManagerService
```python
class APIManagerService:
    def __init__(self, api_manager_client, file_output, output_config)
    async def get_api_manager_info()
    async def _get_applications()
    async def _fetch_api_details(self, applications)
    def _organize_api_details(self, applications, results)
    def _integrate_api_details(self, applications, api_details)
    def _integrate_single_api_details(self, api, api_id, api_details)
    async def _output_api_manager_info(self, applications)
```

### 3.4 CloudHubService
```python
class CloudHubService:
    def __init__(self, cloudhub_client, file_output, output_config)
    async def get_cloudhub_info()
```