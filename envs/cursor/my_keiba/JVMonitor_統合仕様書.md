# JVMonitor 統合仕様書
## JV-Linkデータ取得・表示システム完全ガイド

---

## 📋 目次
1. [システム概要](#システム概要)
2. [アーキテクチャ構成](#アーキテクチャ構成)
3. [データ取得システム](#データ取得システム)
4. [データ表示システム](#データ表示システム)
5. [JV-Linkデータ種類詳細](#jv-linkデータ種類詳細)
6. [ファイル・パス構成](#ファイルパス構成)
7. [運用フロー](#運用フロー)
8. [トラブルシューティング](#トラブルシューティング)

---

## 🎯 システム概要

### 目的
JRA-VAN Data Labから競馬データを取得し、SQLiteデータベースに保存、JVMonitorで表示・分析する統合システム

### 主要コンポーネント
- **JVLinkToSQLite**: データ取得・変換エンジン
- **JVMonitor**: データ表示・分析アプリケーション
- **JVAcquire**: データ取得専用UIツール
- **race.db**: 統合SQLiteデータベース

---

## 🏗️ アーキテクチャ構成

### システム構成図
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   JRA-VAN       │    │  JVLinkToSQLite │    │   race.db       │
│   Data Lab      │───▶│      EXE        │───▶│   (SQLite)      │
│   (.jvd files)  │    │   (変換エンジン)  │    │   (統合DB)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   JVAcquire     │    │   JVMonitor     │
                       │  (取得UI)       │    │  (表示・分析)    │
                       └─────────────────┘    └─────────────────┘
```

### データフロー
1. **データ取得**: JVAcquire → JVLinkToSQLite → race.db
2. **データ表示**: race.db → JVMonitor → ユーザー
3. **設定管理**: appsettings.json → 全コンポーネント

---

## 🔄 データ取得システム

### 取得モード
| モード | 用途 | DataSpec | 実行頻度 |
|--------|------|----------|----------|
| **Setup** | 初期セットアップ | RACE, YSCH, HOSE, HOYU, COMM, MING | 初回のみ |
| **Normal** | 通常更新 | RACE, YSCH, HOSE, HOYU, COMM, MING | 開催日 |
| **Diff** | 差分更新 | DIFF, DIFN | リアルタイム |
| **Realtime** | オッズ取得 | O1-O6 | レース前後 |

### ✅ セットアップデータ取得成功（2025/09/08）

#### 成功した方法
**直接実行方式** - BATファイルやPowerShellスクリプトを経由せず、JVLinkToSQLiteを直接実行

```bash
JVLinkToSQLite.exe -m exec -s "Setup.xml" -d "race.db"
```

#### 実行結果
- **DBファイルサイズ**: 6,161,465,344バイト（約6.1GB）
- **最終更新時刻**: 2025/09/08 21:23:31
- **取得データ**: RACE, YSCH, HOSE, HOYU, COMM, MING（2021年～）
- **実行時間**: 約30分

#### 成功の要因
1. **テンプレートファイル使用**: `Setup.xml`テンプレートを直接指定
2. **BAT/PowerShell回避**: 中間スクリプトによるXMLパースエラーを回避
3. **適切なパス指定**: JVLinkToSQLite-0.1.2ディレクトリの実行ファイルを使用

#### 失敗していた方法との比較
- **BATファイル実行**: XMLパースエラー（KeyNotFoundException）
- **PowerShellスクリプト**: InnerTextプロパティエラー
- **setting.xml直接実行**: UM,KS,CH,BR,BNのDataSpec認識エラー

#### 今後の推奨方法
セットアップデータ取得は**直接実行方式**を使用し、BATファイルは補助的な用途に限定する。

### ✅ 差分データ取得成功（2025/09/08）

#### 成功した方法
**直接実行方式** - セットアップと同様にJVLinkToSQLiteを直接実行

```bash
JVLinkToSQLite.exe -m exec -s "Diff.xml" -d "race.db"
```

#### 実行結果
- **DBファイルサイズ**: 6,166,511,616バイト（約6.2GB）← 約5MB増加
- **最終更新時刻**: 2025/09/08 21:29:25
- **実行時間**: 約3.7秒

#### 取得されたデータ
- **DIFF**: 該当データなし（正常）
- **DIFN**: 7ファイル、合計2,473レコード取得
  - BNFW（馬主情報）: 416レコード
  - BRFW（生産者情報）: 312レコード  
  - CHFW（調教師情報）: 184レコード
  - KSFW（騎手情報）: 113レコード
  - RALW（レース情報）: 2レコード
  - SELW（レース馬情報）: 18レコード
  - UMFW（馬情報）: 1,528レコード

#### 重要な発見
1. **DIFNでUM、KS、CH、BR、BNが取得できた** - これらは差分データとして利用可能
2. **直接実行方式が有効** - セットアップと同様に成功
3. **リアルタイム更新** - 最新の差分データが正常に取得された

#### 今後の推奨方法
差分データ取得も**直接実行方式**を使用し、定期的な更新に活用する。

### 📁 本物ファイルの場所（2025/09/08確認）

#### JVLinkToSQLite.exe（本物）
- **パス**: `C:\my_project_folder\envs\cursor\my_keiba\JVLinkToSQLite-0.1.2\JVLinkToSQLiteArtifact\JVLinkToSQLite.exe`
- **サイズ**: 116,224バイト
- **最終更新**: 2025/08/10 12:39:24
- **バージョン**: 0.1.2.0
- **著作権**: Copyright (C) 2023 Akira Sugiura

#### race.db（本物）
- **パス**: `C:\my_project_folder\envs\cursor\my_keiba\JVLinkToSQLite-0.1.2\JVLinkToSQLiteArtifact\race.db`
- **サイズ**: 6,166,511,616バイト（約6.2GB）
- **最終更新**: 2025/09/08 21:29:25
- **状態**: セットアップデータ + 差分データ取得済み

#### その他のJVLinkToSQLite.exe（非推奨）
- `C:\my_project_folder\envs\cursor\my_keiba\CollectorV2\JVLinkToSQLite.exe` (116,224バイト)
- `C:\my_project_folder\envs\cursor\my_keiba\JVLinkToSQLite\JVLinkToSQLite.exe` (116,224バイト)

#### その他のrace.db（非推奨）
- `C:\my_project_folder\envs\cursor\my_keiba\race.db` (5,169,582,080バイト)
- `C:\my_project_folder\envs\cursor\my_keiba\JVAcquire\bin\Debug\net6.0-windows\race.db` (2,058,248,192バイト)
- `C:\my_project_folder\envs\cursor\my_keiba\JVMonitor\JVMonitor\bin\Debug\net6.0-windows\race.db` (57,606,144バイト)

### 実行順序
```
1. Setup (初回) → 2. Normal (開催日) → 3. Diff (継続) → 4. Realtime (必要時)
```

### JVAcquire使用方法
1. **EXE選択**: `C:\JVLinkToSQLite\JVLinkToSQLiteArtifact\JVLinkToSQLite.exe`
2. **テンプレート選択**: Diff.xml, Normal.xml, Realtime.xml, Setup.xml
3. **日付設定**: 開始日と期間(日)を指定
4. **実行**: ボタンクリックで取得開始

---

## 📊 データ表示システム

### JVMonitor機能
- **3ペイン表示**: 日付選択 → 開催・レース選択 → 出走馬表示
- **リアルタイム更新**: 差分データの自動反映
- **データ検証**: 取得データの整合性確認
- **出馬表表示**: レース詳細情報の表示

### 表示項目
#### レースヘッダー
```
20**年**月**日　第*回**競馬＊＊日目　発送時刻　**：**
**R　****（レース名）
（芝ORダートOR障害）*****ｍ
```

#### 出走馬情報
| 枠番 | 馬番 | 馬評価 | 馬名 | 騎手 | 斤量 | オッズ | 調教師 | 馬主 |
|------|------|--------|------|------|------|--------|--------|------|
| 1 | 1 | S | サンプル馬 | 武豊 | 57.0 | 3.2 | 池江泰郎 | 金子真人 |

---

## 📋 JV-Linkデータ種類詳細

### 主要データ種類
| データ種類 | 構造体名 | 説明 | 更新頻度 | 用途 |
|------------|----------|------|----------|------|
| **RA** | JV_RA_RACE | レース基本情報 | 開催日 | レース情報 |
| **SE** | JV_SE_RACE_UMA | レース結果・馬情報 | 開催日 | 出走馬・結果 |
| **O1** | JV_O1_ODDS_TANFUKUWAKU | 単勝・複勝・馬連オッズ | リアルタイム | オッズ表示 |
| **O2** | JV_O2_ODDS_UMAREN | 馬連オッズ | リアルタイム | オッズ表示 |
| **O3** | JV_O3_ODDS_WIDE | ワイドオッズ | リアルタイム | オッズ表示 |
| **O4** | JV_O4_ODDS_UMATAN | 馬単オッズ | リアルタイム | オッズ表示 |
| **O5** | JV_O5_ODDS_SANREN | 三連複オッズ | リアルタイム | オッズ表示 |
| **O6** | JV_O6_ODDS_SANRENTAN | 三連単オッズ | リアルタイム | オッズ表示 |
| **UM** | JV_UM_UMA | 馬基本情報 | 不定期 | 馬情報 |
| **KS** | JV_KS_KISYU | 騎手情報 | 不定期 | 騎手情報 |
| **CH** | JV_CH_CHOKYOSI | 調教師情報 | 不定期 | 調教師情報 |
| **BN** | JV_BN_BANUSI | 馬主情報 | 不定期 | 馬主情報 |
| **HC** | JV_HC_HANRO | 坂路調教データ | 毎日 | 調教情報 |
| **WC** | JV_WC_WOOD | ウッドチップ調教データ | 毎日 | 調教情報 |
| **JG** | JV_JG_JOGAIBA | 除外情報 | 毎日 | 除外情報 |

### ファイル命名規則
```
[データ種類][競馬場コード][年月日][作成時刻].jvd
```
例: `RAPW2025072020250717161413.jvd`

---

## 📁 ファイル・パス構成

### メインデータベース（中心）
| 項目 | パス | 説明 |
|------|------|------|
| **メインDB** | `C:\JVLinkToSQLite\JVLinkToSQLiteArtifact\race.db` | **中心となるSQLiteデータベース** |
| **メインEXE** | `C:\JVLinkToSQLite\JVLinkToSQLiteArtifact\JVLinkToSQLite.exe` | **データ取得実行ファイル** |

### プロジェクト構成
| 項目 | パス | 説明 |
|------|------|------|
| **プロジェクトルート** | `C:\my_project_folder\envs\cursor\my_keiba\` | 開発・運用の中心ディレクトリ |
| **JVMonitor** | `C:\my_project_folder\envs\cursor\my_keiba\JVMonitor\` | データ表示アプリケーション |
| **JVAcquire** | `C:\my_project_folder\envs\cursor\my_keiba\JVAcquire\` | データ取得専用アプリケーション |

### 設定ファイル（appsettings.json）
| 項目 | パス | 説明 |
|------|------|------|
| **データベース** | `C:\JVLinkToSQLite\JVLinkToSQLiteArtifact\race.db` | メインDB |
| **実行ファイル** | `C:\JVLinkToSQLite\JVLinkToSQLiteArtifact\jvlinktosqlite.exe` | 取得EXE |
| **差分設定** | `C:\my_project_folder\envs\cursor\my_keiba\diff.xml` | 差分更新用XML |
| **通常設定** | `C:\my_project_folder\envs\cursor\my_keiba\normal.xml` | 通常更新用XML |
| **リアルタイム設定** | `C:\my_project_folder\envs\cursor\my_keiba\realtime.xml` | オッズ取得用XML |
| **セットアップ設定** | `C:\my_project_folder\envs\cursor\my_keiba\setup.xml` | セットアップ用XML |

### テンプレートXML（JVAcquire用）
| 項目 | パス | 説明 |
|------|------|------|
| **Diff.xml** | `C:\my_project_folder\envs\cursor\my_keiba\JVLinkToSQLite\JVMonitor\Templates\Diff.xml` | 差分更新テンプレート |
| **Realtime.xml** | `C:\my_project_folder\envs\cursor\my_keiba\JVLinkToSQLite\JVMonitor\Templates\Realtime.xml` | オッズ取得テンプレート |
| **Normal.xml** | `C:\my_project_folder\envs\cursor\my_keiba\JVLinkToSQLite\JVMonitor\Templates\Normal.xml` | 通常更新テンプレート |
| **Setup.xml** | `C:\my_project_folder\envs\cursor\my_keiba\JVLinkToSQLite\JVMonitor\Templates\Setup.xml` | セットアップテンプレート |

### データ保存先
| 項目 | パス | 説明 |
|------|------|------|
| **JRA-VANデータ** | `C:\ProgramData\JRA-VANData\data_s\NEW\` | JV-Linkから取得した生データ |
| **SQLite変換後** | `C:\JVLinkToSQLite\JVLinkToSQLiteArtifact\race.db` | 変換済みデータベース |

### バックアップ・ログ
| 項目 | パス | 説明 |
|------|------|------|
| **DBバックアップ** | `C:\JVLinkToSQLite\JVLinkToSQLiteArtifact\backup\` | データベースバックアップ |
| **実行ログ** | `C:\JVLinkToSQLite\JVLinkToSQLiteArtifact\logs\` | 実行ログファイル |
| **設定バックアップ** | `C:\JVLinkToSQLite\JVLinkToSQLiteArtifact\setting.xml.backup_*` | 設定ファイルバックアップ |

---

## 🔄 運用フロー

### 初回セットアップ
1. **JVAcquire起動**
2. **Setup実行**: マスターデータ取得
3. **JVMonitor起動**: データ確認

### 日常運用
1. **Normal実行**: 開催日の基本データ取得
2. **Diff実行**: 差分データ取得
3. **Realtime実行**: オッズデータ取得（必要時）
4. **JVMonitor**: データ表示・分析

### データ取得タイミング
| タイミング | 実行内容 | 対象データ |
|------------|----------|------------|
| **開催前日** | Normal | レース情報、出走馬情報 |
| **開催当日** | Diff | 最新情報、除外情報 |
| **レース前** | Realtime | オッズ情報 |
| **レース後** | Diff | 結果情報 |

---

## ⚠️ トラブルシューティング

### よくある問題と解決方法

#### 1. 「該当データがありません」
- **原因**: 新しいデータがない（正常）
- **対処**: 青いダイアログで「該当データなし（正常）」と表示
- **確認**: ログで「該当データがありません」を確認

#### 2. XMLエラー（KeyNotFoundException）
- **原因**: テンプレートXMLのDataSpecが不正
- **対処**: テンプレートファイルを修正版に置き換え
- **確認**: JVLinkToSQLite 0.1.2対応のDataSpecのみ使用

#### 3. パスエラー
- **原因**: appsettings.jsonの設定が不正
- **対処**: パス一覧表で正しいパスを確認
- **確認**: ファイルの存在確認

#### 4. データベースエラー
- **原因**: race.dbの破損またはアクセス権限
- **対処**: バックアップからの復元
- **確認**: ログファイルで詳細確認

### ログファイル確認
| ログファイル | 場所 | 内容 |
|--------------|------|------|
| **実行ログ** | `C:\JVLinkToSQLite\JVLinkToSQLiteArtifact\logs\` | 実行結果詳細 |
| **JVMonitorログ** | アプリケーション内 | 表示エラー |
| **JVAcquireログ** | アプリケーション内 | 取得エラー |

### 緊急時対応
1. **データベース復元**: バックアップから復元
2. **設定リセット**: デフォルト設定に戻す
3. **ログ確認**: エラー詳細を確認
4. **段階的実行**: Setup → Normal → Diff の順で実行

---

## 📈 パフォーマンス最適化

### データベース最適化
- **インデックス**: 頻繁に検索されるカラムにインデックス設定
- **VACUUM**: 定期的なデータベース最適化
- **バックアップ**: 日次バックアップの自動化

### メモリ効率
- **ストリーミング処理**: 大容量データの効率的処理
- **バッチ処理**: 段階的なデータ統合
- **キャッシュ**: 頻繁にアクセスされるデータのキャッシュ

---

## 🔧 開発・保守

### 開発環境
- **Visual Studio 2022**: C# WinForms開発
- **.NET 6**: アプリケーション実行環境
- **SQLite**: データベース管理

### バージョン管理
- **Git**: ソースコード管理
- **バックアップ**: 設定ファイル・データベースの定期バックアップ

### 監視・アラート
- **ログ監視**: エラーログの自動監視
- **データ整合性**: 定期的なデータ検証
- **パフォーマンス**: 実行時間・メモリ使用量の監視

---

## 📚 参考資料

### 公式ドキュメント
- **JVLinkToSQLite**: `C:\JVLinkToSQLite\JVLinkToSQLiteArtifact\JVLinkToSQLite_0.1.2.0.pdf`
- **CURSOR_BOOTSTRAP**: `C:\JVLinkToSQLite\JVLinkToSQLiteArtifact\CURSOR_BOOTSTRAP.md`

### 設定ファイル
- **appsettings.json**: アプリケーション設定
- **テンプレートXML**: データ取得設定

### ログ・バックアップ
- **実行ログ**: 詳細な実行履歴
- **データベースバックアップ**: データ復旧用

---

## 📅 2025年9月13日の更新内容

### ✅ JVMonitorアプリケーション修正完了

#### 修正内容
1. **コンパイルエラーの修正**
   - 重複定義エラー（Form1.cs と Form1_Fixed.cs）
   - null参照警告の修正
   - await演算子の不足修正

2. **不足イベントハンドラーの追加**
   - BtnRefreshDate_Click
   - BtnRunDiff_Click
   - BtnRunSetup_Click
   - BtnValidateDay_Click
   - BtnYDateCheck_Click
   - BtnGenerateBox_Click
   - BtnGenerateScenario_Click

3. **UI要素の修正**
   - lblLatestResultDate → lblToday への参照修正
   - 未使用フィールドのコメントアウト

#### ビルド結果
- **ビルド**: 成功（警告なし）
- **アプリケーション**: 正常起動・終了確認
- **実行ファイル**: `JVMonitor\bin\Release\net6.0-windows\win-x64\JVMonitor.exe`

### ✅ データベース状況確認（2025年9月13日）

#### 最新データ状況
- **全テーブル更新日時**: 2025年9月8日
- **データの鮮度**: 5-6日前
- **レースデータ**: 29,915レコード
- **オッズデータ**: 7,680レコード（25.7%カバレッジ）

#### オッズデータ詳細
```
NL_O1_ODDS_TANFUKUWAKU: 7,680 レコード (単勝・複勝)
NL_O2_ODDS_UMAREN: 7,680 レコード (馬連)
NL_O3_ODDS_WIDE: 7,680 レコード (ワイド)
NL_O4_ODDS_UMATAN: 7,680 レコード (馬単)
NL_O5_ODDS_SANREN: 7,944 レコード (三連複)
NL_O6_ODDS_SANRENTAN: 7,632 レコード (三連単)
```

### ✅ エクセルオッズ統合システム確認

#### 統合システムの実装状況
- **統合SQL**: `integration_queries.sql` 実装済み
- **統合ロジック**: JRA-VAN優先、エクセル補完
- **オッズ更新**: 確定データ（蓄積系）で十分

#### 統合テスト結果
```
レース: 20250906 01R01
Excel単勝: 1, 複勝: 1.5
JRA-VAN単勝: 2778, 複勝: 0227-0570
最終単勝: 2778, 複勝: 0227
```

**結論**: リアルタイムデータ不要、確定データでエクセルオッズ更新可能

### 🔧 セッション管理システム構築

#### 実装ファイル
- `session_manager.ps1`: JRA-VANセッション管理
- `run_with_session.ps1`: 統合データ取得フロー
- `run_with_session.bat`: バッチ版
- `realtime_fallback.xml`: フォールバック設定

#### 機能
- **動的セッションキー取得**: JVInit/JVSetUI/JVOpen
- **自動フォールバック**: リアルタイム失敗時はDIFF実行
- **統合フロー**: Normal → Diff → Realtime

### 📊 システム全体の状況（2025年9月13日）

#### ✅ 完了項目
- JVMonitorアプリケーション修正
- データベース統合確認
- エクセルオッズ統合システム確認
- セッション管理システム構築
- リアルタイム認証問題解決

#### ⚠️ 注意事項
- データの鮮度: 5-6日前（最新データ取得推奨）
- オッズカバレッジ: 25.7%（低い）
- 最新開催日データ: 未取得

#### 🎯 推奨運用
1. **JVMonitor**: 正常動作、オッズ取得ボタン使用可能
2. **データ更新**: 差分更新で最新データ取得
3. **エクセル統合**: 確定データで十分、リアルタイム不要

---

**最終更新**: 2025年9月13日  
**バージョン**: 1.1  
**作成者**: JVMonitor開発チーム
