# JVLinkToSQLite データ取得システム パス一覧表

## 🎯 メインデータベース（中心）
| 項目 | パス | 説明 |
|------|------|------|
| **メインDB** | `C:\my_project_folder\envs\cursor\my_keiba\JVLinkToSQLite-0.1.2\JVLinkToSQLiteArtifact\race.db` | **中心となるSQLiteデータベース** |
| **メインEXE** | `C:\my_project_folder\envs\cursor\my_keiba\JVLinkToSQLite-0.1.2\JVLinkToSQLiteArtifact\JVLinkToSQLite.exe` | **データ取得実行ファイル** |

## 📁 プロジェクト構成

### 1. メイン作業ディレクトリ
| 項目 | パス | 説明 |
|------|------|------|
| **プロジェクトルート** | `C:\my_project_folder\envs\cursor\my_keiba\` | 開発・運用の中心ディレクトリ |
| **JVMonitor** | `C:\my_project_folder\envs\cursor\my_keiba\JVMonitor\` | データ表示アプリケーション |
| **JVAcquire** | `C:\my_project_folder\envs\cursor\my_keiba\JVAcquire\` | データ取得専用アプリケーション |

### 2. 設定ファイル（appsettings.json）
| 項目 | パス | 説明 |
|------|------|------|
| **データベース** | `C:\my_project_folder\envs\cursor\my_keiba\JVLinkToSQLite-0.1.2\JVLinkToSQLiteArtifact\race.db` | メインDB |
| **実行ファイル** | `C:\my_project_folder\envs\cursor\my_keiba\JVLinkToSQLite-0.1.2\JVLinkToSQLiteArtifact\JVLinkToSQLite.exe` | 取得EXE |
| **差分設定** | `C:\my_project_folder\envs\cursor\my_keiba\diff.xml` | 差分更新用XML |
| **通常設定** | `C:\my_project_folder\envs\cursor\my_keiba\normal.xml` | 通常更新用XML |
| **リアルタイム設定** | `C:\my_project_folder\envs\cursor\my_keiba\realtime.xml` | オッズ取得用XML |
| **セットアップ設定** | `C:\my_project_folder\envs\cursor\my_keiba\setup.xml` | セットアップ用XML |

### 3. テンプレートXML（JVAcquire用）
| 項目 | パス | 説明 |
|------|------|------|
| **Diff.xml** | `C:\my_project_folder\envs\cursor\my_keiba\JVLinkToSQLite\JVMonitor\Templates\Diff.xml` | 差分更新テンプレート |
| **Realtime.xml** | `C:\my_project_folder\envs\cursor\my_keiba\JVLinkToSQLite\JVMonitor\Templates\Realtime.xml` | オッズ取得テンプレート |
| **Normal.xml** | `C:\my_project_folder\envs\cursor\my_keiba\JVLinkToSQLite\JVMonitor\Templates\Normal.xml` | 通常更新テンプレート |
| **Setup.xml** | `C:\my_project_folder\envs\cursor\my_keiba\JVLinkToSQLite\JVMonitor\Templates\Setup.xml` | セットアップテンプレート |

## 🔄 データ取得フロー

### 実行順序
1. **セットアップ** → `Setup.xml` でマスターデータ取得
2. **通常更新** → `Normal.xml` でレース・出走馬データ取得  
3. **差分更新** → `Diff.xml` で最新データ取得
4. **オッズ取得** → `Realtime.xml` でオッズデータ取得

### 実行用BATファイル
| ファイル名 | パス | 用途 | 説明 |
|------------|------|------|------|
| **setup.bat** | `C:\my_project_folder\envs\cursor\my_keiba\scripts\setup.bat` | セットアップデータ取得 | 2021年～のRACE、YSCH、HOSE、HOYU、COMM、MING取得 |
| **diff.bat** | `C:\my_project_folder\envs\cursor\my_keiba\scripts\diff.bat` | 差分更新 | 最新データのみ取得 |
| **normal.bat** | `C:\my_project_folder\envs\cursor\my_keiba\scripts\normal.bat` | マスタデータ取得 | 2023年～のUM、KS、CH、BR、BN等基本情報取得 |
| **odds_o1.bat** | `C:\my_project_folder\envs\cursor\my_keiba\scripts\odds_o1.bat` | リアルタイムデータ取得 | オッズデータ取得 |

### 現在の設定構成（2025年9月8日更新）
| 設定ファイル | 用途 | 取得データ | 期間 | 状態 |
|------------|------|----------|------|------|
| **Setup.xml** | セットアップデータ | RACE、YSCH、HOSE、HOYU、COMM、MING | 2021年～ | 有効 |
| **setting.xml** | マスタデータ | UM、KS、CH、BR、BN | 2023年～ | 有効 |
| **Realtime.xml** | リアルタイムデータ | O1-O6（オッズ） | 開催日のみ | 有効 |

### データ保存先
| 項目 | パス | 説明 |
|------|------|------|
| **JRA-VANデータ** | `C:\ProgramData\JRA-VANData\data_s\NEW\` | JV-Linkから取得した生データ |
| **SQLite変換後** | `C:\my_project_folder\envs\cursor\my_keiba\JVLinkToSQLite-0.1.2\JVLinkToSQLiteArtifact\race.db` | 変換済みデータベース |

## 🛠️ 開発・運用ツール

### アプリケーション
| 項目 | パス | 説明 |
|------|------|------|
| **JVMonitor** | `C:\my_project_folder\envs\cursor\my_keiba\JVMonitor\JVMonitor.exe` | データ表示・分析ツール |
| **JVAcquire** | `C:\my_project_folder\envs\cursor\my_keiba\JVAcquire\JVAcquire.exe` | データ取得専用ツール |

### バックアップ・ログ
| 項目 | パス | 説明 |
|------|------|------|
| **DBバックアップ** | `C:\my_project_folder\envs\cursor\my_keiba\JVLinkToSQLite-0.1.2\JVLinkToSQLiteArtifact\backup\` | データベースバックアップ |
| **実行ログ** | `C:\my_project_folder\envs\cursor\my_keiba\JVLinkToSQLite-0.1.2\JVLinkToSQLiteArtifact\logs\` | 実行ログファイル |
| **設定バックアップ** | `C:\my_project_folder\envs\cursor\my_keiba\JVLinkToSQLite-0.1.2\JVLinkToSQLiteArtifact\setting.xml.backup_*` | 設定ファイルバックアップ |

## 📊 データ分析・確認

### Pythonスクリプト
| 項目 | パス | 説明 |
|------|------|------|
| **データ確認** | `C:\my_project_folder\envs\cursor\my_keiba\check_*.py` | 各種データ確認スクリプト |
| **分析ツール** | `C:\my_project_folder\envs\cursor\my_keiba\CollectorV2\analyze_jvlink_data.py` | データ分析スクリプト |

## ⚠️ 重要な注意点

1. **メインデータベース**: `C:\my_project_folder\envs\cursor\my_keiba\JVLinkToSQLite-0.1.2\JVLinkToSQLiteArtifact\race.db` が中心
2. **設定の一元化**: `appsettings.json` でパス管理
3. **テンプレートの分離**: 取得用途別にXMLテンプレートを分離
4. **バックアップ**: 重要なデータは自動バックアップ対象

## 🔧 トラブルシューティング

### よくある問題
- **「該当データがありません」**: 正常な結果（新しいデータがない）
- **XMLエラー**: テンプレートファイルのDataSpecが不正
- **パスエラー**: `appsettings.json` の設定確認

### 解決手順
1. JVAcquireでテンプレートパス確認
2. 実行順序: Setup → Normal → Diff → Realtime
3. ログファイルで詳細確認

