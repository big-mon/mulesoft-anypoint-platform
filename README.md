# Anypoint Platform Client

MuleSoft の Anypoint Platform API を使用してアプリケーション情報を取得する Python プログラムです。API Manager や CloudHub の情報を非同期で効率的に取得し、JSON形式で出力します。

## 概要

このツールは以下のような場合に便利です：

- Anypoint Platform の API 情報を一括で取得したい場合
- CloudHub のアプリケーション情報を環境横断で取得したい場合
- 取得した情報を構造化されたJSONとして保存したい場合

## 機能

### API Manager 情報取得
- アプリケーション一覧
- ポリシー設定
- Contracts 情報
- アラート情報
- ティア情報

### CloudHub 情報取得
- アプリケーション一覧
- デプロイメント情報
- ステータス情報

### その他の特徴
- 非同期処理による高速な情報取得
- 柔軟な出力設定
- エラーハンドリング

## 必要な環境

- Python 3.8以上
- 必要なライブラリ
  - requests
  - aiohttp
  - python-dotenv

## インストール方法

1. リポジトリのクローン

```bash
git clone https://github.com/big-mon/mulesoft-anypoint-platform.git
cd mulesoft-anypoint-platform
```

2. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

3. 環境変数の設定

```bash
cp .env.example .env
```

`.env`ファイルを編集し、以下の情報を設定してください：

- `ANYPOINT_CLIENT_ID`: Anypoint Platform の Client ID
- `ANYPOINT_CLIENT_SECRET`: Anypoint Platform の Client Secret
- `ANYPOINT_ORGANIZATION_ID`: 組織 ID
- `ANYPOINT_BASE_URL`: Anypoint Platform の Base URL（オプション）

4. 出力設定

`output_config.env`ファイルで、各種情報の出力要否や出力ファイル名を設定できます。

## 使用方法

### 基本的な使用方法

```bash
python src/main.py
```

### 出力ファイル

実行すると、以下のファイルが `output/YYYYMMDD_HHMM/` ディレクトリに出力されます：

- `api_manager.json`: API Manager の情報
- `cloudhub.json`: CloudHub の情報

## トラブルシューティング

### よくあるエラー

1. 認証エラー
   - Client ID、Client Secret、Organization ID が正しく設定されているか確認してください

2. ネットワークエラー
   - Anypoint Platform への接続が可能か確認してください
   - プロキシ設定が必要な場合は環境変数で設定してください

## 開発者向け情報

### テスト

```bash
python -m pytest tests/
```

### コーディング規約

- PEP 8 に準拠
- Type hints の使用を推奨
- Docstring は Google スタイルを使用

## コントリビューション

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'add: some amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. Pull Request を作成

## バグ報告・機能要望

バグを発見した場合や新機能の要望がある場合は、GitHubのIssueに登録してください。

## 更新履歴

詳細な更新履歴は[CHANGELOG.md](CHANGELOG.md)を参照してください。

## ライセンス

MIT License