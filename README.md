# Anypoint Platform Client

MuleSoft の Anypoint Platform API を使用してアプリケーション情報を取得する Python プログラム

## 機能

- API Manager からアプリケーション情報取得
  - アプリケーション一覧
  - ポリシー設定
  - Contracts 情報
  - アラート情報
  - ティア情報
- CloudHub からアプリケーション情報取得
- 非同期処理による高速な情報取得
- 柔軟な出力設定

## 必要な環境

- Python 3.x
- requests, aiohttp ライブラリ

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

4. 出力設定の設定

`output_config.env`ファイルで、各種情報の出力要否や出力ファイル名を設定できます。

## 使用方法

```bash
python src/main.py
```

## ライセンス

MIT License
