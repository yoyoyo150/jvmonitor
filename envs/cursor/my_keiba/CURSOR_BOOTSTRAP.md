# JVMonitor / JVLinkToSQLite — 開発ガードレール（Cursor 起動時に読む・強化版）

この指令書は、JVMonitor（WPF/.NET 8）と JVLinkToSQLite（データ取得エンジン）を**安全**に開発・運用するためのガードレールです。
Cursor は以下のルールに従って提案・修正・実行を行ってください。

## 0. 環境と前提
- OS: Windows 10/11 x64
- .NET: .NET 8 (LTS)
- タイムゾーン: Asia/Tokyo（JST）
- 主設定ファイル: `C:\JVLinkToSQLite\setting.xml`（※運用では D: 配置推奨）
- 取得キャッシュ出力（.jvd）: 既定 `C:\ProgramData\JRA-VAN\Data Lab\data`（※運用では D: へ移設推奨）
- UI: JVMonitor（WPF/WinForms）。取得エンジンは Urasandesu.JVLinkToSQLite.exe（リアルタイムは**コンソール有り**で起動）。

## 1. 絶対ルール
1. **DataSpec ホワイトリスト以外を setting.xml に書かない**  
   許可: `TOKU, RACE, DIFF, BLOD, SLOP, SNAP, WOOD, YSCH, HOSE, HOYU, COMM, MING, DIFN, BLDN, UM, KS, CH, HR, BR, OR, TR, SR, LR, MR, PR, NR, RR, 0B11, 0B12, 0B13, 0B14, 0B15, 0B17`  
   禁止例: `SNPN, HOSN`／注：`SE`/`RA`は **DataSpecではなくRACE配下**。
2. **書換え前に必ずバックアップ（世代5件）／差分最小**。
3. **RACEの人気除外（O1〜O6）**はUIと1:1で同期（取得＝除外から外す／除外＝除外に入れる）。`WF`は方針に従う。
4. **リアルタイム親子整合**：子0Bxxが1つでもON→親ON、子全OFF→親OFF。
5. **未来データ遮断**：JSTの「現在＋5分超」は破棄・警告・親一時OFF（2分×3で再試行）。
6. **初回はRACEでベースを作成**（空DBにDIFF/DIFNだけはNG）。
7. **許可ルート外へ書かない**（C:\直下など）。Gitフック＋実行時ガードで強制。

## 2. スマート更新（順序固定）
1) Sanitize（ホワイトリスト化＋RACE除外整備）  
2) Preflight（権限／.jvdスナップショット／差分期間の一致）  
3) 通常更新（RACE/DIFF/DIFN＋マスタ群、必要ならBLOD/BLDN）  
4) Postcheck（ExitCode==0／ログにERRORなし／.jvd増分あり）  
5) 任意：リアルタイム（開催時間帯のみ親ON＋0Bxx、未来データ遮断）

## 3. 事前・事後チェック
- 事前：未知DataSpecなし／RACE除外がUI一致／出力先書込可／差分期間がUI値に一致
- 事後：ExitCode==0／ログERRORなし／.jvd増分あり／未来データ検出0件（検出時は再試行ログあり）

## 4. エラー時
- XML読込系例外→未知DataSpec疑い→Sanitize再適用
- 失敗→2分×3リトライ→ダメなら親リアルOFF・要約表示
- 書戻しは直前バックアップに戻す

## 5. 変更提案の出し方（Cursor）
Plan→Diff（最小）→Apply→Verify の順。破壊的変更は要確認。コミットメッセージは `feat|fix|chore|test|refactor:`。

## 6. テスト要件
- サニタイズ（未知DataSpec除去）
- RACE除外（人気ON/OFFでO1〜O6の有無切替）
- 未来データ遮断（now+10min入力→破棄＆ログ）
- 親子整合（子有→親ON／子全OFF→親OFF）
- 差分期間（UI値→setting.xml→実行ログ反映）

## 7. 三層ブレーキ
- ポリシー：`CURSOR_SAFETY.md`（Plan→Diff→Apply→Verify／許可外生成禁止）
- ツール：`.cursorignore` で不可視化、`pre-commit` で許可外パス拒否
- 実行時：`GuardedFileSystem` で許可外書込みを例外停止

## 8. 初手テンプレ


#repo
CURSOR_SAFETY.md / CURSOR_BOOTSTRAP.md を厳守。まず Plan を出し、承認後に最小 diff を提示。
禁止: 許可ルート外の生成、.sln/.csprojの変更、大規模一括編集。

'@
Set-Content -LiteralPath (Join-Path $root "CURSOR_BOOTSTRAP.md") -Value $bootstrap -Encoding UTF8

# 2) CURSOR_SAFETY.md
$safety = @'
# 編集ポリシー（Cursorは厳守）

## 変更範囲
- 変更可: `JVMonitor/**`, `JVLinkToSQLite/**`, `scripts/**`
- **禁止**: プロジェクト外（C:\直下など）・新規ルート作成・巨大成果物追加（*.jvd, *.csv, *.xlsx, *.zip）

