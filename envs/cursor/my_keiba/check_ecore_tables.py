#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ecore.dbのテーブル構造確認
"""
import sqlite3

def check_ecore_tables():
    """ecore.dbのテーブル構造を確認"""
    print("=== ecore.db テーブル構造確認 ===")
    
    conn = sqlite3.connect('ecore.db')
    cursor = conn.cursor()
    
    # 全テーブル一覧
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    print(f"全テーブル数: {len(tables)}")
    print("テーブル一覧:")
    for table in tables:
        print(f"  - {table[0]}")
    
    # N_UMA関連テーブルを検索
    print("\n=== N_UMA関連テーブル ===")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'N_UMA%'")
    uma_tables = cursor.fetchall()
    
    if uma_tables:
        print("N_UMA関連テーブル:")
        for table in uma_tables:
            print(f"  - {table[0]}")
    else:
        print("❌ N_UMA関連テーブルが見つかりません")
    
    # N_RACE関連テーブルを検索
    print("\n=== N_RACE関連テーブル ===")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'N_RACE%'")
    race_tables = cursor.fetchall()
    
    if race_tables:
        print("N_RACE関連テーブル:")
        for table in race_tables:
            print(f"  - {table[0]}")
    else:
        print("❌ N_RACE関連テーブルが見つかりません")
    
    conn.close()

if __name__ == "__main__":
    check_ecore_tables()
