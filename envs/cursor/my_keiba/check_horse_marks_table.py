import sqlite3

def check_horse_marks_table():
    """HORSE_MARKSテーブルの詳細確認"""
    
    print("=== HORSE_MARKSテーブルの詳細確認 ===")
    
    conn = sqlite3.connect('ecore.db')
    cursor = conn.cursor()
    
    # 1. テーブル構造確認
    cursor.execute("PRAGMA table_info(HORSE_MARKS)")
    columns = cursor.fetchall()
    print(f"カラム数: {len(columns)}")
    
    mark_columns = [col for col in columns if 'Mark' in col[1] or 'ZI' in col[1] or 'ZM' in col[1]]
    print(f"Mark関連カラム: {[col[1] for col in mark_columns]}")
    
    # 2. ナムラクレアのデータ確認
    cursor.execute("""
        SELECT *
        FROM HORSE_MARKS
        WHERE HorseName LIKE '%ナムラクレア%'
        ORDER BY RaceDate DESC
        LIMIT 5
    """)
    
    data = cursor.fetchall()
    print(f"\nナムラクレアのデータ: {len(data)}件")
    
    if data:
        # カラム名を取得
        column_names = [col[1] for col in columns]
        print("カラム名:", column_names)
        
        for i, row in enumerate(data):
            print(f"\nレコード{i+1}:")
            for j, value in enumerate(row):
                if j < len(column_names):
                    print(f"  {column_names[j]}: {value}")
    
    # 3. 全データの件数確認
    cursor.execute("SELECT COUNT(*) FROM HORSE_MARKS")
    total_count = cursor.fetchone()[0]
    print(f"\nHORSE_MARKSテーブルの総レコード数: {total_count:,}件")
    
    conn.close()

if __name__ == "__main__":
    check_horse_marks_table()




