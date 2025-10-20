import sqlite3

def check_horse_marks_final():
    """HORSE_MARKSテーブルの最終確認"""
    
    print("=== HORSE_MARKSテーブルの最終確認 ===")
    
    conn = sqlite3.connect('ecore.db')
    cursor = conn.cursor()
    
    # 1. ナムラクレアのデータ検索
    print("\n=== ナムラクレアのデータ検索 ===")
    cursor.execute("""
        SELECT SourceDate, HorseName, Mark5, Mark6, ZI_INDEX, ZM_VALUE
        FROM HORSE_MARKS
        WHERE HorseName LIKE '%ナムラクレア%'
        ORDER BY SourceDate DESC
        LIMIT 5
    """)
    
    data = cursor.fetchall()
    print(f"ナムラクレアのデータ: {len(data)}件")
    
    if data:
        print("SourceDate | HorseName | Mark5 | Mark6 | ZI_INDEX | ZM_VALUE")
        print("------------------------------------------------------------")
        for row in data:
            print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]}")
    
    # 2. 全データの件数確認
    cursor.execute("SELECT COUNT(*) FROM HORSE_MARKS")
    total_count = cursor.fetchone()[0]
    print(f"\nHORSE_MARKSテーブルの総レコード数: {total_count:,}件")
    
    # 3. 日付範囲確認
    cursor.execute("SELECT MIN(SourceDate), MAX(SourceDate) FROM HORSE_MARKS")
    date_range = cursor.fetchone()
    print(f"データの日付範囲: {date_range[0]} ～ {date_range[1]}")
    
    conn.close()
    
    print("\n=== 結論 ===")
    print("JVMonitorはHORSE_MARKSテーブルからMark5/Mark6データを取得している")
    print("このテーブルに古いデータが不足している可能性がある")

if __name__ == "__main__":
    check_horse_marks_final()




