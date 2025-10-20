#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ビュー作成スクリプト
"""
import sqlite3
from pathlib import Path

def create_views(db_path="ecore.db"):
    """ビューを作成"""
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    
    # sql/create_views.sql を読み込んで実行
    sql_path = Path("sql/create_views.sql")
    sql = sql_path.read_text(encoding="utf-8")
    
    # セミコロンで分割して実行
    for statement in sql.split(";"):
        statement = statement.strip()
        if statement:
            try:
                cur.execute(statement)
                print(f"[ok] executed: {statement[:50]}...")
            except Exception as e:
                print(f"[error] {e}")
                print(f"  statement: {statement[:100]}...")
    
    con.commit()
    con.close()
    print("[ok] views created")

if __name__ == "__main__":
    create_views()




