import sqlite3
import sys
import io
import subprocess
import os
import time
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

JV_MONITOR_PATH = r"C:\my_project_folder\envs\cursor\my_keiba\JVMonitor\JVMonitor\bin\Debug\net6.0-windows\JVMonitor.exe"
DB_PATH = 'ecore.db'

def verify_jvmonitor_fix():
    print("=== JVMonitor.exeでの実際の確認 ===\n")

    # 1. データベースの状況を確認
    print("1. データベースの状況を確認")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 最新のデータを確認
    cursor.execute("SELECT MAX(SourceDate) FROM HORSE_MARKS")
    latest_date = cursor.fetchone()[0]
    print(f"最新の日付: {latest_date}")
    
    # 最新日付のレコード数
    cursor.execute("SELECT COUNT(*) FROM HORSE_MARKS WHERE SourceDate = ?", (latest_date,))
    latest_count = cursor.fetchone()[0]
    print(f"最新日付のレコード数: {latest_count} 件")
    
    # 馬印データの状況
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN Mark1 IS NOT NULL AND Mark1 != '' THEN 1 END) as mark1_count,
            COUNT(CASE WHEN Mark2 IS NOT NULL AND Mark2 != '' THEN 1 END) as mark2_count,
            COUNT(CASE WHEN Mark3 IS NOT NULL AND Mark3 != '' THEN 1 END) as mark3_count
        FROM HORSE_MARKS 
        WHERE SourceDate = ?
    """, (latest_date,))
    
    mark_stats = cursor.fetchone()
    total, m1, m2, m3 = mark_stats
    print(f"馬印データ: 馬印1={m1}({m1/total*100:.1f}%), 馬印2={m2}({m2/total*100:.1f}%), 馬印3={m3}({m3/total*100:.1f}%)")
    
    # サンプルデータ
    cursor.execute("""
        SELECT HorseName, Mark1, Mark2, Mark3
        FROM HORSE_MARKS 
        WHERE SourceDate = ? AND (Mark1 IS NOT NULL OR Mark2 IS NOT NULL OR Mark3 IS NOT NULL)
        LIMIT 5
    """, (latest_date,))
    
    samples = cursor.fetchall()
    print("サンプルデータ:")
    for sample in samples:
        horse_name, m1, m2, m3 = sample
        print(f"  {horse_name}: 馬印1={m1}, 馬印2={m2}, 馬印3={m3}")
    
    conn.close()

    # 2. JVMonitor.exeの存在確認
    print("\n2. JVMonitor.exeの存在確認")
    if os.path.exists(JV_MONITOR_PATH):
        print(f"✅ JVMonitor.exeが存在します: {JV_MONITOR_PATH}")
        
        # ファイルの更新時刻
        mod_time = datetime.fromtimestamp(os.path.getmtime(JV_MONITOR_PATH))
        print(f"ファイル更新時刻: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # ファイルサイズ
        file_size = os.path.getsize(JV_MONITOR_PATH)
        print(f"ファイルサイズ: {file_size:,} bytes")
    else:
        print(f"❌ JVMonitor.exeが見つかりません: {JV_MONITOR_PATH}")
        return

    # 3. JVMonitor.exeの実行テスト
    print("\n3. JVMonitor.exeの実行テスト")
    try:
        # JVMonitor.exeを起動（非同期）
        print("JVMonitor.exeを起動中...")
        process = subprocess.Popen([JV_MONITOR_PATH], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True)
        
        # 少し待機
        time.sleep(3)
        
        # プロセスの状態を確認
        if process.poll() is None:
            print("✅ JVMonitor.exeが正常に起動しました")
            print("⚠️ 手動でJVMonitorの画面を確認してください")
            print("   1. 馬印データが表示されているか")
            print("   2. 最新の日付のデータが表示されているか")
            print("   3. 馬印更新（増分）ボタンが機能するか")
            
            # プロセスを終了
            process.terminate()
            process.wait()
        else:
            print("❌ JVMonitor.exeの起動に失敗しました")
            stdout, stderr = process.communicate()
            if stdout:
                print(f"標準出力: {stdout}")
            if stderr:
                print(f"エラー出力: {stderr}")
                
    except Exception as e:
        print(f"❌ JVMonitor.exeの実行エラー: {e}")

    # 4. 確認手順の提示
    print("\n4. 確認手順")
    print("以下の手順でJVMonitorの動作を確認してください:")
    print("1. JVMonitor.exeを手動で起動")
    print("2. 最新の日付（2025年10月5日）を選択")
    print("3. 馬印データが表示されているか確認")
    print("4. 馬印更新（増分）ボタンをクリック")
    print("5. ボタンが正常に動作するか確認")
    print("6. エラーメッセージが表示されないか確認")

    # 5. 期待される結果
    print("\n5. 期待される結果")
    print("✅ 正常な場合:")
    print("   - 馬印データが表示される")
    print("   - 馬印更新（増分）ボタンが機能する")
    print("   - エラーメッセージが表示されない")
    print("❌ 問題がある場合:")
    print("   - 馬印データが表示されない")
    print("   - 馬印更新（増分）ボタンが機能しない")
    print("   - エラーメッセージが表示される")

if __name__ == '__main__':
    verify_jvmonitor_fix()

