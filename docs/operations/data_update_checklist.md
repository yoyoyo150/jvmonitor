# データ更新チェックリスト

Excel 由来データを `excel_data.db` に取り込み、`JVMonitor.exe` で共有する際の基本フローです。作業担当者は更新毎にこのチェックリストを辿ってください。

## 1. 事前準備
- `yDate` フォルダに新しい Excel を配置し、ファイル名の先頭 8 桁が開催日になっているか確認。
- 追加・修正したファイル名を `excel_data.db` の `HORSE_MARKS.SourceFile` と照合し、必要に応じて対象日の既存レコードを削除する（上書きモードの場合）。
- 取り込み前に `docs/README.md` に記載の説明資料を最新化したか確認。

## 2. 取り込み実行
- `envs/cursor/my_keiba/JVMonitor/JVMonitor/bin/Debug/net6.0-windows` を作業ディレクトリとし、`enhanced_excel_import.py --mode incremental` を実行。
- 同じファイルを入れ替えた場合は `--mode full` で再投入し、対象日の行を一括でリフレッシュする。
- 実行ログを確認し、エラーが無いか／取り込んだ件数が想定通りかを記録。

## 3. 取り込み後
- `excel_data.db` を開き、`SELECT MAX(SourceDate), COUNT(*) FROM HORSE_MARKS` で最新日付と総件数を控える。
- JVMonitor を再起動し、対象開催の馬詳細画面で馬印・朝オッズが反映されているか目視確認。
- 新しい資料や気付きがあれば `yDate/現状確認.txt` または `docs/` 配下に追記。

## 4. 共有・配布
- 配布用フォルダに `JVMonitor.exe`, `JVMonitor.dll`, `excel_data.db`, `docs/` をまとめ、検証済みの日時と担当者を `release_notes.txt` に記載。
- チャット等で「更新日／対象開催／チェック済み担当者」を通知し、共有メンバーに参照を促す。
- Git ローカルリポジトリにコミットしておき、必要になった時点で履歴を遡れる状態を維持。
