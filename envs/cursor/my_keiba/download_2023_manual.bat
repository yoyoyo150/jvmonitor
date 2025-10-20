@echo off
echo 2023年データダウンロード用スクリプト
echo =====================================

cd /d "J:\new program file\everydb230\everydb230\Application Files\EveryDB2.3_2_3_0_0"

echo.
echo EveryDB2.3を起動中...
start EveryDB2.3.exe

echo.
echo 手動で以下の操作を実行してください:
echo 1. EveryDB2.3のウィンドウで「蓄積系」を選択
echo 2. 「時系列」タブを選択
echo 3. 開始日を「2023/01/01」に設定
echo 4. 終了日を「2023/12/31」に設定
echo 5. データ種別で以下を選択:
echo    - N_RACE (レース情報)
echo    - N_UMA_RACE (出馬情報)
echo    - N_UMA (馬情報)
echo    - N_KISYU (騎手情報)
echo    - N_CHOKYO (調教師情報)
echo 6. 「ダウンロード開始」ボタンをクリック
echo 7. 完了まで待機

echo.
echo 完了後、このスクリプトを再実行してデータを確認してください。
pause
