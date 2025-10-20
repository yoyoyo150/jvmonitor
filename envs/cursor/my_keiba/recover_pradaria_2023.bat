@echo off
echo プラダリア2023年データ復旧スクリプト
echo =====================================

echo.
echo 1. データベースの整合性を確認中...
python check_pradaria_2023_data.py

echo.
echo 2. EveryDB2.3でデータを再ダウンロードしてください:
echo    - 蓄積系 > 時系列
echo    - 開始日: 2023/01/01
echo    - 終了日: 2023/12/31
echo    - データ種別: N_RACE, N_UMA_RACE, N_UMA

echo.
echo 3. 完了後、このスクリプトを再実行してください。
pause
