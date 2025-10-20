# 予想システム自動化ガイド

## 毎回の実行前チェックリスト

### 1. データ整合性チェック (必須)
```bash
python ml/data_integrity_check.py
```
- ✅ 全ての予想データが実際のレースと整合していることを確認
- ❌ 無効な予想が0件であることを確認

### 2. 予想実行
```bash
python -m ml.predict_today --date YYYY-MM-DD --scenario PRE
```
- 実行前に必ず上記の整合性チェックを実行
- 存在しない日付の場合は警告が表示される

### 3. 予想結果確認
```bash
python -m ml.evaluation.evaluate_predictions --date-from YYYY-MM-DD --date-to YYYY-MM-DD --scenario PRE
```

## 自動化されている安全機能

### predict_today.py の安全機能
- ✅ レースデータ存在チェック
- ✅ 出走馬データ存在チェック  
- ✅ データ0件時の自動停止
- ✅ 警告メッセージ出力

### data_integrity_check.py の機能
- ✅ 予想データと実際のレースデータの整合性チェック
- ✅ 無効な予想の検出と報告
- ✅ 全体的な整合性レポート

## 問題発生時の対処

### 架空データが生成された場合
1. `python cleanup_predictions.py` でデータクリーンアップ
2. `python ml/data_integrity_check.py` で整合性確認
3. 正しい日付で予想を再実行

### データベースエラーの場合
1. データベースファイルの存在確認
2. パス設定の確認 (appsettings.json)
3. 権限の確認

## 定期メンテナンス

### 週次
- 予想データの整合性チェック
- 古い予想データのクリーンアップ

### 月次  
- データベースの最適化
- バックアップの確認

## 緊急時の連絡先
- システム管理者: [連絡先]
- 技術サポート: [連絡先]
