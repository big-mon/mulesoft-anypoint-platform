# 要件メモ

## 1. 目的

MuleSoft Anypoint Platform の API Manager API と Runtime Manager API を利用し、環境ごとの情報を取得して JSON として保存する。

## 2. 取得対象

### API Manager

- API 一覧
- Policies
- Contracts
- Alerts
- Tiers

### Runtime Manager

- アプリケーション一覧
- デプロイメント関連情報
- 実行ステータス

## 3. 出力要件

- API Manager と Runtime Manager は別ファイルで出力する
- それぞれ取得できる全量を保持する
- 出力形式は JSON
- 出力先は `output/YYYYMMDD_HHMM/`

出力ファイル:

- `api_manager.json`
- `cloudhub.json`

## 4. 実装方針

- 処理は出力物単位で分ける
- 各処理は `取得 -> 整形 -> 出力` を基本フローとする
- 過剰なレイヤー分割は行わない
- 共通化は認証、環境一覧取得、出力処理に限定する
- API Manager と Runtime Manager の情報は統合しない

## 5. 非機能要件

- 複数環境の取得は非同期で行う
- 取得失敗時はエラー内容を標準出力へ表示する
- 出力有無とファイル名は `config/output_config.env` で切り替えられる

## 6. テスト観点

- API Manager
  - 一覧取得結果の整形
  - 詳細情報の反映
  - API 0 件時の出力
  - 詳細情報が空のときの出力
- Runtime Manager
  - 環境ごとの取得結果整形
  - 出力無効時の挙動
- 共通
  - 出力設定の読み込み
  - JSON ファイル出力
