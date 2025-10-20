@echo off
echo GDI+ Error Fix - EveryDB2.3 Runner
echo.

REM 環境変数を設定
set GDI_PLUS_ERROR_MODE=0
set DISPLAY=

echo 環境変数を設定しました
echo GDI_PLUS_ERROR_MODE=0
echo DISPLAY=
echo.

REM 既存のプロセスを終了
echo 既存のEveryDB2.3プロセスを終了中...
taskkill /IM EveryDB2.3.exe /F >nul 2>&1

REM 5秒待機
echo 5秒待機中...
timeout /t 5 /nobreak >nul

REM EveryDB2.3を開始
echo EveryDB2.3を開始中...
echo 画面が表示されませんが、処理は継続されます
echo 停止するには Ctrl+C を押してください
echo.

start /B "" "J:\new program file\everydb230\everydb230\Application Files\EveryDB2.3_2_3_0_0\EveryDB2.3.exe"

echo EveryDB2.3が開始されました
echo バックグラウンドで実行中...
echo.

REM 無限ループで待機
:loop
timeout /t 60 /nobreak >nul
echo [%date% %time%] 実行中...
goto loop
