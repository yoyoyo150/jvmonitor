#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日単位でのエクセルデータ表示問題確認
"""
import sqlite3
from datetime import datetime, timedelta

def check_daily_excel_data():
    """日単位でのエクセルデータ状況確認"""
    print("=== 日単位でのエクセルデータ表示問題確認 ===")
    
    # 画像で見える日付を確認
    visible_dates = [
        "2025/08/10",  # 画像で見える日付
        "2024/11/24", 
        "2024/02/17",
        "2023/11/26",
        "2023/06/12",
        "2023/05/27",
        "2023/04/08",
        "2023/01/08"
    ]
    
    conn = sqlite3.connect('excel_data.db')
    cursor = conn.cursor()
    
    print("各日付のエクセルデータ状況:")
    
    for date_str in visible_dates:
        # 日付をYYYYMMDD形式に変換
        year, month, day = date_str.split('/')
        date_key = f"{year}{month.zfill(2)}{day.zfill(2)}"
        table_name = f"EXCEL_DATA_{date_key}"
        
        print(f"\n📅 {date_str} ({table_name}):")
        
        # テーブル存在確認
        cursor.execute("SELECT name FROM sqlite_master WHERE type=? AND name=?", ('table', table_name))
        exists = cursor.fetchone()
        
        if exists:
            # レコード数確認
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            total_count = cursor.fetchone()[0]
            
            # 馬印データの充足率確認
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE 馬印1 IS NOT NULL AND 馬印1 != '' AND 馬印1 != 'None'")
                mark1_count = cursor.fetchone()[0]
                
                cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE 馬印2 IS NOT NULL AND 馬印2 != '' AND 馬印2 != 'None'")
                mark2_count = cursor.fetchone()[0]
                
                cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE ZM IS NOT NULL AND ZM != ''")
                zm_count = cursor.fetchone()[0]
                
                print(f"  ✅ テーブル存在: {total_count}頭")
                print(f"  📊 馬印1データ: {mark1_count}/{total_count} ({mark1_count/total_count*100:.1f}%)")
                print(f"  📊 馬印2データ: {mark2_count}/{total_count} ({mark2_count/total_count*100:.1f}%)")
                print(f"  📊 ZMデータ: {zm_count}/{total_count} ({zm_count/total_count*100:.1f}%)")
                
                # サンプルデータ確認
                cursor.execute(f"SELECT 馬名S, 馬印1, 馬印2, ZM FROM {table_name} WHERE 馬印2 IS NOT NULL LIMIT 1")
                sample = cursor.fetchone()
                if sample:
                    print(f"  例: {sample[0]} - 馬印1:{sample[1]}, 馬印2:{sample[2]}, ZM:{sample[3]}")
                    
            except Exception as e:
                print(f"  ⚠️  データ確認エラー: {e}")
        else:
            print(f"  ❌ テーブル不存在")
    
    # 最近の日付で欠損チェック
    print(f"\n=== 最近7日間の状況 ===")
    today = datetime.now()
    for i in range(7):
        check_date = today - timedelta(days=i)
        date_key = check_date.strftime('%Y%m%d')
        table_name = f"EXCEL_DATA_{date_key}"
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type=? AND name=?", ('table', table_name))
        exists = cursor.fetchone()
        
        if exists:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"✅ {check_date.strftime('%Y/%m/%d')} ({date_key}): {count}頭")
        else:
            print(f"❌ {check_date.strftime('%Y/%m/%d')} ({date_key}): テーブルなし")
    
    conn.close()

def check_horsedetailform_date_logic():
    """HorseDetailForm.csの日付別データ取得ロジック確認"""
    print(f"\n=== HorseDetailForm.cs 日付別データ取得確認 ===")
    
    conn = sqlite3.connect('excel_data.db')
    cursor = conn.cursor()
    
    # HorseDetailForm.csと同じロジックでテーブル一覧取得
    table_query = "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'EXCEL_DATA_%' ORDER BY name DESC"
    cursor.execute(table_query)
    table_names = [row[0] for row in cursor.fetchall()]
    
    print(f"検出されたEXCEL_DATAテーブル数: {len(table_names)}")
    print("最新10テーブル:")
    
    for i, table_name in enumerate(table_names[:10]):
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        
        # 日付部分を抽出
        date_part = table_name.replace('EXCEL_DATA_', '')
        if len(date_part) == 8:
            formatted_date = f"{date_part[:4]}/{date_part[4:6]}/{date_part[6:8]}"
        else:
            formatted_date = date_part
        
        print(f"  {i+1:2d}. {formatted_date} ({table_name}): {count}頭")
    
    conn.close()

def main():
    """メイン処理"""
    print("🔍 日単位エクセルデータ確認システム")
    print("=" * 60)
    
    # 1. 日単位データ確認
    check_daily_excel_data()
    
    # 2. HorseDetailFormロジック確認
    check_horsedetailform_date_logic()
    
    print("\n" + "=" * 60)
    print("📋 問題の可能性:")
    print("1. 特定日付のEXCEL_DATA_*テーブルが存在しない")
    print("2. テーブルは存在するが、馬印データが空またはNone")
    print("3. HorseDetailForm.csが古いテーブルを優先して読んでいる")
    print("4. 日付フォーマットの不整合")

if __name__ == "__main__":
    main()
