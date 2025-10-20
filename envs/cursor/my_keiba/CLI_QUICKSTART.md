# my_keiba CLI クイックスタート

`cli.py` は依存なし（argparse）のシンプルな CLI です。まずはこの土台で運用できます。

- 実行: `python cli.py <サブコマンド> [オプション]`
- ヘルプ: `python cli.py --help` / `python cli.py <サブコマンド> --help`
- ログ: `-v` で詳細表示、`-q` で非エラー出力を抑制

## 主なサブコマンド

### export（エクスポート）
JVLink 由来の SQLite からエントリをエクスポートします（外部スクリプトに委譲）。

- 既定ハンドラ: `export_entries_from_jvlink_sqlite.py`
- 代替フォールバック: `output/logic/db_today_check_and_export.py`
- 配置場所が異なる場合: `--script-path <スクリプトへのパス>` を指定

使用例:
- `python cli.py export --db race.db --from 20240901 --to 20240914 --outdir output/exports`
- `python cli.py export --db race.db --tables RACE HORSE --format csv`

### predict（予測実行）
予測エンジンを実行し、JSON 出力を生成します（共通オプションはハンドラにフォワード）。

- エンジン指定:
  - `--engine pass` → `no_odds_box3_plus.py`（リポジトリ外にある場合は `--script-path` を指定）
  - `--engine bloodline` → `bloodline_box3.py`（`output/logic` で自動検出）

使用例:
- `python cli.py predict --engine bloodline --date 20240914 --outdir output/preds`
- `python cli.py predict --engine pass --db race.db --config prediction_config.json --outdir output/preds --script-path D:\tools\no_odds_box3_plus.py`

### txt（TXT 生成）
予測 JSON から TXT を生成します（外部スクリプトに委譲）。

- 既定ハンドラ: `json_to_txt.py`
- 代替フォールバック: `scripts/generate_box3_txt.py`

使用例:
- `python cli.py txt --input output/preds --outdir output/txt`

### validate（JSON 検証・内蔵）
予測 JSON の構造を検証します（内蔵実装）。既定ルールは以下です。

- 1レースあたり `patterns` が 3 件
- 各 `pattern` は `horses` を 4 頭（既定は重複不可）
- `total` があれば、`horses[*].score` の合計とおおむね一致（±1e-6）

使用例:
- `python cli.py validate --input output/preds --recursive`
- キー名が異なる場合: `--pattern-key candidates --horses-key ids --total-key sum --score-key s`

終了コード: すべて合格で `0`、不合格が含まれる場合は `3`

### eval（簡易 ROI 評価・内蔵）
ワイド BOX（簡易）の ROI を概算します。結果 CSV は少なくとも `race_id,payout` を持つ想定です。

- 予測 JSON の各レースで `patterns[0].horses` を BOX 対象とみなします（4頭なら 6 点）。
- ステーク（1点あたり掛金）は `--stake`（既定 100）。

使用例:
- `python cli.py eval --pred output/preds --results-csv data/results_min.csv --stake 100`

## ハンドラ検出について
CLI は以下のディレクトリを優先的に探索します：`./`、`scripts/`、`src/`、`output/logic/`、`CollectorV2/`。
見つからない場合は `--script-path` で直接パスを指定してください。

## 典型フロー（例）
1. エクスポート: `python cli.py export --db race.db --from 20240901 --to 20240914 --outdir output/exports`
2. 予測: `python cli.py predict --engine bloodline --date 20240914 --outdir output/preds`
3. 検証: `python cli.py validate --input output/preds --recursive`
4. TXT 化: `python cli.py txt --input output/preds --outdir output/txt`
5. 評価: `python cli.py eval --pred output/preds --results-csv data/results_min.csv --stake 100`

## 1) DB → CSV（RA/SE 自動JOIN）
RA（レース情報）と SE（払戻などの結果情報）を 1 ファイルにまとめて CSV 出力する例です。

用語対応（NL スキーマ）
- RA = `NL_RA_RACE`
- SE = `NL_SE_RACE_UMA`

- 分割エクスポート（RA/SE をそれぞれ CSV 化）
  - `python cli.py export --db race.db --tables NL_RA_RACE NL_SE_RACE_UMA --format csv --outdir output/exports`

- ハンドラが JOIN 機能を持つ場合（パススルーで指示）
  - `python cli.py export --db race.db --format csv --outdir output/exports -- --join NL_RA_RACE,NL_SE_RACE_UMA --on race_id --output ra_se.csv`
  - 備考: `--` 以降はハンドラにそのまま渡ります（CLI は解釈しません）。

