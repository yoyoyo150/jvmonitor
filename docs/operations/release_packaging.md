# 開発環境パッケージング手順

仲間内に JVMonitor の開発環境を配布する際は、以下の手順でコードとドキュメントのみをまとめたバンドルを作成してください。大容量のデータベース (`ecore.db`, `excel_data.db` など) や Excel 原本は含まれません。

## 事前確認
- `excel_data.db` や `ecore.db` を更新した直後であれば、内容を別途共有するか、受け取る側が再生成できるように案内しておく。
- 直近の変更を Git ローカルでコミットしておき、バンドル生成後に差分が分かる状態を保つ。

## バンドルの作成
1. PowerShell を開き、リポジトリ直下 (`C:\my_project_folder`) で以下を実行:
   ```powershell
   pwsh -File envs/cursor/my_keiba/tools/create_dev_bundle.ps1 -Zip
   ```
   - `-Zip` を付けると `dist/` 配下に ZIP ファイルが生成されます。
   - `-OutputRoot` を指定すると出力場所を変えられます。
2. スクリプトは次を自動で行います:
   - `envs/cursor/my_keiba/` 全体をコピーし、DB (`*.db`, `*.sqlite*`) や Excel (`*.xlsx`) を削除
   - `docs/` フォルダをコピーし、最新の索引やチェックリストを同梱
   - 除外したファイル/ディレクトリの一覧を `bundle_manifest.txt` に出力

## 配布時の注意
- 受け取る側は `docs/README.md` から参照を開始し、必要な DB や Excel を自前で用意してもらう。
- 実データを共有する場合は暗号化付きの別チャネルで渡し、このバンドルとは明確に分ける。
- バンドル生成後、`dist/JVMonitorDevBundle_YYYYMMDD_HHMM` 以下の内容を確認し、不要物が混ざっていないか目視チェックを行う。

## 関連ドキュメント
- [データ更新チェックリスト](data_update_checklist.md)
- [レース印・馬印の説明](../../envs/cursor/my_keiba/yDate/レース印・馬印の説明.md)
- [競馬予想理論（修正版）](../../envs/cursor/my_keiba/予想理論_修正版.md)

