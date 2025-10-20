import sqlite3

def check_horse_marks_safe():
    """HORSE_MARKSテーブルの安全な確認"""
    
    print("=== HORSE_MARKSテーブルの安全な確認 ===")
    
    conn = sqlite3.connect('ecore.db')
    cursor = conn.cursor()
    
    # 1. テーブル構造確認
    cursor.execute("PRAGMA table_info(HORSE_MARKS)")
    columns = cursor.fetchall()
    print(f"カラム数: {len(columns)}")
    
    # 全カラム名を表示
    column_names = [col[1] for col in columns]
    print(f"全カラム: {column_names}")
    
    # 2. ナムラクレアのデータ検索（カラム名を特定してから）
    print("\n=== ナムラクレアのデータ検索 ===")
    
    # 馬名カラムを特定
    name_columns = [col for col in columns if 'name' in col[1].lower() or 'horse' in col[1].lower()]
    print(f"馬名関連カラム: {[col[1] for col in name_columns]}")
    
    if name_columns:
        name_col = name_columns[0]
        cursor.execute(f"""
            SELECT *
            FROM HORSE_MARKS
            WHERE {name_col} LIKE '%ナムラクレア%'
            LIMIT 3
        """)
        
        data = cursor.fetchall()
        print(f"ナムラクレアのデータ: {len(data)}件")
        
        if data:
            print("\n最初のレコード:")
            for i, value in enumerate(data[0]):
                if i < len(column_names):
                    print(f"  {column_names[i]}: {value}")
    
    # 3. 全データの件数確認
    cursor.execute("SELECT COUNT(*) FROM HORSE_MARKS")
    total_count = cursor.fetchone()[0]
    print(f"\nHORSE_MARKSテーブルの総レコード数: {total_count:,}件")
    
    conn.close()

if __name__ == "__main__":
    check_horse_marks_safe()




