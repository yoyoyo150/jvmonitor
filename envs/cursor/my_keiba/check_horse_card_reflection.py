import sqlite3
import sys
import io
import os
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

DB_PATH = 'excel_data.db'

def check_horse_card_reflection():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=== 馬のカード反映状況確認 ===\n")

    # 1. 最新データの確認
    print("1. 最新データの確認")
    cursor.execute("SELECT MAX(SourceDate) FROM HORSE_MARKS")
    latest_date = cursor.fetchone()[0]
    print(f"最新データ日: {latest_date}")

    cursor.execute("SELECT COUNT(*) FROM HORSE_MARKS WHERE SourceDate = ?", (latest_date,))
    latest_count = cursor.fetchone()[0]
    print(f"最新日のレコード数: {latest_count:,} 件")

    # 2. 馬印データの確認
    print("\n2. 馬印データの確認")
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN Mark1 IS NOT NULL AND Mark1 != '' THEN 1 END) as mark1_count,
            COUNT(CASE WHEN Mark2 IS NOT NULL AND Mark2 != '' THEN 1 END) as mark2_count,
            COUNT(CASE WHEN Mark3 IS NOT NULL AND Mark3 != '' THEN 1 END) as mark3_count,
            COUNT(CASE WHEN Mark4 IS NOT NULL AND Mark4 != '' THEN 1 END) as mark4_count,
            COUNT(CASE WHEN Mark5 IS NOT NULL AND Mark5 != '' THEN 1 END) as mark5_count,
            COUNT(CASE WHEN Mark6 IS NOT NULL AND Mark6 != '' THEN 1 END) as mark6_count,
            COUNT(CASE WHEN Mark7 IS NOT NULL AND Mark7 != '' THEN 1 END) as mark7_count,
            COUNT(CASE WHEN Mark8 IS NOT NULL AND Mark8 != '' THEN 1 END) as mark8_count
        FROM HORSE_MARKS
        WHERE SourceDate = ?
    """, (latest_date,))
    
    mark_stats = cursor.fetchone()
    print(f"総レコード数: {mark_stats[0]:,} 件")
    print(f"馬印1: {mark_stats[1]:,} 件 ({mark_stats[1]/mark_stats[0]*100:.1f}%)")
    print(f"馬印2: {mark_stats[2]:,} 件 ({mark_stats[2]/mark_stats[0]*100:.1f}%)")
    print(f"馬印3: {mark_stats[3]:,} 件 ({mark_stats[3]/mark_stats[0]*100:.1f}%)")
    print(f"馬印4: {mark_stats[4]:,} 件 ({mark_stats[4]/mark_stats[0]*100:.1f}%)")
    print(f"馬印5: {mark_stats[5]:,} 件 ({mark_stats[5]/mark_stats[0]*100:.1f}%)")
    print(f"馬印6: {mark_stats[6]:,} 件 ({mark_stats[6]/mark_stats[0]*100:.1f}%)")
    print(f"馬印7: {mark_stats[7]:,} 件 ({mark_stats[7]/mark_stats[0]*100:.1f}%)")
    print(f"馬印8: {mark_stats[8]:,} 件 ({mark_stats[8]/mark_stats[0]*100:.1f}%)")

    # 3. 最新日のサンプルデータ
    print("\n3. 最新日のサンプルデータ")
    cursor.execute("""
        SELECT HorseName, Mark1, Mark2, Mark3, Mark4, Mark5, Mark6, Mark7, Mark8, 
               ZI_INDEX, ZM_VALUE, R_MARK1, R_MARK2, R_MARK3
        FROM HORSE_MARKS 
        WHERE SourceDate = ? 
        LIMIT 5
    """, (latest_date,))
    
    samples = cursor.fetchall()
    for i, sample in enumerate(samples, 1):
        print(f"  サンプル{i}: {sample[0]}")
        print(f"    馬印1-8: {sample[1:9]}")
        print(f"    ZI/ZM: {sample[9]}/{sample[10]}")
        print(f"    R印1-3: {sample[11:14]}")

    # 4. 馬印の種類分析
    print("\n4. 馬印の種類分析")
    for mark_num in range(1, 9):
        cursor.execute(f"""
            SELECT Mark{mark_num}, COUNT(*) as cnt 
            FROM HORSE_MARKS 
            WHERE SourceDate = ? AND Mark{mark_num} IS NOT NULL AND Mark{mark_num} != ''
            GROUP BY Mark{mark_num} 
            ORDER BY cnt DESC 
            LIMIT 10
        """, (latest_date,))
        
        mark_types = cursor.fetchall()
        if mark_types:
            print(f"  馬印{mark_num}の種類:")
            for mark_type, count in mark_types:
                print(f"    {mark_type}: {count} 件")

    # 5. 更新履歴の確認
    print("\n5. 更新履歴の確認")
    cursor.execute("""
        SELECT SourceDate, COUNT(*) as cnt, MAX(ImportedAt) as last_import
        FROM HORSE_MARKS 
        GROUP BY SourceDate 
        ORDER BY SourceDate DESC 
        LIMIT 10
    """)
    
    history = cursor.fetchall()
    print("  日付別レコード数:")
    for date, count, last_import in history:
        print(f"    {date}: {count:,} 件 (最終更新: {last_import})")

    # 6. 問題の特定
    print("\n6. 問題の特定")
    
    # 馬印が空のレコード数
    cursor.execute("""
        SELECT COUNT(*) FROM HORSE_MARKS 
        WHERE SourceDate = ? 
        AND (Mark1 IS NULL OR Mark1 = '') 
        AND (Mark2 IS NULL OR Mark2 = '') 
        AND (Mark3 IS NULL OR Mark3 = '') 
        AND (Mark4 IS NULL OR Mark4 = '') 
        AND (Mark5 IS NULL OR Mark5 = '') 
        AND (Mark6 IS NULL OR Mark6 = '') 
        AND (Mark7 IS NULL OR Mark7 = '') 
        AND (Mark8 IS NULL OR Mark8 = '')
    """, (latest_date,))
    
    empty_marks = cursor.fetchone()[0]
    print(f"  馬印が全て空のレコード: {empty_marks:,} 件")
    
    if empty_marks > 0:
        print("  ⚠️ 馬印データが反映されていないレコードが存在します")
    else:
        print("  ✅ 馬印データは正常に反映されています")

    conn.close()

if __name__ == '__main__':
    check_horse_card_reflection()


