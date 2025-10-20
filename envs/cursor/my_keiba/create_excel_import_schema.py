#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excelインポート用スキーマ作成スクリプト
"""
import sqlite3
from pathlib import Path

def create_excel_import_schema(db_path="ecore.db"):
    """Excelインポート用スキーマを作成"""
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    
    sql_path = Path("sql/create_excel_import_schema.sql")
    sql_script = sql_path.read_text(encoding="utf-8")
    
    # 各SQL文を個別に実行
    for statement in sql_script.split(';'):
        statement = statement.strip()
        if statement:
            try:
                cur.execute(statement)
                print(f"[ok] Executed: {statement[:50]}...")
            except sqlite3.OperationalError as e:
                # ビューが既に存在する場合のエラーは無視
                if "already exists" in str(e):
                    print(f"[info] View/Table already exists, skipping: {statement[:50]}...")
                else:
                    print(f"[error] {e}: {statement[:100]}...")
            except Exception as e:
                print(f"[error] {e}: {statement[:100]}...")
    
    con.commit()
    con.close()
    print(f"[ok] Schema from {sql_path} applied.")

if __name__ == "__main__":
    create_excel_import_schema()




