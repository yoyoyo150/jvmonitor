#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
シンプルなVLOOKUP方式でオクタヴィアヌスのデータを抜き出し
"""
import sqlite3

def simple_vlookup_test():
    """オクタヴィアヌスのデータをVLOOKUP方式で抜き出し"""
    print("=== オクタヴィアヌスのデータ直接検索（VLOOKUP方式） ===")
    
    conn = sqlite3.connect('excel_data.db')
    cursor = conn.cursor()
    
    # オクタヴィアヌスを検索
    horse_name = 'オクタヴィアヌス'
    
    # 全テーブルから検索
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'EXCEL_DATA_%' ORDER BY name DESC")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"対象馬: {horse_name}")
    print(f"検索対象テーブル数: {len(tables)}")
    
    found_data = []
    
    for table in tables[:20]:  # 最新20テーブルを検索
        try:
            cursor.execute(f"SELECT * FROM {table} WHERE 馬名S = ?", (horse_name,))
            result = cursor.fetchone()
            
            if result:
                # カラム名取得
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [col[1] for col in cursor.fetchall()]
                
                # 日付抽出
                date_part = table.replace('EXCEL_DATA_', '')
                formatted_date = f"{date_part[:4]}/{date_part[4:6]}/{date_part[6:8]}"
                
                print(f"\n✅ {formatted_date} ({table}):")
                
                # 重要な列のデータを表示（VLOOKUP結果）
                important_cols = ['馬名S', '馬印1', '馬印2', '馬印3', 'ZM', 'ZI指数', 'オリジナル', '加速']
                
                for i, col_name in enumerate(columns):
                    if col_name in important_cols and i < len(result):
                        print(f"  {col_name}: {result[i]}")
                
                found_data.append((formatted_date, table, result))
                
        except Exception as e:
            continue
    
    if not found_data:
        print(f"\n❌ {horse_name} のデータが見つかりません")
        
        # 類似する馬名を検索
        print("\n類似する馬名を検索中...")
        for table in tables[:5]:
            try:
                cursor.execute(f"SELECT 馬名S FROM {table} WHERE 馬名S LIKE ?", (f"%オクタ%",))
                similar = cursor.fetchall()
                if similar:
                    print(f"{table}: {[s[0] for s in similar]}")
            except:
                continue
    else:
        print(f"\n📊 {horse_name} のデータが {len(found_data)} 日分見つかりました")
    
    conn.close()
    return found_data

def test_any_horse_from_excel():
    """エクセル画像に見える任意の馬でテスト"""
    print(f"\n=== エクセル画像に見える馬でのVLOOKUPテスト ===")
    
    # 画像から読み取れる馬名
    test_horses = [
        "オクタヴィアヌス",
        "マイネルエポック", 
        "ラブリーミライ",
        "ウインベラーノ",
        "ブルータス"
    ]
    
    conn = sqlite3.connect('excel_data.db')
    cursor = conn.cursor()
    
    # 最新のテーブルで検索
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'EXCEL_DATA_%' ORDER BY name DESC LIMIT 1")
    latest_table = cursor.fetchone()[0]
    
    print(f"検索対象テーブル: {latest_table}")
    
    for horse_name in test_horses:
        cursor.execute(f"SELECT 馬名S, 馬印1, 馬印2, ZM, ZI指数 FROM {latest_table} WHERE 馬名S = ?", (horse_name,))
        result = cursor.fetchone()
        
        if result:
            print(f"✅ {horse_name}: 馬印1={result[1]}, 馬印2={result[2]}, ZM={result[3]}, ZI指数={result[4]}")
        else:
            print(f"❌ {horse_name}: 見つからず")
    
    conn.close()

def main():
    """メイン処理"""
    print("🔍 シンプルVLOOKUP方式テスト")
    print("=" * 60)
    
    # 1. オクタヴィアヌス検索
    found_data = simple_vlookup_test()
    
    # 2. 他の馬でもテスト
    test_any_horse_from_excel()
    
    print("\n" + "=" * 60)
    print("📋 VLOOKUPの考え方:")
    print("1. 馬名をキーにしてEXCEL_DATA_*テーブルから直接検索")
    print("2. 該当行の必要な列データを抜き出し")
    print("3. HorseDetailForm.csでこの方式を使用すれば即座に表示")

if __name__ == "__main__":
    main()
