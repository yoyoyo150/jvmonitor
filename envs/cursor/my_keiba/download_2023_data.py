# -*- coding: utf-8 -*-
import subprocess
import sys
import io
import time
import os

# UTF-8エンコーディング設定
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def check_everydb_status():
    """EveryDB2.3の状態確認"""
    print("=== EveryDB2.3の状態確認 ===\n")
    
    everydb_path = r"J:\new program file\everydb230\everydb230\Application Files\EveryDB2.3_2_3_0_0\EveryDB2.3.exe"
    
    if os.path.exists(everydb_path):
        print(f"[OK] EveryDB2.3が見つかりました: {everydb_path}")
        file_size = os.path.getsize(everydb_path)
        print(f"[OK] ファイルサイズ: {file_size:,} bytes")
        return True
    else:
        print(f"[ERROR] EveryDB2.3が見つかりません: {everydb_path}")
        return False

def download_2023_data():
    """2023年のデータをダウンロード"""
    print("\n=== 2023年データのダウンロード ===\n")
    
    everydb_path = r"J:\new program file\everydb230\everydb230\Application Files\EveryDB2.3_2_3_0_0\EveryDB2.3.exe"
    
    try:
        print("EveryDB2.3を起動中...")
        
        # EveryDB2.3を起動
        process = subprocess.Popen([everydb_path], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True)
        
        print("[OK] EveryDB2.3が起動しました")
        print("手動でデータダウンロードを実行してください:")
        print("1. EveryDB2.3のウィンドウで「蓄積系」を選択")
        print("2. 2023年のデータを選択")
        print("3. ダウンロードを実行")
        print("4. 完了後、このスクリプトを再実行してデータを確認")
        
        # プロセスが終了するまで待機
        print("\nプロセスが終了するまで待機中...")
        process.wait()
        
        print("[OK] EveryDB2.3が終了しました")
        
    except Exception as e:
        print(f"[ERROR] EveryDB2.3の起動エラー: {e}")

def verify_2023_data():
    """2023年のデータを確認"""
    print("\n=== 2023年データの確認 ===\n")
    
    import sqlite3
    
    try:
        conn = sqlite3.connect('ecore.db')
        cursor = conn.cursor()
        
        # 2023年のレースデータ確認
        cursor.execute("SELECT COUNT(*) FROM N_RACE WHERE Year = '2023'")
        race_count = cursor.fetchone()[0]
        print(f"2023年のレース数: {race_count:,} 件")
        
        # 2023年の出馬データ確認
        cursor.execute("SELECT COUNT(*) FROM N_UMA_RACE WHERE Year = '2023'")
        uma_count = cursor.fetchone()[0]
        print(f"2023年の出馬数: {uma_count:,} 件")
        
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
        
        # 2023年の月別データ確認
        print("\n2023年の月別レース数:")
        cursor.execute("""
            SELECT 
                SUBSTR(MonthDay, 1, 2) as month,
                COUNT(*) as race_count
            FROM N_RACE
            WHERE Year = '2023'
            GROUP BY SUBSTR(MonthDay, 1, 2)
            ORDER BY month DESC
        """)
        monthly_data = cursor.fetchall()
        
        for month, race_count in monthly_data:
            print(f"  {month}月: {race_count:,} レース")
        
        conn.close()
        
        if race_count > 0 and uma_count > 0:
            print("\n[OK] 2023年のデータが正常に取得されました")
            return True
        else:
            print("\n[WARNING] 2023年のデータが不足しています")
            return False
            
    except Exception as e:
        print(f"[ERROR] データ確認エラー: {e}")
        return False

def main():
    """メイン実行"""
    print("=== 2023年データダウンロード支援 ===\n")
    
    # 1. EveryDB2.3の状態確認
    if not check_everydb_status():
        return
    
    # 2. 現在のデータ確認
    print("\n=== 現在のデータ確認 ===")
    verify_2023_data()
    
    # 3. データダウンロードの実行
    print("\n=== データダウンロードの実行 ===")
    download_2023_data()
    
    # 4. ダウンロード後の確認
    print("\n=== ダウンロード後の確認 ===")
    if verify_2023_data():
        print("\n🎉 2023年のデータが正常に取得されました！")
        print("JVMonitorで2023年の成績が表示されるはずです。")
    else:
        print("\n⚠️ 2023年のデータがまだ不足しています。")
        print("EveryDB2.3で再度データダウンロードを実行してください。")

if __name__ == "__main__":
    main()


