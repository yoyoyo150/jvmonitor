import sqlite3

def check_namura_claire_marks():
    conn = sqlite3.connect('excel_data.db')
    cursor = conn.cursor()

    print("=== ナムラクレアのMark5/Mark6データ確認 ===")
    cursor.execute("""
        SELECT SourceDate, HorseName, Mark5, Mark6, ZI_INDEX
        FROM HORSE_MARKS
        WHERE HorseName = 'ナムラクレア'
        ORDER BY SourceDate DESC
    """)
    
    data = cursor.fetchall()
    if data:
        print("SourceDate | HorseName | Mark5 | Mark6 | ZI_INDEX")
        print("-------------------------------------------------")
        for row in data:
            print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]}")
    else:
        print("ナムラクレアのデータはHORSE_MARKSテーブルに見つかりませんでした。")

    conn.close()

if __name__ == "__main__":
    check_namura_claire_marks()




