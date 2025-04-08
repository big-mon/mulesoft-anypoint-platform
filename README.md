# Anypoint Platform Client

MuleSoft の Anypoint Platform API を使用してアプリケーション情報を取得する Python プログラム

## 機能

- API Manager からアプリケーション情報取得
- Runtime Manager からアプリケーション情報取得
- PyPy 互換の実装

## 必要な環境

- Python 3.x
- PyPy
- requests ライブラリ

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
- `ANYPOINT_ORGANIZATION_ID`: 組織ID
- `ANYPOINT_ENVIRONMENT_ID`: 環境ID

## 使用方法

```bash
python src/main.py
```

## ライセンス

MIT License
