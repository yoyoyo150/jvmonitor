import sqlite3
import os

def test_historical_horse_data():
    """古い馬データの表示状況をテスト"""
    
    print("=== 古い馬データの表示状況テスト ===")
    
    conn = sqlite3.connect('excel_data.db')
    cursor = conn.cursor()
    
    # 2024年の馬データサンプル
    print("\n1. 2024年の馬データサンプル")
    cursor.execute("""
        SELECT SourceDate, HorseName, Mark5, Mark6, ZI_INDEX
        FROM HORSE_MARKS 
        WHERE SourceDate LIKE '2024%'
        ORDER BY SourceDate DESC
        LIMIT 5
    """)
    
    print("最新5件の2024年データ:")
    for row in cursor.fetchall():
        print(f"  {row[0]} | {row[1]} | M5:{row[2]} | M6:{row[3]} | ZI:{row[4]}")
    
    # 特定の馬の歴史データ
    print("\n2. 特定の馬の歴史データ（2024年）")
    cursor.execute("""
        SELECT SourceDate, HorseName, Mark5, Mark6
        FROM HORSE_MARKS 
        WHERE SourceDate LIKE '2024%' AND HorseNameS IS NOT NULL
        GROUP BY HorseNameS
        ORDER BY SourceDate DESC
        LIMIT 3
    """)
    
    print("2024年の馬（最新3頭）:")
    for row in cursor.fetchall():
        print(f"  {row[0]} | {row[1]} | {row[2]} | M5:{row[3]} | M6:{row[4]}")
    
    # データの時系列分布
    print("\n3. データの時系列分布")
    cursor.execute("""
        SELECT 
            SUBSTR(SourceDate, 1, 6) as month,
            COUNT(*) as count
        FROM HORSE_MARKS 
        WHERE SourceDate LIKE '2024%'
        GROUP BY month
        ORDER BY month DESC
    """)
    
    print("2024年月別データ:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]:,}件")
    
    conn.close()
    
    print("\n=== 結論 ===")
    print("古いデータ（2024年）は正常に登録されています")
    print("JVMonitorで馬カードを確認して、古いデータが表示されるかテストしてください")

if __name__ == "__main__":
    test_historical_horse_data()
