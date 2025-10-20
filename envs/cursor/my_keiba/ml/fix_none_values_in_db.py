#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
データベース内の'None'文字列をNULLに修正
"""
import sqlite3

def fix_none_values_in_excel_data():
    """EXCEL_DATA_*テーブル内の'None'文字列をNULLに修正"""
    print("=== データベース内'None'値修正システム ===")
    
    conn = sqlite3.connect('excel_data.db')
    cursor = conn.cursor()
    
    # 全EXCEL_DATA_*テーブルを取得
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'EXCEL_DATA_%'")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"対象テーブル数: {len(tables)}")
    
    # 修正対象列
    columns_to_fix = ['馬印1', '馬印2', '馬印3', '馬印4', '馬印5', '馬印6', '馬印7', '馬印8']
    
    total_updates = 0
    
    for table_name in tables:
        print(f"\n📋 処理中: {table_name}")
        
        # テーブルの列情報を取得
        cursor.execute(f"PRAGMA table_info({table_name})")
        existing_columns = [col[1] for col in cursor.fetchall()]
        
        table_updates = 0
        
        for col in columns_to_fix:
            if col in existing_columns:
                # 'None'文字列の数を確認
                cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {col} = 'None'")
                none_count = cursor.fetchone()[0]
                
                if none_count > 0:
                    # 'None'をNULLに更新
                    cursor.execute(f"UPDATE {table_name} SET {col} = NULL WHERE {col} = 'None'")
                    table_updates += none_count
                    print(f"  {col}: {none_count}件の'None'をNULLに修正")
        
        # 'null'文字列も修正
        for col in columns_to_fix:
            if col in existing_columns:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {col} = 'null'")
                null_count = cursor.fetchone()[0]
                
                if null_count > 0:
                    cursor.execute(f"UPDATE {table_name} SET {col} = NULL WHERE {col} = 'null'")
                    table_updates += null_count
                    print(f"  {col}: {null_count}件の'null'をNULLに修正")
        
        total_updates += table_updates
        if table_updates > 0:
            print(f"  ✅ {table_name}: {table_updates}件修正")
        else:
            print(f"  ✅ {table_name}: 修正不要")
    
    conn.commit()
    conn.close()
    
    print(f"\n📊 修正完了: 総計{total_updates}件の'None'/'null'をNULLに修正")
    return total_updates

def verify_fix():
    """修正結果の確認"""
    print("\n=== 修正結果確認 ===")
    
    conn = sqlite3.connect('excel_data.db')
    cursor = conn.cursor()
    
    # EXCEL_DATA_20240810でブラックシールドを確認
    table_name = 'EXCEL_DATA_20240810'
    horse_name = 'ブラックシールド'
    
    query = f"SELECT 馬名S, 馬印1, 馬印2, 馬印3, 馬印4, 馬印5 FROM {table_name} WHERE 馬名S = ?"
    cursor.execute(query, (horse_name,))
    result = cursor.fetchone()
    
    if result:
        print(f"🐎 {horse_name} (修正後):")
        print(f"  馬印1: {result[1]} ({'NULL' if result[1] is None else 'データあり'})")
        print(f"  馬印2: {result[2]} ({'NULL' if result[2] is None else 'データあり'})")
        print(f"  馬印3: {result[3]} ({'NULL' if result[3] is None else 'データあり'})")
        print(f"  馬印4: {result[4]} ({'NULL' if result[4] is None else 'データあり'})")
        print(f"  馬印5: {result[5]} ({'NULL' if result[5] is None else 'データあり'})")
    
    # 全体統計
    cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE 馬印1 = 'None'")
    remaining_none = cursor.fetchone()[0]
    print(f"\n📊 残存'None'文字列: {remaining_none}件")
    
    conn.close()

def main():
    """メイン処理"""
    print("🔧 データベース'None'値修正システム")
    print("=" * 50)
    
    # 1. 'None'値を修正
    updates = fix_none_values_in_excel_data()
    
    # 2. 修正結果確認
    verify_fix()
    
    print("\n" + "=" * 50)
    print("📋 次のステップ:")
    print("1. JVMonitor.exeを再起動")
    print("2. 馬詳細画面でブラックシールドを確認")
    print("3. 8/10のデータが正しく表示されるか確認")

if __name__ == "__main__":
    main()
