# -*- coding: utf-8 -*-
import sqlite3
import sys
import io
import os
import subprocess
import time

# UTF-8エンコーディング設定
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def check_current_data():
    """現在のデータ状況を確認"""
    print("=== 現在のデータ状況確認 ===\n")
    
    conn = sqlite3.connect('ecore.db')
    cursor = conn.cursor()
    
    # 年別レース数確認
    cursor.execute("""
        SELECT 
            Year,
            COUNT(*) as race_count
        FROM N_RACE
        WHERE Year BETWEEN '2020' AND '2025'
        GROUP BY Year
        ORDER BY Year DESC
    """)
    yearly_data = cursor.fetchall()
    
    print("年別レース数:")
    for year, race_count in yearly_data:
        print(f"  {year}年: {race_count:,} レース")
    
    # プラダリアの2023年成績確認
    cursor.execute("""
        SELECT COUNT(*) FROM N_UMA_RACE
        WHERE Bamei = 'プラダリア' AND Year = '2023'
    """)
    pradaria_2023 = cursor.fetchone()[0]
    print(f"\nプラダリアの2023年出馬数: {pradaria_2023} 件")
    
    conn.close()

def configure_everydb_for_2023():
    """EveryDB2.3の設定を2023年データ取得用に変更"""
    print("\n=== EveryDB2.3設定変更 ===\n")
    
    config_path = r"J:\new program file\everydb230\everydb230\Application Files\EveryDB2.3_2_3_0_0\config.xml"
    
    if os.path.exists(config_path):
        print(f"[OK] 設定ファイルが見つかりました: {config_path}")
        
        # 設定ファイルの内容を確認
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print("\n現在の設定内容:")
            print(content[:500] + "..." if len(content) > 500 else content)
    else:
        print(f"[ERROR] 設定ファイルが見つかりません: {config_path}")

def create_2023_download_script():
    """2023年データダウンロード用スクリプトを作成"""
    print("\n=== 2023年データダウンロード用スクリプト作成 ===\n")
    
    script_content = '''@echo off
echo 2023年データダウンロード用スクリプト
echo =====================================

cd /d "J:\\new program file\\everydb230\\everydb230\\Application Files\\EveryDB2.3_2_3_0_0"

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
'''
    
    with open('download_2023_manual.bat', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("[OK] download_2023_manual.bat を作成しました")

def run_everydb_with_2023_settings():
    """2023年設定でEveryDB2.3を実行"""
    print("\n=== 2023年設定でEveryDB2.3を実行 ===\n")
    
    everydb_path = r"J:\new program file\everydb230\everydb230\Application Files\EveryDB2.3_2_3_0_0\EveryDB2.3.exe"
    
    if os.path.exists(everydb_path):
        print("EveryDB2.3を起動中...")
        try:
            # EveryDB2.3を起動
            process = subprocess.Popen([everydb_path], 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE,
                                     text=True)
            
            print("[OK] EveryDB2.3が起動しました")
            print("\n手動で以下の操作を実行してください:")
            print("1. EveryDB2.3のウィンドウで「蓄積系」を選択")
            print("2. 「時系列」タブを選択")
            print("3. 開始日を「2023/01/01」に設定")
            print("4. 終了日を「2023/12/31」に設定")
            print("5. データ種別で以下を選択:")
            print("   - N_RACE (レース情報)")
            print("   - N_UMA_RACE (出馬情報)")
            print("   - N_UMA (馬情報)")
            print("   - N_KISYU (騎手情報)")
            print("   - N_CHOKYO (調教師情報)")
            print("6. 「ダウンロード開始」ボタンをクリック")
            print("7. 完了まで待機")
            
            # プロセスが終了するまで待機
            print("\nプロセスが終了するまで待機中...")
            process.wait()
            
            print("[OK] EveryDB2.3が終了しました")
            
        except Exception as e:
            print(f"[ERROR] EveryDB2.3の起動エラー: {e}")
    else:
        print(f"[ERROR] EveryDB2.3が見つかりません: {everydb_path}")

def verify_2023_download():
    """2023年データのダウンロード結果を確認"""
    print("\n=== 2023年データダウンロード結果確認 ===\n")
    
    conn = sqlite3.connect('ecore.db')
    cursor = conn.cursor()
    
    # 2023年のレース数確認
    cursor.execute("SELECT COUNT(*) FROM N_RACE WHERE Year = '2023'")
    race_2023 = cursor.fetchone()[0]
    print(f"2023年のレース数: {race_2023:,} 件")
    
    # 2023年の出馬数確認
    cursor.execute("SELECT COUNT(*) FROM N_UMA_RACE WHERE Year = '2023'")
    uma_2023 = cursor.fetchone()[0]
    print(f"2023年の出馬数: {uma_2023:,} 件")
    
    # プラダリアの2023年成績確認
    cursor.execute("""
        SELECT COUNT(*) FROM N_UMA_RACE
        WHERE Bamei = 'プラダリア' AND Year = '2023'
    """)
    pradaria_2023 = cursor.fetchone()[0]
    print(f"プラダリアの2023年出馬数: {pradaria_2023} 件")
    
    if pradaria_2023 > 0:
        print("\nプラダリアの2023年成績:")
        cursor.execute("""
            SELECT 
                MonthDay,
                JyoCD,
                RaceNum,
                NyusenJyuni,
                KakuteiJyuni,
                KisyuRyakusyo,
                Honsyokin,
                Time
            FROM N_UMA_RACE
            WHERE Bamei = 'プラダリア' AND Year = '2023'
            ORDER BY MonthDay DESC
        """)
        races = cursor.fetchall()
        
        for race in races:
            monthday, jyo_cd, race_num, nyusen, kakutei, kisyu, honsyokin, time = race
            date_str = f"{monthday[:2]}月{monthday[2:]}日"
            print(f"  {date_str} 場{jyo_cd} {race_num}R ({kakutei or nyusen}位)")
            print(f"    騎手: {kisyu}, 賞金: {honsyokin}円, タイム: {time}")
    
    conn.close()
    
    if race_2023 > 0 and uma_2023 > 0:
        print("\n[OK] 2023年のデータが正常に取得されました")
        return True
    else:
        print("\n[WARNING] 2023年のデータがまだ不足しています")
        return False

def main():
    """メイン実行"""
    print("=== 2023年データ強制ダウンロード ===\n")
    
    # 1. 現在のデータ状況確認
    check_current_data()
    
    # 2. EveryDB2.3設定確認
    configure_everydb_for_2023()
    
    # 3. 2023年ダウンロード用スクリプト作成
    create_2023_download_script()
    
    # 4. EveryDB2.3を2023年設定で実行
    run_everydb_with_2023_settings()
    
    # 5. ダウンロード結果確認
    if verify_2023_download():
        print("\n🎉 2023年のデータが正常に取得されました！")
        print("JVMonitorで2023年の成績が表示されるはずです。")
    else:
        print("\n⚠️ 2023年のデータがまだ不足しています。")
        print("EveryDB2.3で再度データダウンロードを実行してください。")

if __name__ == "__main__":
    main()