- 直接 SQL で JOIN（SQLite をそのまま参照）
  - 例（PowerShell）: 下記を `scripts/join_ra_se.py` として保存して実行
    - `python scripts/join_ra_se.py --db race.db --out output/exports/ra_se.csv`
  - サンプル実装（キー名は環境に合わせて調整）:
    ```python
    # scripts/join_ra_se.py
    import argparse, csv, sqlite3
    p = argparse.ArgumentParser(); p.add_argument('--db', required=True); p.add_argument('--out', required=True)
    a = p.parse_args()
    con = sqlite3.connect(a.db)
    # 例: RA と SE を race_id（仮）で内部結合。必要に応じて列名を変更してください。
    sql = '''
    SELECT RA.race_id, RA.jyo, RA.date, RA.name,
           SE.payout, SE.odds
      FROM RA
      JOIN SE USING (race_id)
    '''
    cur = con.execute(sql)
    cols = [d[0] for d in cur.description]
    with open(a.out, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(cols); w.writerows(cur)
    ```
  - スキーマが異なる場合（例: `RaceKey` 等で結合）:
    - `JOIN SE ON RA.RaceKey = SE.RaceKey`
    - 必要に応じて列名・キー名を差し替えてください。

### 日付・モード指定の例（ハンドラ依存）
ハンドラ側で `--date` や `--mode both` などのオプションを受ける場合は、そのまま渡せます（CLI が自動でパススルー）。

- 例: `python cli.py export --db C:\path\to\race.db --date 20250914 --mode both --outdir .`

#### 場を絞る例（passモード・通過順位＋上がり用エントリCSV）
場を中山・阪神に絞って、pass エンジン向けのエントリCSVを出力する例です。

- 実行:
  - `python cli.py export --db C:\path\to\race.db --date 20250914 --mode pass --outdir . --tracks 中山 阪神`
- 出力（例）:
  - `entries_today.csv`
  - 列: `date, track, race, horse_id, field_size, pass_1c, pass_2c, agari_rank`
  - 備考: 列名・並びはハンドラ仕様に準拠します。

## 2) 予想JSON生成（通過順位＋上がり）
通過順位・上がり（いわゆる「上がり3F」）ベースのロジックで予想 JSON を生成します。既定では以下のハンドラに委譲します。

- `--engine pass` → `no_odds_box3_plus.py`（リポジトリ外にある場合は `--script-path` を指定）
- `--engine bloodline` → `bloodline_box3.py`（`output/logic` で自動検出）

基本例（通過順位＋上がり・日付指定）
- `python cli.py predict --engine pass --date 20250914 --outdir output/preds`

DB を指定する場合（必要に応じて）
- `python cli.py predict --engine pass --db C:\path\to\race.db --date 20250914 --outdir output\preds`

ハンドラ固有の詳細パラメータ（例: パターン数や上位頭数など）は、そのまま追記すれば渡せます。
- 例: `python cli.py predict --engine pass --date 20250914 --outdir output\preds -- --topn 4 --patterns 3`
- 備考: `--` は明示的な区切りとして有効ですが、CLI は未知のフラグを自動転送するため省略も可能です。

生成物の検証（推奨）
- `python cli.py validate --input output/preds --recursive`

エントリCSVを直接指定する例（ハンドラへそのまま転送）
- `python cli.py predict --engine pass --entries entries_today.csv --config prediction_config_min.json --date 20250914 --out box3_20250914.json`
- 備考: `--entries` や `--out` は CLI では解釈せず、ハンドラ（no_odds_box3_plus.py）にそのまま渡されます。

## 2') 予想JSON生成（血統ファースト）
血統重視のロジックで予想 JSON を生成します。

- 対応エンジン: `--engine bloodline` → `bloodline_box3.py`（`output/logic` で自動検出）

基本例（血統ファースト）
- `python cli.py predict --engine bloodline --date 20250914 --outdir output/preds_bloodline`

エントリCSVを指定する例（ハンドラに依存）
- `python cli.py predict --engine bloodline --entries entries_today.csv --date 20250914 --out bloodline_box3_20250914.json`

設定ファイルを併用する例
- `python cli.py predict --engine bloodline --config prediction_config.json --date 20250914 --outdir output/preds_bloodline`

生成物の検証（推奨）
- `python cli.py validate --input output/preds_bloodline --recursive`