## 作業手順（ステップゲート）
1. **Plan**: 変更ファイル一覧・目的・リスク・ロールバック（編集禁止）
2. **Diff**: 最小差分パッチのみ（新規ファイルは `JVMonitor/` or `scripts/` のみ）
3. **Review**: 承認後に Apply（承認前は書換禁止）
4. **Verify**: ビルド & HealthCheck（失敗時はロールバック）

## 禁止行為
- 無断の構造変更/移動
- `.sln/.csproj` の追加/削除（要確認）
- 許可外ディレクトリへの書込み
- 100行以上の一括編集（分割する）

## 出力様式
- すべて「最小差分（patch）」で出力
- 危険操作は **[CONFIRM REQUIRED]** を先頭に付与
'@
Set-Content -LiteralPath (Join-Path $root "CURSOR_SAFETY.md") -Value $safety -Encoding UTF8

# 3) guardrails_v2.json
$guardrails = @'
{
  "timezone": "Asia/Tokyo",
  "paths": {
    "settingXml": "C:/JVLinkToSQLite/setting.xml",
    "jvdRoots": [
      "C:/ProgramData/JRA-VAN/Data Lab/data",
      "C:/ProgramData/JRA-VANData/data"
    ],
    "logs": "C:/JVLinkToSQLite/logs"
  },
  "allowedDataSpecs": [
    "TOKU","RACE","DIFF","BLOD","SLOP","SNAP","WOOD","YSCH","HOSE","HOYU","COMM","MING",
    "DIFN","BLDN","UM","KS","CH","HR","BR","OR","TR","SR","LR","MR","PR","NR","RR",
    "0B11","0B12","0B13","0B14","0B15","0B17"
  ],
  "prohibitedDataSpecs": ["SNPN","HOSN","SE","RA"],
  "raceExclusion": {
    "control": "ExcludedRecordSpecs",
    "popularityKeys": ["O1","O2","O3","O4","O5","O6"],
    "wfKey": "WF"
  },
  "realtime": {
    "windowDays": ["Saturday","Sunday"],
    "start": "09:00",
    "end": "17:30",
    "futureGraceMinutes": 5,
    "childSpecs": ["0B11","0B12","0B13","0B14","0B15","0B17"]
  },
  "smartUpdate": {
    "steps": ["sanitize","preflight","runNormal","postcheck","maybeRunRealtime"],
    "retry": {"count": 3, "intervalMinutes": 2}
  },
  "preflightChecks": [
    "settingXml exists",
    "only allowedDataSpecs present",
    "race ExcludedRecordSpecs matches UI",
    "jvdRoots writable and accessible"
  ],
  "postflightChecks": [
    "exitCode == 0",
    "log has no ERROR",
    "jvd delta observed",
    "no future-dated records"
  ],
  "hardStops": [
    "unknown DataSpec present",
    "diff without base RACE",
    "realtime parent ON with no child ON"
  ],
  "ui": {
    "statusLeds": ["IDLE","NORMAL","REALTIME_WAIT","REALTIME_RX","ERROR"],
    "mustShow": ["lastReceiveAt","receiveCount30m","lastJvdUpdates"]
  }
}
'@
Set-Content -LiteralPath (Join-Path $root "guardrails_v2.json") -Value $guardrails -Encoding UTF8

# 4) .cursorignore
$cursorignore = @'
**/bin/**
**/obj/**
**/.git/**
**/.vs/**
**/.venv/**
**/__pycache__/**

# data & artifacts
**/*.jvd
**/*.csv
**/*.xlsx
**/*.zip
**/*.7z

