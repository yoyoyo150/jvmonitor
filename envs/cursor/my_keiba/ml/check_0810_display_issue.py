#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
8/10データの表示問題確認
画像で見える馬名で実際のデータを確認
"""
import sqlite3

def check_0810_horse_data():
    """8/10の特定馬データ確認"""
    print("=== 8/10データの詳細確認 ===")
    
    # 画像で見える馬名
    test_horses = [
        "イタダキマス",
        "オメガステークス", 
        "ブラックシールド"
    ]
    
    conn = sqlite3.connect('excel_data.db')
    cursor = conn.cursor()
    
    table_name = 'EXCEL_DATA_20240810'
    
    for horse_name in test_horses:
        print(f"\n🐎 対象馬: {horse_name}")
        
        # 完全一致検索
        query = f"SELECT 馬名S, 馬印1, 馬印2, 馬印3, 馬印4, 馬印5, ZM, ZI指数, オリジナル, 加速 FROM {table_name} WHERE 馬名S = ?"
        cursor.execute(query, (horse_name,))
        result = cursor.fetchone()
        
        if result:
            print(f"✅ {horse_name} のデータ発見:")
            print(f"  馬印1: '{result[1]}'")
            print(f"  馬印2: '{result[2]}'")
            print(f"  馬印3: '{result[3]}'")
            print(f"  馬印4: '{result[4]}'")
            print(f"  馬印5: '{result[5]}'")
            print(f"  ZM: '{result[6]}'")
            print(f"  ZI指数: '{result[7]}'")
            print(f"  オリジナル: '{result[8]}'")
            print(f"  加速: '{result[9]}'")
        else:
            print(f"❌ {horse_name} のデータが見つかりません")
            
            # 部分一致で検索
            like_query = f"SELECT 馬名S FROM {table_name} WHERE 馬名S LIKE ?"
            cursor.execute(like_query, (f'%{horse_name[:3]}%',))
            similar = cursor.fetchall()
            if similar:
                print("  類似する馬名:")
                for s in similar[:5]:  # 最初の5件のみ
                    print(f"    {s[0]}")
    
    # 8/10の全データ統計
    print(f"\n📊 {table_name} 統計:")
    
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    total_count = cursor.fetchone()[0]
    print(f"  総レコード数: {total_count}")
    
    # NULL/空文字でないデータの数
    columns_to_check = ['馬印1', '馬印2', '馬印3', 'ZM', 'ZI指数', 'オリジナル', '加速']
    
    for col in columns_to_check:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {col} IS NOT NULL AND {col} != ''")
        non_null_count = cursor.fetchone()[0]
        print(f"  {col}データ有り: {non_null_count}/{total_count} ({non_null_count/total_count*100:.1f}%)")
    
    # サンプルデータ表示
    print(f"\n📋 サンプルデータ（最初の3件）:")
    cursor.execute(f"SELECT 馬名S, 馬印1, 馬印2, ZM, ZI指数 FROM {table_name} LIMIT 3")
    samples = cursor.fetchall()
    
    for i, sample in enumerate(samples, 1):
        print(f"  {i}. {sample[0]}: 馬印1='{sample[1]}', 馬印2='{sample[2]}', ZM='{sample[3]}', ZI指数='{sample[4]}'")
    
    conn.close()

def check_horsedetailform_path():
    """HorseDetailForm.csがexcel_data.dbを正しく参照しているか確認"""
    print("\n=== HorseDetailForm.cs パス確認 ===")
    
    import os
    
    # 現在のexcel_data.dbパス
    current_path = os.path.abspath('excel_data.db')
    print(f"📁 現在のexcel_data.db: {current_path}")
    print(f"📁 ファイル存在: {'✅' if os.path.exists(current_path) else '❌'}")
    
    # JVMonitorが期待するパス（appsettings.jsonから）
    expected_path = "C:\\my_project_folder\\envs\\cursor\\my_keiba\\excel_data.db"
    print(f"📁 JVMonitor期待パス: {expected_path}")
    print(f"📁 パス一致: {'✅' if current_path == expected_path else '❌'}")
    
    if os.path.exists(current_path):
        file_size = os.path.getsize(current_path)
        print(f"📊 ファイルサイズ: {file_size:,} bytes")

def main():
    """メイン処理"""
    print("🔍 8/10データ表示問題確認システム")
    print("=" * 50)
    
    # 1. 8/10データの詳細確認
    check_0810_horse_data()
    
    # 2. パス確認
    check_horsedetailform_path()
    
    print("\n" + "=" * 50)
    print("📋 問題の可能性:")
    print("1. データは存在するが、値がNULLまたは空文字")
    print("2. HorseDetailForm.csの表示ロジックに問題")
    print("3. 色設定により見えにくくなっている")
    print("4. データ形式の不整合")

if __name__ == "__main__":
    main()
