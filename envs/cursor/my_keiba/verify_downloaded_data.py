import sqlite3

def verify_downloaded_data():
    conn = sqlite3.connect('ecore.db')
    cursor = conn.cursor()
    
    print("=== ダウンロード後のデータ確認 ===\n")
    
    # 1. N_TOKU_RACE (特別レース) の確認
    cursor.execute("SELECT COUNT(*) FROM N_TOKU_RACE")
    toku_race_count = cursor.fetchone()[0]
    print(f"1. N_TOKU_RACE (特別レース): {toku_race_count:,} 件")
    
    if toku_race_count > 0:
        cursor.execute("SELECT * FROM N_TOKU_RACE LIMIT 3")
        sample_data = cursor.fetchall()
        print("   サンプルデータ:")
        for i, row in enumerate(sample_data):
            print(f"   {i+1}: {row[:5]}...")  # 最初の5カラムのみ表示
    
    print("\n" + "="*50 + "\n")
    
    # 2. N_TOKU (特別登録馬) の確認
    cursor.execute("SELECT COUNT(*) FROM N_TOKU")
    toku_count = cursor.fetchone()[0]
    print(f"2. N_TOKU (特別登録馬): {toku_count:,} 件")
    
    if toku_count > 0:
        cursor.execute("SELECT * FROM N_TOKU LIMIT 3")
        sample_data = cursor.fetchall()
        print("   サンプルデータ:")
        for i, row in enumerate(sample_data):
            print(f"   {i+1}: {row[:5]}...")  # 最初の5カラムのみ表示
    
    print("\n" + "="*50 + "\n")
    
    # 3. N_SCHEDULE (開催スケジュール) の確認
    cursor.execute("SELECT COUNT(*) FROM N_SCHEDULE")
    schedule_count = cursor.fetchone()[0]
    print(f"3. N_SCHEDULE (開催スケジュール): {schedule_count:,} 件")
    
    if schedule_count > 0:
        cursor.execute("SELECT * FROM N_SCHEDULE LIMIT 3")
        sample_data = cursor.fetchall()
        print("   サンプルデータ:")
        for i, row in enumerate(sample_data):
            print(f"   {i+1}: {row[:5]}...")  # 最初の5カラムのみ表示
    
    print("\n" + "="*50 + "\n")
    
    # 4. データの増加確認
    print("4. データ増加確認")
    print(f"   特別レース: {toku_race_count:,} 件")
    print(f"   特別登録馬: {toku_count:,} 件")
    print(f"   開催スケジュール: {schedule_count:,} 件")
    
    # 5. 年別データ確認
    if toku_race_count > 0:
        print("\n5. 特別レースの年別分布")
        cursor.execute("""
            SELECT Year, COUNT(*) as count 
            FROM N_TOKU_RACE 
            GROUP BY Year 
            ORDER BY Year DESC 
            LIMIT 5
        """)
        yearly_data = cursor.fetchall()
        for year, count in yearly_data:
            print(f"   {year}年: {count:,} 件")
    
    conn.close()

if __name__ == "__main__":
    verify_downloaded_data()