# logs
**/logs/**

Thumbs.db
.DS_Store
'@
Set-Content -LiteralPath (Join-Path $root ".cursorignore") -Value $cursorignore -Encoding UTF8

# 5) Git hook wrapper (sh) + PowerShell本体
$hookSh = @'
#!/bin/sh
if command -v pwsh >/dev/null 2>&1; then
  pwsh -NoProfile -File ".githooks/pre-commit.ps1"
else
  powershell -NoProfile -ExecutionPolicy Bypass -File ".githooks/pre-commit.ps1"
fi
'@
Set-Content -LiteralPath (Join-Path $root ".githooks\pre-commit") -Value $hookSh -Encoding ASCII
# 可能なら実行権（Git Bash用）
try { & git update-index --add --chmod=+x ".githooks/pre-commit" } catch {}

$hookPs1 = @'
# .githooks/pre-commit.ps1
$ErrorActionPreference='Stop'

$allowed = @(
  "JVMonitor\", "JVLinkToSQLite\", "scripts\", ".githooks\", "CURSOR_BOOTSTRAP.md", "CURSOR_SAFETY.md", "guardrails_v2.json", ".cursorignore"
)

$changed = git diff --cached --name-only
if (-not $changed) { exit 0 }

$bad = @()
foreach($f in $changed.Split("`n")){
  if([string]::IsNullOrWhiteSpace($f)){ continue }
  $ok = $false
  foreach($root in $allowed){
    if($f.StartsWith($root, [System.StringComparison]::OrdinalIgnoreCase)){ $ok=$true; break }
  }
  if(-not $ok){ $bad += $f }
}

if($bad.Count -gt 0){
  Write-Host "❌ 許可ルート外の変更があります。コミットを中止します。" -ForegroundColor Red
  $bad | % { Write-Host " - $_" }
  Write-Host "許可ルート: $($allowed -join ', ')"
  exit 1
}

# 10MB超の新規ファイルを拒否
$large = git diff --cached --name-only --diff-filter=A | %{
  $s = (Get-Item $_ -ErrorAction SilentlyContinue)
  if($s -and $s.Length -gt 10MB){ $_ }
}
if($large){
  Write-Host "❌ 10MB超の新規ファイルがあります。コミットを中止します。" -ForegroundColor Red
  $large | % { Write-Host " - $_" }
  exit 1
}
'@
Set-Content -LiteralPath (Join-Path $root ".githooks\pre-commit.ps1") -Value $hookPs1 -Encoding UTF8

# 6) GuardedFileSystem.cs
$guardCs = @'
using System;
using System.IO;
using System.Linq;

namespace JVMonitor.Common
{
    public static class GuardedFileSystem
    {
        // 許可ルート（運用では D:\ を推奨。必要なら変更）
        public static string[] AllowedRoots { get; set; } = new[]
        {
            @"D:\JVMonitor", @"D:\JVData"
        };

        private static void EnsureAllowed(string path)
        {
            var full = Path.GetFullPath(path).TrimEnd(Path.DirectorySeparatorChar) + Path.DirectorySeparatorChar;
            bool ok = AllowedRoots.Any(r =>
                full.StartsWith(Path.GetFullPath(r).TrimEnd(Path.DirectorySeparatorChar) + Path.DirectorySeparatorChar,
                                StringComparison.OrdinalIgnoreCase));
            if (!ok) throw new InvalidOperationException($"許可外への書き込みは禁止です: {full}");
        }

        public static void WriteAllText(string path, string content)
        {
            EnsureAllowed(path);
            Directory.CreateDirectory(Path.GetDirectoryName(path)!);
            File.WriteAllText(path, content);
        }

        public static void Copy(string src, string dst, bool overwrite = true)
        {
            EnsureAllowed(dst);
            Directory.CreateDirectory(Path.GetDirectoryName(dst)!);
            File.Copy(src, dst, overwrite);
        }

        public static void Move(string src, string dst, bool overwrite = true)
        {
            EnsureAllowed(dst);
            if (overwrite && File.Exists(dst)) File.Delete(dst);
            Directory.CreateDirectory(Path.GetDirectoryName(dst)!);
            File.Move(src, dst);
        }
    }
}
'@
Set-Content -LiteralPath (Join-Path $root "src\GuardedFileSystem.cs") -Value $guardCs -Encoding UTF8

# 7) healthcheck.ps1
$health = @'
# scripts/healthcheck.ps1
$ErrorActionPreference = 'Stop'
$setting = 'C:\JVLinkToSQLite\setting.xml'
$jvdRoots = @('C:\ProgramData\JRA-VAN\Data Lab\data','C:\ProgramData\JRA-VANData\data') | ?{ Test-Path $_ }

Write-Host "=== JV Health Check ==="

if(!(Test-Path $setting)){ Write-Host "[FAIL] setting.xml not found" -f Red; exit 1 }
[xml]$xml = Get-Content $setting -Raw
$specs = $xml.JVLinkToSQLiteSetting.Details.JVNormalUpdateSetting.DataSpecSettings.JVDataSpecSetting |
         % { $_.DataSpec } | Sort-Object -Unique
$allowed = @('TOKU','RACE','DIFF','BLOD','SLOP','SNAP','WOOD','YSCH','HOSE','HOYU','COMM','MING','DIFN','BLDN',
             'UM','KS','CH','HR','BR','OR','TR','SR','LR','MR','PR','NR','RR','0B11','0B12','0B13','0B14','0B15','0B17')
$bad = $specs | ?{ $allowed -notcontains $_ }
if($bad){ Write-Host "[FAIL] unknown DataSpec: $($bad -join ', ')" -f Red } else { Write-Host "[OK] DataSpec whitelist" -f Green }

if(!$jvdRoots){ Write-Host "[WARN] no jvd roots found"; exit 0 }
$files = $jvdRoots | % { Get-ChildItem $_ -Filter *.jvd -ErrorAction SilentlyContinue } | Sort LastWriteTime -Desc
$last = $files | Select -First 10 FullName,LastWriteTime
Write-Host "[INFO] recent jvd:"; $last | Format-Table -AutoSize
'@
Set-Content -LiteralPath (Join-Path $root "scripts\healthcheck.ps1") -Value $health -Encoding UTF8

Write-Host "✅ Files created."
Write-Host "次に実行:  git config core.hooksPath .githooks"

補足

AllowedRoots（D:\JVMonitor / D:\JVData） はあなたの運用に合わせて変更OK。

既に CURSOR_BOOTSTRAP.md がある場合は、上書き確認が出たら 置き換え を選んでください（強化版です）。

フックが動かない場合は、Git Bash 環境で git update-index --chmod=+x .githooks/pre-commit を一度流して権限を付けてください。