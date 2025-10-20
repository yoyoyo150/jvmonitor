import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

DB_PATH = 'ecore.db'

def check_duplicates():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=== N_UMA_RACE 2023年重複データ確認 ===\n")

    # 重複データの確認
    cursor.execute("""
        SELECT Year, MonthDay, JyoCD, RaceNum, Umaban, COUNT(*) as cnt 
        FROM N_UMA_RACE 
        WHERE Year = '2023' 
        GROUP BY Year, MonthDay, JyoCD, RaceNum, Umaban 
        HAVING COUNT(*) > 1 
        LIMIT 10
    """)
    duplicates = cursor.fetchall()
    
    if duplicates:
        print("重複データが見つかりました:")
        for dup in duplicates:
            print(f"  {dup[0]}{dup[1]} 場{dup[2]} {dup[3]}R {dup[4]}番: {dup[5]}件")
    else:
        print("重複データは見つかりませんでした。")

    # 総レコード数確認
    cursor.execute("SELECT COUNT(*) FROM N_UMA_RACE WHERE Year = '2023'")
    total_count = cursor.fetchone()[0]
    print(f"\n2023年総レコード数: {total_count:,} 件")

    # ユニークレコード数確認
    cursor.execute("""
        SELECT COUNT(*) FROM (
            SELECT DISTINCT Year, MonthDay, JyoCD, RaceNum, Umaban 
            FROM N_UMA_RACE 
            WHERE Year = '2023'
        )
    """)
    unique_count = cursor.fetchone()[0]
    print(f"2023年ユニークレコード数: {unique_count:,} 件")

    conn.close()

if __name__ == '__main__':
    check_duplicates()
