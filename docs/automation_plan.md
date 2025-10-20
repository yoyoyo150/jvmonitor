# Automation Plan (CURSOR Agent Workflow)

このドキュメントは、CURSOR のエージェント機能を使って予想パイプラインを半自動化するための手順をまとめたものです。手動での実行にも利用できます。

---

## 1. 前提

- リポジトリルートで Python が利用可能（`requirements.txt` をインストール済み）。
- `envs/cursor/my_keiba/ecore.db`（公式データ）と `excel_data.db`（馬印データ）が更新されていること。
- `predictions.db` は `python -m ml.db.create_predictions_db` で初期化済み。
- モデルは `ml/model_artifacts/` に配置（例: `win-YYYYMMDDHHMMSS.joblib`）。

---

## 2. 日次フロー（前日予想）

1. **最新データを取り込む**  
   - JVMonitor 経由で `ecore.db` を更新。  
   - 必要に応じて馬印を `excel_data.db` にインポート。

2. **予想を生成（シナリオ PRE）**  
```powershell
python -m ml.predict_today --date 2025-10-13 --scenario PRE
```
- ランク判定は `ml/config/rank_rules.json` で管理。デフォルトでは WinScore / M5 / ZI・ZM 指数などを用いて S～E の6段階に分類し、S/A を投資対象とする（PRE シナリオではオッズは参照しない）。
- 実行後 `envs/cursor/my_keiba/predictions.db` に結果が追記/更新される。

3. **JVMonitor で確認**  
   - `Predictions` テーブルを `ThreePaneRaceBrowserControl` などから JOIN し、`WinScore` や `InvestFlag` を表示する。

### JVMonitor UI操作のポイント

- `対象日付` を指定して `前日予想 (PRE)` / `当日 LIVE 更新` ボタンを押すと、裏で `python -m ml.predict_today` が実行されログに反映されます。
- 予測結果には `RankGrade` 列が追加され、S/A が投資候補（ログ上では「S:***」「A:***」のように出力、S/A 行には * 印が付与）として表示されます。グリッド上では S/A を強調表示するよう調整してください。
- `結果評価` ボタンはその日のみを対象に `python -m ml.evaluation.evaluate_predictions --date-from {日付} --date-to {日付}` を実行し、下部サマリーに ROI・ヒット率を表示します。
- `期間シミュレーション` グループにある `開始日付` / `終了日付` を設定し、`期間予測` で複数日のバッチ予測、`期間評価` で一括評価が可能です。
- 期間評価は自動で JSON レポートを生成し、成功時に最新サマリーへ反映されます（ログに保存先パスが表示されます）。

---

## 3. 当日ライブ更新（オプション）

発走前にリアルタイム情報（最新オッズ、馬場発表等）を使って予想を上書きする。

```powershell
python -m ml.predict_today --date 2025-10-13 --scenario LIVE
```

`Scenario='LIVE'` で `Predictions` に追記されるため、前日予想と当日予想を比較できる。オッズ条件などは `ml/config/rank_rules.json` の LIVE セクションで調整する。

---

## 4. 運用エージェントのタスク例

1. **毎朝 4:00**  
   - `ml/predict_today.py --scenario PRE` を実行し、前日予想を作成。
2. **レース 30/15/5 分前**  
   - `--scenario LIVE` を実行して最新情報で上書き（必要なレースのみ）。オッズやランク条件は `ml/config/rank_rules.json` の LIVE セクションで調整する。
3. **日次レポート**  
   - `Predictions` と実際の着順を突合するスクリプト（今後実装予定）を走らせ、ROI/ヒット率を集計。
4. **月次メンテナンス**  
   - `ml/features/build_features.py --output ml/output/features_all.parquet`  
   - `ml/models/train_win_model.py --features ml/output/features_all.parquet`  
   - モデルバージョンを更新し、タスクで用いる `--model-version` を最新に切替える。

---

## 5. CURSOR エージェントへの指示例

1. 「データ更新済み。2025-10-13 の PRE 予想を実行して」  
   - エージェントが `python -m ml.predict_today --date 2025-10-13 --scenario PRE` を実行。
2. 「当日 LIVE 予想を実行して（必要ならランク条件も更新して）」  
   - `python -m ml.predict_today --date 2025-10-13 --scenario LIVE` を実行。閾値の変更は事前に `ml/config/rank_rules.json` の LIVE セクションを編集する。
3. 「最新モデルに更新して」  
   - `ml/features/build_features.py --output ...` → `ml/models/train_win_model.py --model-version ...` を順番に実行する指示を書く。
4. 「JVMonitor で 2025-10-10〜2025-10-13 をシミュレーションして評価まで実施して」  
   - エージェントへの操作例: 予測パネルを開く → `開始日付=2025-10-10` / `終了日付=2025-10-13` に設定 → `期間予測` → `期間評価` の順にクリックし、ログとサマリーの結果を報告させる。

---

## 6. 補足

- `ml/predict_today.py` は内部で `build_feature_frame` を呼び出すので、事前にパーケットを作る必要はありません。  
- 投資判定ロジックは `ml/config/rank_rules.json` で調整できる（PRE シナリオはオッズを参照せず、S/A ランクが投資対象）。
- エージェント実行時はリポジトリルートで `python -m ...` を実行するようにします。  
- ログが必要な場合は `--logfile` オプションを追加した派生スクリプトを用意してください。
---

## 7. 予想結果の突合・評価

1. **評価スクリプトの実行**  
   ```powershell
   python -m ml.evaluation.evaluate_predictions --date-from 2025-10-12 --date-to 2025-10-13 --scenario PRE
   ```
   - `envs/cursor/my_keiba/predictions.db` と `ecore.db` を JOIN し、的中率と ROI を算出。
   - `--output-json reports/pred_eval.json` のように指定すると JSON で保存します。

2. **CURSOR エージェントへの指示例**  
   - 「2025-10-12〜13 の PRE 予想を評価して JSON で保存して」  
     `python -m ml.evaluation.evaluate_predictions --date-from 2025-10-12 --date-to 2025-10-13 --scenario PRE --output-json reports/pred_eval.json`

3. **注意点**  
   - ROI は `Predictions` に保存されたオッズを用いた概算です。公式払戻データが取得できる場合はスクリプトを拡張してください。

## 8. ランク調整と分析

- ランク閾値を調整する前に、以下のコマンドで期間別の成績を把握してください。
  ```powershell
  python -m ml.evaluation.analyze_rank_metrics --date-from 2025-10-01 --date-to 2025-10-13 --scenario PRE --output-csv reports/rank_summary.csv
  ```
  - 各ランクの件数・的中率・ROI が表示され、`reports/rank_summary.csv` にも出力されます。
- PRE シナリオではオッズを使わずにランク付けするため、WinScore / M5 / ZI・ZM 指数・調教師勝率などの指標を中心に調整してください。
- LIVE シナリオでは同ファイルの `max_odds` などを使って当日オッズを基準に絞り込みます。
- 閾値の調整後は、`predict_today` → `analyze_rank_metrics` → `evaluate_predictions` の順に検証サイクルを回すと、前日予想の改善具合を素早く把握できます。

- 評価結果には Invest grade breakdown が含まれ、各ランクごとの件数・的中率を確認できます。
