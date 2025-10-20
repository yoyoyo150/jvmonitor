@echo off
echo データベース復旧スクリプト
echo ==========================

echo.
echo 1. EveryDB2.3を完全に終了してください
echo 2. タスクマネージャーでEveryDB2.3.exeが実行されていないことを確認してください
echo 3. このスクリプトを再実行してください

echo.
echo データベースファイルの状態確認中...
if exist ecore.db (
    echo ✅ ecore.db が存在します
    dir ecore.db
) else (
    echo ❌ ecore.db が見つかりません
)

echo.
echo プロセス確認中...
tasklist /FI "IMAGENAME eq EveryDB2.3.exe" 2>nul
if %errorlevel% == 0 (
    echo ⚠️ EveryDB2.3.exeが実行中です
    echo EveryDB2.3を終了してください
) else (
    echo ✅ EveryDB2.3.exeは実行されていません
)

echo.
echo データベースロック解除を試行中...
python unlock_database.py

pause
