# 競馬データ取得・分析システム

## 基本方針
**「計画→確認→実行→要約→次の候補」を徹底**

このプロジェクトでは、Codex (Cursor) エージェントとの対話において、常に確認を取ってから実行することを基本とします。

## 対話式運用ルール

### 1. 計画表示
- 実行前に必ず計画を表示
- 影響範囲とリスクを明示
- 複数ステップの場合は全体像を説明

### 2. 確認プロンプト
- 計画を理解した上で Yes/No を確認
- リスクがある場合は特に注意喚起
- ユーザーが理解できない場合は説明を追加

### 3. 実行
- 承認後に実行
- 進捗を適切に報告
- エラーが発生した場合は即座に停止

### 4. 要約
- 実行結果を簡潔に要約
- 次に必要なアクションがあれば提示
- 問題があれば対処法を提案

### 5. 次の候補
- 関連する次のステップを提案
- ユーザーの意図に沿った選択肢を提示

## 初期化コマンド

### `/init`
AGENTS.mdを参照して対話フローに切り替え

### `/approvals`
APPROVALS.mdの方針で自動許可の範囲を設定

## システム構成

### 主要コンポーネント
- **JVMonitor**: C# WinForms アプリケーション（メインUI）
- **JVLinkToSQLite**: JV-LinkデータをSQLiteに変換
- **Pythonスクリプト群**: データ処理・予想生成
- **CLI**: コマンドラインインターフェース

### データフロー
1. JV-Linkデータ取得
2. SQLiteデータベース変換
3. エクセルファイル読み込み（オッズ・脚質データ）
4. 予想生成（血統ベース・オッズベース）
5. 結果出力（JSON・TXT）

## 使用方法

### CLI使用例

#### 通常の使用（確認プロンプト付き）
```bash
# データエクスポート（計画表示→確認→実行）
python cli.py export --db race.db --date 20250914 --mode both --outdir .

# 予想実行（計画表示→確認→実行）
python cli.py predict --engine bloodline --entries entries_today.csv --config prediction_config.json --date 20250914 --out box3_20250914.json
```

#### 自動承認モード
```bash
# 全部自動承認（CI向け）
python cli.py --yes predict --engine pass --entries entries_today.csv --config prediction_config_min.json --date 20250914 --out box3_20250914.json

# 確認を出さない
python cli.py --no-interactive export --db race.db --date 20250914
```

#### 対話モード（ウィザード）
```bash
# 完全対話モード - ガイド付きで操作選択
python cli.py wizard

# ウィザードでデフォルト値を指定
python cli.py wizard --db C:\path\race.db --date 20250914
```

#### 環境変数による動作制御
```bash
# 既定で確認ON（全コマンドで確認プロンプト表示）
set CLI_INTERACTIVE=1
python cli.py export --db race.db --date 20250914
```

### 環境変数
```bash
# 既定で確認ON（全コマンドで確認プロンプト表示）
set CLI_INTERACTIVE=1

# 確認を無効化（CI環境など）
set CLI_INTERACTIVE=0
```

## ファイル構成

### 設定ファイル
- `AGENTS.md`: Codexエージェント運用ルール
- `APPROVALS.md`: 自動許可範囲設定
- `prediction_config.json`: 予想設定
- `bloodline_config.json`: 血統設定

### データベース
- `race.db`: メインデータベース（JV-Linkデータ）
- `excel_race_data.db`: エクセルデータベース（オッズ・脚質）

### 出力ファイル
- `output/`: 予想結果・ログファイル
- `output/logic/`: Pythonスクリプト
- `output/box3_*.txt`: BOX×3予想結果

## 開発・運用

### 安全第一の原則
- 変更系操作は必ず確認
- バックアップを取ってから実行
- エラー時は即座に停止
- 復旧手順を事前に準備

### 確認が必要な操作
- ファイル・ディレクトリの作成・削除・変更
- データベースの変更
- システム設定の変更
- 外部ツールの実行

### 自動許可される操作
- ファイル・ディレクトリの読み取り
- 情報収集系のコマンド
- データベースの読み取り

## トラブルシューティング

### よくある問題
1. **パスエラー**: 相対パス・絶対パスの確認
2. **権限エラー**: 管理者権限での実行
3. **ファイルロック**: プロセスの終了確認
4. **データベースエラー**: 接続・テーブル構造の確認

### ログ確認
- JVMonitor: アプリケーション内ログ
- CLI: 標準出力・エラー出力
- Pythonスクリプト: 各スクリプトのログ

## ライセンス
このプロジェクトは競馬データの分析・研究目的で使用されています。

## 注意事項
- 競馬データの使用は適切な範囲内で行ってください
- 個人の責任において使用してください
- 商用利用の場合は適切なライセンスを確認してください
