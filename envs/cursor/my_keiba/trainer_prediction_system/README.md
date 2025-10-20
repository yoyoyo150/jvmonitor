# 調教師予想システム

## 概要
調教師の成績分析と予想候補生成を行うシステムです。JVMonitorとの連携により、一定のクオリティを保証します。

## システム構成
```
trainer_prediction_system/
├── config/
│   └── trainer_prediction_config.json  # 設定ファイル
├── src/
│   ├── database_manager.py             # データベース管理
│   └── trainer_prediction_system.py    # メインシステム
├── outputs/                            # 出力ファイル
├── logs/                               # ログファイル
└── run_analysis.py                     # 実行スクリプト
```

## 主要機能

### 1. データベース管理
- 統一されたデータベース参照（N_UMA_RACEテーブル）
- データ品質検証
- エラーハンドリング

### 2. 調教師成績分析
- 着順率計算
- 勝率・連対率・複勝率の算出
- 統計データの生成

### 3. 予想候補生成
- 高成績調教師の選定
- スコアリングシステム
- 候補ランキング

### 4. JVMonitor連携
- 期待値との比較
- 許容範囲内での検証
- 品質レポート生成

## 使用方法

### 基本実行
```bash
python run_analysis.py
```

### 設定変更
`config/trainer_prediction_config.json`を編集して設定を変更できます。

## 設定項目

### データベース設定
- `db_path`: データベースファイルパス
- `primary_table`: メインテーブル（N_UMA_RACE）
- `trainer_column`: 調教師カラム名

### 分析設定
- `date_range`: 分析期間
- `trainer_criteria`: 調教師選定条件
- `course_type_filter`: コースタイプフィルタ

### 品質管理
- `data_validation`: データ検証設定
- `result_validation`: 結果検証設定
- `jvmonitor_alignment`: JVMonitor連携設定

## 出力ファイル

### CSVファイル
- `trainer_analysis_YYYYMMDD_HHMMSS.csv`: 調教師分析結果
- `candidates_YYYYMMDD_HHMMSS.csv`: 予想候補

### JSONファイル
- `trainer_analysis_YYYYMMDD_HHMMSS.json`: 分析結果（JSON形式）
- `quality_report_YYYYMMDD_HHMMSS.json`: 品質レポート

### ログファイル
- `trainer_prediction_YYYYMMDD.log`: 実行ログ

## 品質管理

### データ品質検証
- 必須カラムの存在確認
- 空値チェック
- 着順データの妥当性確認

### 結果品質検証
- 調教師数の範囲チェック
- 着順率の妥当性確認
- JVMonitor連携検証

### エラーハンドリング
- データベース接続エラー
- データ品質エラー
- 分析処理エラー

## トラブルシューティング

### よくある問題
1. **データベース接続エラー**: データベースファイルパスを確認
2. **データ品質エラー**: データの整合性を確認
3. **JVMonitor連携エラー**: 期待値と実際の値の差を確認

### ログ確認
ログファイルでエラーの詳細を確認できます。

## バージョン情報
- バージョン: 1.0.0
- 作成日: 2025-10-01
- 最終更新: 2025-10-01

## ライセンス
このシステムは内部使用目的で作成されています。




