param(
    [string]$OutputRoot,
    [switch]$Zip
)

# --- ルート解決 ------------------------------------------------------------
$scriptRoot = $PSScriptRoot
if (-not $scriptRoot) {
    $scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
}
if ([string]::IsNullOrWhiteSpace($scriptRoot)) {
    throw "スクリプトの場所を特定できませんでした。"
}

$toolsDir = Get-Item -LiteralPath $scriptRoot
$myKeibaRoot = $toolsDir.Parent
$cursorDir   = $myKeibaRoot.Parent
$envsDir     = $cursorDir.Parent
$repoRoot    = $envsDir.Parent

if (-not $myKeibaRoot -or -not $repoRoot) {
    throw "必須パスの特定に失敗しました。"
}

if (-not $OutputRoot) {
    $OutputRoot = Join-Path $repoRoot.FullName "dist"
}

if ([string]::IsNullOrWhiteSpace($OutputRoot)) {
    throw "出力先ディレクトリが無効です。"
}

if (-not (Test-Path $OutputRoot)) {
    New-Item -ItemType Directory -Path $OutputRoot | Out-Null
}

$timestamp   = Get-Date -Format "yyyyMMdd_HHmm"
$bundleName  = "JVMonitorDevBundle_$timestamp"
$bundleRoot  = Join-Path $OutputRoot $bundleName

if ([string]::IsNullOrWhiteSpace($bundleRoot)) {
    throw "バンドル先のパスが無効です。"
}

Write-Host "[create_dev_bundle] 出力先: $bundleRoot"
New-Item -ItemType Directory -Path $bundleRoot -Force | Out-Null

# --- コピー処理 ------------------------------------------------------------
$targetKeiba = Join-Path $bundleRoot "my_keiba"
Write-Host "[create_dev_bundle] my_keiba をコピー中..."
Copy-Item -Path $myKeibaRoot.FullName -Destination $targetKeiba -Recurse -Force

$docsSource = Join-Path $repoRoot.FullName "docs"
if (Test-Path $docsSource) {
    $docsTarget = Join-Path $bundleRoot "docs"
    Write-Host "[create_dev_bundle] docs をコピー中..."
    Copy-Item -Path $docsSource -Destination $docsTarget -Recurse -Force
}

# --- 除外フィルタ ----------------------------------------------------------
$directoriesToRemove = @("logs","outputs","runs","__pycache__","publish","dist","build")
foreach ($dirName in $directoriesToRemove) {
    Get-ChildItem -Path $bundleRoot -Directory -Filter $dirName -Recurse -ErrorAction SilentlyContinue |
        ForEach-Object {
            Write-Host "[create_dev_bundle] ディレクトリ削除: $($_.FullName)"
            Remove-Item -LiteralPath $_.FullName -Recurse -Force
        }
}

$filePatternsToRemove = @("*.db","*.db-shm","*.db-wal","*.sqlite","*.sqlite3","*.mdb","*.accdb","*.xlsx")
foreach ($pattern in $filePatternsToRemove) {
    Get-ChildItem -Path $bundleRoot -Include $pattern -Recurse -File -ErrorAction SilentlyContinue |
        ForEach-Object {
            Write-Host "[create_dev_bundle] 削除: $($_.FullName)"
            Remove-Item -LiteralPath $_.FullName -Force
        }
}

# --- マニフェスト ----------------------------------------------------------
$manifestPath = Join-Path $bundleRoot "bundle_manifest.txt"
$manifest = @"
JVMonitor Developer Bundle
生成日時 : $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
スクリプト : tools/create_dev_bundle.ps1

含まれる主要ディレクトリ:
- my_keiba (DB/Excelデータを除く)
- docs (共有ドキュメント)

除外パターン:
- ディレクトリ: $($directoriesToRemove -join ', ')
- ファイル: $($filePatternsToRemove -join ', ')

DB や実データは含まれないため、利用者は各自で再取得してください。
"@
Set-Content -Path $manifestPath -Value $manifest -Encoding UTF8

# --- ZIP オプション --------------------------------------------------------
if ($Zip) {
    $zipPath = "$bundleRoot.zip"
    if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
    Write-Host "[create_dev_bundle] ZIP を作成: $zipPath"
    Compress-Archive -Path $bundleRoot -DestinationPath $zipPath
}

Write-Host "[create_dev_bundle] 完了"