エントリCSV＋血統統計CSVを併用する例（そのままハンドラに転送）
- `python cli.py predict --engine bloodline --entries entries_bloodline.csv --blood-stats bloodline_stats.csv --config bloodline_config.json --date 20250914 --out box3_20250914.json`

備考: `--entries` や `--blood-stats`、`--out` 等は CLI では解釈せず、`bloodline_box3.py` にそのまま渡されます。

入力ファイル（必須列）
- blood: `entries_bloodline.csv`
  - 列: `date, track, race, horse_id, surface, distance, sire, damsire`
  - 任意列: `sire_line, damsire_line`（あればニック判定に利用）
  - 注意: `track` の表記は `bloodline_stats.csv` の `track` 列と整合させてください（例: 「阪神」or内部コード）。

## 3) 人間確認用にTXT化
JSON の予想結果を、人的レビューしやすい TXT 形式に変換します（外部コンバータに委譲）。

- 既定ハンドラ: `json_to_txt.py`
- 代替フォールバック: `scripts/generate_box3_txt.py`

基本例（ディレクトリ一括変換）
- `python cli.py txt --input output/preds --outdir output/txt`

単一ファイルの変換
- `python cli.py txt --input box3_20250914.json --out box3_20250914.txt`

ハンドラ固有の出力調整（例: フォーマット/並び順など）は未知オプションとして転送可能
- 例: `python cli.py txt --input output/preds --outdir output/txt -- --fmt wide --sort odds`
- 備考: `--` 以降はハンドラへ直渡し（`--` 省略でも未知フラグは転送されます）。

## 4) JSON の構造検証
予想 JSON の構造や値の基本整合性を検証します（内蔵機能）。

- 基本: `python cli.py validate --input output/preds --recursive`
- 単一ファイル: `python cli.py validate --input box3_20250914.json`
- サイレント（終了コードのみ確認）: `python cli.py validate --input output/preds -q`
- キー名が異なる場合の例:
  - `python cli.py validate --input output/preds --pattern-key candidates --horses-key ids --total-key sum --score-key s`

検証内容（既定）
- 1レースあたり `patterns` が 3 件存在
- 各 `pattern` に `horses` が 4 頭（重複なし）
- `total` が存在する場合、`horses[*].score` の合計とほぼ一致（±1e-6）

終了コード
- 0: 全ファイルが合格（かつ 1 件以上の検証対象がある）
- 3: 失敗が含まれる、または検証対象が見つからない

## 5) （任意）ワイドBOXのざっくり評価
内蔵の簡易評価で ROI を概算します。予測 JSON と結果 CSV（少なくとも `race_id,payout`）を入力に、
BOX（`patterns[0].horses` を採用）でのワイド想定の掛け金・払戻・ROI を表示します。

使用例（ディレクトリ一括）
- `python cli.py eval --pred output/preds --results-csv data/results_min.csv --stake 100`

単一 JSON の評価例
- `python cli.py eval --pred box3_20250914.json --results-csv results_20250914.csv --stake 100`

エイリアス・定数払戻の例（ご指定の形）
- `python cli.py eval --pred box3_20250914.json --truth results.csv --stake 100 --payout 300`
  - `--truth` は `--results-csv` のエイリアスです。
  - `--payout 300` を指定すると、的中1件あたり 300 円の固定払戻として集計します（CSVの金額を無視）。
  - CSV の `race_id` 列名が異なる場合は `--id-column`、払戻列名が異なる場合は `--payout-column` を指定してください。

出力例（概略）
- `Races: 25, Wins: 9, Stake: 6000, Return: 7350, ROI: 1.225`

前提・注意
- 1レースの選択は最初のパターン `patterns[0].horses` を採用（4頭なら 6 組み合わせ）。
- 掛け金は「1点あたり `--stake` 円 × 組み合わせ数」。
- 結果 CSV はレースごとに 1 行、`payout` はその BOX 選択に該当するワイドの合計払戻を入れてください。
  - レース内に複数の的中があり CSV が明細行で分かれる場合は、事前にレース単位で合算してください。
- 返還・締切や重複購入の扱い、控除・手数料などは考慮しない簡易評価です。
## 補足
- JSON スキーマが異なる場合は検証用オプションで合わせてください。
- 将来的に `--lang {en,ja}` によるメッセージの多言語化を検討しています（必要になった段階で最小差分で追加可能）。

## 既存 CLI について
以前の CLI は `cli_legacy.py` としてリポジトリ直下にバックアップ済みです。
