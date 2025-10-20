#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
8/10 VLOOKUPテスト
"""
import sqlite3

def test_0810_vlookup():
    """8/10のVLOOKUPテスト"""
    print("=== 8/10 VLOOKUPテスト ===")
    
    conn = sqlite3.connect('excel_data.db')
    cursor = conn.cursor()
    
    # 8/10のテーブルから画像に見える馬を検索
    table_name = 'EXCEL_DATA_20250810'
    test_horses = ['オクタヴィアヌス', 'イタダキマス', 'ブラックシールド']
    
    print(f"検索テーブル: {table_name}")
    
    for horse_name in test_horses:
        cursor.execute(f"SELECT 馬名S, 馬印1, 馬印2, 馬印3, ZM, ZI指数, オリジナル, 加速 FROM {table_name} WHERE 馬名S = ?", (horse_name,))
        result = cursor.fetchone()
        
        if result:
            print(f"\n✅ {horse_name}:")
            print(f"  馬印1: \"{result[1]}\"")
            print(f"  馬印2: {result[2]}")
            print(f"  馬印3: {result[3]}")
            print(f"  ZM: {result[4]}")
            print(f"  ZI指数: {result[5]}")
            print(f"  オリジナル: {result[6]}")
            print(f"  加速: {result[7]}")
        else:
            print(f"❌ {horse_name}: 見つからず")
    
    # 8/10で実際に存在する馬のサンプル
    print(f"\n=== 8/10 実在馬サンプル ===")
    cursor.execute(f"SELECT 馬名S, 馬印1, 馬印2, ZM, ZI指数 FROM {table_name} WHERE 馬印1 IS NOT NULL AND 馬印1 != '' LIMIT 3")
    samples = cursor.fetchall()
    
    for sample in samples:
        print(f"✅ {sample[0]}: 馬印1=\"{sample[1]}\", 馬印2={sample[2]}, ZM={sample[3]}, ZI指数={sample[4]}")
    
    conn.close()

if __name__ == "__main__":
    test_0810_vlookup()
