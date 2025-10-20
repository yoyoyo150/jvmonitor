# JVMonitor ドキュメント索引

## 1. 目的
JVMonitor/Excel 連携の基本情報と、仲間内で共有する際のルールをここから辿れるようにします。まず本ページを確認し、その後リンク先の詳細資料へ進んでください。

## 2. データ構成の概要
- `envs/cursor/my_keiba/ecore.db` … JRA-VAN から取り込んだメインデータベース（番組・成績などの外殻）
- `envs/cursor/my_keiba/excel_data.db` … `yDate` 配下の Excel からインポートした補完情報（馬印・朝オッズなど）
- `envs/cursor/my_keiba/yDate/` … Excel 原本の置き場。取り込み済みかどうかは `HORSE_MARKS.SourceFile` で管理します。

## 3. 参照ドキュメント
- [レース印・馬印の説明](../envs/cursor/my_keiba/yDate/レース印・馬印の説明.md)
- [競馬予想理論（修正版）](../envs/cursor/my_keiba/予想理論_修正版.md)
- [運用フローとチェックリスト](operations/data_update_checklist.md)

## 4. 実行ツール
- WinForms アプリ `envs/cursor/my_keiba/JVMonitor/JVMonitor/bin/Debug/net6.0-windows/JVMonitor.exe`
- Excel 取り込みスクリプト `envs/cursor/my_keiba/JVMonitor/JVMonitor/fix_excel_data_import.py`（配布時は `bin/.../enhanced_excel_import.py` を同梱）

## 5. 更新履歴
- 2025-10-04: 初版作成。Excel 連携の説明資料と運用フローを索引化。
