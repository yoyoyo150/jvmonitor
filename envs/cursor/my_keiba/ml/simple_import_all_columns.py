#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
エクセルデータ全列インポートスクリプト（シンプル版）
全ての列をそのまま取り込む
"""
import sys
import os
import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def main():
    """メイン関数"""
    try:
        print("=== エクセルデータ全列インポート開始 ===")
        
        # プロジェクトルートに移動
        current_dir = Path.cwd()
        project_root = current_dir
        while not (project_root / "yDate").exists() and project_root.parent != project_root:
            project_root = project_root.parent
        
        if not (project_root / "yDate").exists():
            print("❌ プロジェクトルートが見つかりません")
            return 1
        
        os.chdir(project_root)
        print(f"プロジェクトルート: {project_root}")
        
        # データベース接続
        db_path = "excel_data.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # yDateディレクトリの最新ファイルを処理
        yDate_dir = Path("yDate")
        excel_files = list(yDate_dir.glob("*.xlsx")) + list(yDate_dir.glob("*.csv"))
        excel_files.sort()
        
        # 最新5ファイルのみ処理
        latest_files = excel_files[-5:]
        print(f"処理対象ファイル数: {len(latest_files)}")
        
        total_imported = 0
        
        for file_path in latest_files:
            print(f"処理中: {file_path.name}")
            
            try:
                # エクセルファイル読み込み
                if file_path.suffix == '.xlsx':
                    df = pd.read_excel(file_path, dtype=str, engine='openpyxl').fillna("")
                elif file_path.suffix == '.csv':
                    df = pd.read_csv(file_path, dtype=str, encoding='utf-8').fillna("")
                else:
                    continue
                
                print(f"  列数: {len(df.columns)}, 行数: {len(df)}")
                
                # テーブル名を動的に作成（ファイル名ベース）
                table_name = f"EXCEL_DATA_{file_path.stem.replace('-', '_').replace('.', '_')}"
                
                # テーブルを削除して再作成
                cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                
                # 列名を安全な形に変換
                safe_columns = []
                for col in df.columns:
                    # 特殊文字を置換
                    safe_col = str(col).replace(' ', '_').replace('(', '_').replace(')', '_').replace('-', '_').replace('.', '_').replace('/', '_')
                    # 数字で始まる場合はCOL_を付ける
                    if safe_col and safe_col[0].isdigit():
                        safe_col = f"COL_{safe_col}"
                    # 空の場合はCOL_番号
                    if not safe_col or safe_col == '_':
                        safe_col = f"COL_{len(safe_columns)}"
                    safe_columns.append(safe_col)
                
                # CREATE TABLE文を動的に生成
                columns_def = ", ".join([f"{col} TEXT" for col in safe_columns])
                create_sql = f"""
                    CREATE TABLE {table_name} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        {columns_def},
                        SourceFile TEXT,
                        ImportedAt DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """
                
                cursor.execute(create_sql)
                print(f"  テーブル作成: {table_name} ({len(safe_columns)}列)")
                
                # データ挿入
                records_to_insert = []
                for index, row in df.iterrows():
                    record = {}
                    
                    # 全ての列をそのまま取り込み
                    for orig_col, safe_col in zip(df.columns, safe_columns):
                        record[safe_col] = str(row[orig_col] or "").strip()
                    
                    record['SourceFile'] = file_path.name
                    record['ImportedAt'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    records_to_insert.append(record)
                
                # データベースに挿入
                if records_to_insert:
                    column_names = list(records_to_insert[0].keys())
                    placeholders = ", ".join(f":{name}" for name in column_names)
                    
                    sql = f"""
                        INSERT INTO {table_name} ({', '.join(column_names)})
                        VALUES ({placeholders})
                    """
                    
                    cursor.executemany(sql, records_to_insert)
                    conn.commit()
                    
                    print(f"  ✅ {len(records_to_insert)}件インポート完了")
                    total_imported += len(records_to_insert)
                
                # 列マッピング情報を出力
                print(f"  列マッピング:")
                for i, (orig_col, safe_col) in enumerate(zip(df.columns, safe_columns)):
                    excel_col = chr(65 + i % 26) + (str(i//26 + 1) if i >= 26 else '')
                    print(f"    {excel_col}: {orig_col} → {safe_col}")
                
            except Exception as e:
                print(f"  ❌ エラー: {e}")
                continue
        
        conn.close()
        
        print(f"✅ 総インポート件数: {total_imported:,}")
        print("=== エクセルデータ全列インポート完了 ===")
        
        return 0
        
    except Exception as e:
        print(f"エラー: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
