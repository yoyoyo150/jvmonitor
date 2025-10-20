#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JVMonitor「ないない」問題の簡単解決スクリプト
"""

import sqlite3
import os

def simple_fix():
    """簡単な修正を実行"""
    
    print("=== JVMonitor「ないない」問題の簡単解決 ===")
    
    # 1. データベースファイルの存在確認
    db_files = ['excel_data.db', 'ecore.db']
    for db_file in db_files:
        if os.path.exists(db_file):
            print(f"OK: {db_file} が存在します")
        else:
            print(f"NG: {db_file} が見つかりません")
            return False
    
    # 2. データベース最適化
    print("\nデータベースを最適化中...")
    
    try:
        # excel_data.dbの最適化
        conn = sqlite3.connect('excel_data.db')
        cursor = conn.cursor()
        
        # インデックス作成
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_source_date ON HORSE_MARKS(SourceDate)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_horse_name ON HORSE_MARKS(HorseName)")
        
        # 最適化
        cursor.execute("VACUUM")
        cursor.execute("ANALYZE")
        
        conn.close()
        print("OK: excel_data.db の最適化完了")
        
        # ecore.dbの最適化
        conn = sqlite3.connect('ecore.db')
        cursor = conn.cursor()
        
        # 主要テーブルのインデックス作成
        tables = ['N_RACE', 'N_UMA_RACE', 'N_HANRO']
        for table in tables:
            try:
                cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{table}_makedate ON {table}(MakeDate)")
                cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{table}_year_monthday ON {table}(Year, MonthDay)")
            except:
                pass  # テーブルが存在しない場合はスキップ
        
        cursor.execute("VACUUM")
        cursor.execute("ANALYZE")
        
        conn.close()
        print("OK: ecore.db の最適化完了")
        
    except Exception as e:
        print(f"NG: 最適化エラー - {e}")
        return False
    
    # 3. データ確認
    print("\nデータ確認中...")
    
    try:
        conn = sqlite3.connect('excel_data.db')
        cursor = conn.cursor()
        
        # 最新3日分のデータ確認
        cursor.execute("""
            SELECT SourceDate, COUNT(*) 
            FROM HORSE_MARKS 
            GROUP BY SourceDate 
            ORDER BY SourceDate DESC 
            LIMIT 3
        """)
        results = cursor.fetchall()
        
        print("最新の馬印データ:")
        for date, count in results:
            print(f"  {date}: {count}件")
        
        conn.close()
        
    except Exception as e:
        print(f"NG: データ確認エラー - {e}")
        return False
    
    print("\n=== 解決完了 ===")
    print("次の手順:")
    print("1. JVMonitorを一度閉じる")
    print("2. JVMonitorを再起動")
    print("3. データが正しく表示されることを確認")
    
    return True

if __name__ == "__main__":
    simple_fix()








