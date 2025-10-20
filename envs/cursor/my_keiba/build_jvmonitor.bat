@echo off
echo JVMonitor 再ビルドスクリプト
echo ================================

cd /d "C:\my_project_folder\envs\cursor\my_keiba\JVMonitor\JVMonitor"

echo.
echo 1. プロジェクトをクリーンアップ...
dotnet clean

echo.
echo 2. プロジェクトを再ビルド（Release）...
dotnet build --configuration Release

echo.
echo 3. 実行ファイルをDebugフォルダにコピー...
copy "bin\Release\net6.0-windows\JVMonitor.exe" "bin\Debug\net6.0-windows\JVMonitor.exe"
copy "bin\Release\net6.0-windows\JVMonitor.dll" "bin\Debug\net6.0-windows\JVMonitor.dll"
copy "bin\Release\net6.0-windows\JVMonitor.pdb" "bin\Debug\net6.0-windows\JVMonitor.pdb"

echo.
echo 4. ビルド完了！
echo 実行ファイル: C:\my_project_folder\envs\cursor\my_keiba\JVMonitor\JVMonitor\bin\Debug\net6.0-windows\JVMonitor.exe

pause


