#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
馬詳細画面でのデータ反映確認システム
HorseDetailForm.csがどのようにデータを取得しているかを検証
"""
import sqlite3
import os
from datetime import datetime

def check_horse_excel_data(horse_name, target_dates=None):
    """指定された馬のエクセルデータ取得状況確認"""
    print(f"=== 馬詳細データ確認: {horse_name} ===")
    
    if target_dates is None:
        target_dates = ['20240810', '20240914', '20240922', '20250913']
    
    conn = sqlite3.connect('excel_data.db')
    cursor = conn.cursor()
    
    # 正規化された馬名（スペース除去）
    normalized_horse_name = horse_name.replace(' ', '').replace('　', '')
    
    found_data = {}
    
    for date in target_dates:
        table_name = f"EXCEL_DATA_{date}"
        
        # テーブル存在確認
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if not cursor.fetchone():
            print(f"❌ {date}: テーブル {table_name} が存在しません")
            continue
        
        # 馬名での検索（複数パターン）
        search_patterns = [
            horse_name,           # 元の馬名
            normalized_horse_name, # 正規化済み馬名
        ]
        
        found = False
        for pattern in search_patterns:
            try:
                # 馬名S列での検索
                query = f"SELECT 馬名S, 馬印1, 馬印2, ZM, ZI指数, オリジナル, 加速 FROM {table_name} WHERE 馬名S = ?"
                cursor.execute(query, (pattern,))
                result = cursor.fetchone()
                
                if result:
                    found_data[date] = {
                        'horse_name': result[0],
                        'mark1': result[1],
                        'mark2': result[2], 
                        'zm': result[3],
                        'zi': result[4],
                        'original': result[5],
                        'acceleration': result[6]
                    }
                    print(f"✅ {date}: データ発見 - 馬印1:{result[1]}, 馬印2:{result[2]}, ZM:{result[3]}")
                    found = True
                    break
                    
            except Exception as e:
                print(f"⚠️  {date}: 検索エラー - {e}")
        
        if not found:
            print(f"❌ {date}: 馬名 '{horse_name}' のデータが見つかりません")
    
    conn.close()
    return found_data

def check_horsedetailform_logic():
    """HorseDetailForm.csのロジック再現確認"""
    print("\n=== HorseDetailForm.cs ロジック再現 ===")
    
    conn = sqlite3.connect('excel_data.db')
    cursor = conn.cursor()
    
    # 利用可能なEXCEL_DATAテーブルを取得（HorseDetailForm.csと同じロジック）
    table_query = "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'EXCEL_DATA_%' ORDER BY name DESC"
    cursor.execute(table_query)
    table_names = [row[0] for row in cursor.fetchall()]
    
    print(f"検出されたEXCEL_DATAテーブル数: {len(table_names)}")
    
    # 各テーブルの基本情報
    for table_name in table_names[:10]:  # 最新10個のみ表示
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        
        # 馬名S列の存在確認
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        has_horse_name = '馬名S' in columns
        
        print(f"  {table_name}: {count}件, 馬名S列: {'✅' if has_horse_name else '❌'}")
    
    conn.close()

def test_specific_horses():
    """画像で見える特定の馬でテスト"""
    print("\n=== 特定馬でのテスト ===")
    
    # 画像から読み取れる馬名
    test_horses = [
        "ブラックシールド",  # 画像の一番上の馬
        # 他の馬名も必要に応じて追加
    ]
    
    for horse_name in test_horses:
        data = check_horse_excel_data(horse_name)
        
        if data:
            print(f"\n📊 {horse_name} の取得データ:")
            for date, info in data.items():
                print(f"  {date}: 馬印1={info['mark1']}, 馬印2={info['mark2']}, ZM={info['zm']}")
        else:
            print(f"\n❌ {horse_name}: データが見つかりませんでした")

def check_db_registration_system():
    """DB登録・引き出しシステムの確認"""
    print("\n=== DB登録・引き出しシステム確認 ===")
    
    # 1. excel_data.dbの状況
    conn = sqlite3.connect('excel_data.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'EXCEL_DATA_%'")
    tables = cursor.fetchall()
    
    print(f"📊 EXCEL_DATA_*テーブル数: {len(tables)}")
    
    # 2. 各テーブルのデータ量
    total_records = 0
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        total_records += count
    
    print(f"📊 総レコード数: {total_records}")
    
    # 3. HorseDetailForm.csが使用するパス確認
    excel_db_path = os.path.abspath('excel_data.db')
    print(f"📁 excel_data.db パス: {excel_db_path}")
    print(f"📁 ファイル存在: {'✅' if os.path.exists(excel_db_path) else '❌'}")
    
    conn.close()

def main():
    """メイン処理"""
    print("🔍 馬詳細画面データ反映確認システム")
    print("=" * 60)
    
    # 1. HorseDetailFormロジック確認
    check_horsedetailform_logic()
    
    # 2. DB登録・引き出しシステム確認
    check_db_registration_system()
    
    # 3. 特定馬でのテスト
    test_specific_horses()
    
    # 4. 問題の日付データ確認
    print("\n=== 問題日付のデータ状況 ===")
    problem_dates = ['20240810', '20240914', '20240922', '20250913']
    
    conn = sqlite3.connect('excel_data.db')
    cursor = conn.cursor()
    
    for date in problem_dates:
        table_name = f"EXCEL_DATA_{date}"
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        exists = cursor.fetchone()
        
        if exists:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            
            # サンプルデータ確認
            cursor.execute(f"SELECT 馬名S FROM {table_name} LIMIT 3")
            samples = [row[0] for row in cursor.fetchall()]
            
            print(f"✅ {date}: {count}件 - 例: {', '.join(samples)}")
        else:
            print(f"❌ {date}: テーブルなし")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("📋 次のアクション:")
    print("1. JVMonitor.exeを再起動")
    print("2. 馬詳細画面で上記の馬を確認")
    print("3. エクセルデータが表示されるか確認")

if __name__ == "__main__":
    main()
