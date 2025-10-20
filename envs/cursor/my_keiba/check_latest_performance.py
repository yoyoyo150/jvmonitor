import sqlite3
import sys
import io
import pandas as pd
import os
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

DB_PATH = 'ecore.db'

def check_latest_performance():
    print("=== 左上の「最新成績」について確認 ===\n")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. HORSE_MARKSテーブルの構造を確認
    print("1. HORSE_MARKSテーブルの構造を確認")
    cursor.execute("PRAGMA table_info(HORSE_MARKS)")
    columns = cursor.fetchall()
    
    print("成績関連のカラム:")
    performance_columns = []
    for col in columns:
        cid, name, type_name, not_null, default_value, pk = col
        if any(keyword in name.upper() for keyword in ['CHAKU', 'RANK', 'RATE', 'PERFORMANCE', 'SCORE', 'INDEX']):
            performance_columns.append(name)
            print(f"  {name}: {type_name}")
    
    if not performance_columns:
        print("  成績関連のカラムが見つかりませんでした")

    # 2. 最新のデータから成績情報を確認
    print("\n2. 最新のデータから成績情報を確認")
    cursor.execute("SELECT MAX(SourceDate) FROM HORSE_MARKS")
    latest_date = cursor.fetchone()[0]
    print(f"最新の日付: {latest_date}")
    
    # 最新日付のデータから成績関連の情報を取得
    cursor.execute(f"""
        SELECT HorseName, CHAKU, ZI_RANK, RACE_CLASS_C, SEX, AGE, JOCKEY, KINRYO
        FROM HORSE_MARKS 
        WHERE SourceDate = '{latest_date}'
        LIMIT 10
    """)
    
    latest_data = cursor.fetchall()
    print(f"\n最新日付（{latest_date}）の成績データ（最初の10件）:")
    for data in latest_data:
        horse_name, chaku, zi_rank, race_class, sex, age, jockey, kinryo = data
        print(f"  {horse_name}: 着順={chaku}, ZI順位={zi_rank}, クラス={race_class}, 性別={sex}, 年齢={age}, 騎手={jockey}, 斤量={kinryo}")

    # 3. 成績データの統計
    print("\n3. 成績データの統計")
    cursor.execute(f"""
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN CHAKU IS NOT NULL AND CHAKU != '' THEN 1 END) as chaku_count,
            COUNT(CASE WHEN ZI_RANK IS NOT NULL AND ZI_RANK != '' THEN 1 END) as zi_rank_count,
            COUNT(CASE WHEN RACE_CLASS_C IS NOT NULL AND RACE_CLASS_C != '' THEN 1 END) as race_class_count
        FROM HORSE_MARKS 
        WHERE SourceDate = '{latest_date}'
    """)
    
    stats = cursor.fetchone()
    total, chaku_count, zi_rank_count, race_class_count = stats
    print(f"総レコード数: {total} 件")
    print(f"着順データ: {chaku_count} 件 ({chaku_count/total*100:.1f}%)")
    print(f"ZI順位データ: {zi_rank_count} 件 ({zi_rank_count/total*100:.1f}%)")
    print(f"レースクラスデータ: {race_class_count} 件 ({race_class_count/total*100:.1f}%)")

    # 4. 着順データの詳細分析
    print("\n4. 着順データの詳細分析")
    cursor.execute(f"""
        SELECT CHAKU, COUNT(*) as count
        FROM HORSE_MARKS 
        WHERE SourceDate = '{latest_date}' AND CHAKU IS NOT NULL AND CHAKU != ''
        GROUP BY CHAKU
        ORDER BY CAST(CHAKU AS INTEGER)
    """)
    
    chaku_stats = cursor.fetchall()
    print("着順別の件数:")
    for chaku, count in chaku_stats:
        print(f"  {chaku}着: {count} 件")

    # 5. 特定の馬の最新成績を確認
    print("\n5. 特定の馬の最新成績を確認")
    test_horse = "アッチャゴーラ"
    cursor.execute(f"""
        SELECT SourceDate, CHAKU, ZI_RANK, RACE_CLASS_C, JOCKEY, KINRYO
        FROM HORSE_MARKS 
        WHERE HorseName = '{test_horse}'
        ORDER BY SourceDate DESC
        LIMIT 5
    """)
    
    horse_data = cursor.fetchall()
    if horse_data:
        print(f"{test_horse}の最新成績（最新5件）:")
        for data in horse_data:
            date, chaku, zi_rank, race_class, jockey, kinryo = data
            print(f"  {date}: 着順={chaku}, ZI順位={zi_rank}, クラス={race_class}, 騎手={jockey}, 斤量={kinryo}")
    else:
        print(f"{test_horse}のデータが見つかりませんでした")

    # 6. 成績データの説明
    print("\n6. 成績データの説明")
    print("「最新成績」に表示される可能性のあるデータ:")
    print("  - CHAKU: 着順（1着、2着、3着など）")
    print("  - ZI_RANK: ZI指数の順位")
    print("  - RACE_CLASS_C: レースクラス（G1、G2、G3、重賞など）")
    print("  - SEX: 性別（牡、牝、セなど）")
    print("  - AGE: 年齢")
    print("  - JOCKEY: 騎手名")
    print("  - KINRYO: 斤量")
    print("  - その他の指数や評価データ")

    conn.close()

if __name__ == '__main__':
    check_latest_performance()


