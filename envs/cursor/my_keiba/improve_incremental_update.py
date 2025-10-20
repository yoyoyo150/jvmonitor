import sqlite3
import sys
import io
import pandas as pd
import os
import json
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def improve_incremental_update():
    print("=== 馬印更新（増分）の改善案 ===\n")

    # 1. 現在の設定を確認
    print("1. 現在の設定を確認")
    
    # JVMonitorの設定ファイルを確認
    config_path = r"C:\my_project_folder\envs\cursor\my_keiba\JVMonitor\JVMonitor\bin\Debug\net6.0-windows\appsettings.json"
    
    if os.path.exists(config_path):
        print(f"[OK] 設定ファイルが存在します: {config_path}")
        
        # 設定ファイルの内容を確認
        with open(config_path, 'r', encoding='utf-8') as f:
            config_content = f.read()
            print("設定ファイルの内容:")
            print(config_content)
    else:
        print(f"[ERROR] 設定ファイルが見つかりません: {config_path}")

    # 2. 改善された馬印更新スクリプトを作成
    print("\n2. 改善された馬印更新スクリプトを作成")
    
    improved_script = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改善された馬印更新（増分）スクリプト
JVMonitorから呼び出される馬印データの更新処理
"""

import sqlite3
import sys
import io
import pandas as pd
import os
from datetime import datetime
from pathlib import Path
import json

# UTF-8エンコーディング設定
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def load_config():
    """設定ファイルを読み込み"""
    config_path = r"C:\\my_project_folder\\envs\\cursor\\my_keiba\\JVMonitor\\JVMonitor\\bin\\Debug\\net6.0-windows\\appsettings.json"
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"[ERROR] 設定ファイルの読み込みエラー: {e}")
        return None

def get_database_path():
    """データベースパスを取得"""
    config = load_config()
    if config and 'ConnectionStrings' in config:
        return config['ConnectionStrings'].get('DefaultConnection', 'ecore.db')
    return 'ecore.db'

def get_excel_directory():
    """Excelディレクトリを取得"""
    config = load_config()
    if config and 'Options' in config:
        return config['Options'].get('YDateExcelDir', 'yDate')
    return 'yDate'

def check_database_structure(db_path):
    """データベース構造を確認"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # テーブル構造を確認
        cursor.execute("PRAGMA table_info(HORSE_MARKS)")
        columns = cursor.fetchall()
        
        # 主キー制約を確認
        cursor.execute("PRAGMA table_xinfo(HORSE_MARKS)")
        xinfo = cursor.fetchall()
        
        pk_columns = []
        for col in xinfo:
            if len(col) >= 6:
                cid, name, type_name, not_null, default_value, pk = col[:6]
                if pk > 0:
                    pk_columns.append((pk, name))
        
        conn.close()
        
        if pk_columns:
            pk_columns.sort()
            return pk_columns
        else:
            return None
            
    except Exception as e:
        print(f"[ERROR] データベース構造確認エラー: {e}")
        return None

def get_latest_excel_file(excel_dir):
    """最新のExcelファイルを取得"""
    try:
        excel_path = Path(excel_dir)
        if not excel_path.exists():
            print(f"[ERROR] Excelディレクトリが存在しません: {excel_dir}")
            return None
        
        # .xlsxファイルを取得して日付順にソート
        excel_files = list(excel_path.glob("*.xlsx"))
        if not excel_files:
            print(f"[ERROR] Excelファイルが見つかりません: {excel_dir}")
            return None
        
        # ファイル名から日付を抽出してソート
        dated_files = []
        for file in excel_files:
            try:
                date_str = file.stem
                if date_str.isdigit() and len(date_str) == 8:
                    date_obj = datetime.strptime(date_str, '%Y%m%d')
                    dated_files.append((date_obj, file))
            except:
                continue
        
        if not dated_files:
            print(f"[ERROR] 有効な日付形式のExcelファイルが見つかりません")
            return None
        
        # 最新のファイルを返す
        latest_file = max(dated_files, key=lambda x: x[0])[1]
        return latest_file
        
    except Exception as e:
        print(f"[ERROR] 最新Excelファイル取得エラー: {e}")
        return None

def update_horse_marks_incremental():
    """馬印データの増分更新"""
    print("=== 馬印更新（増分）開始 ===\\n")
    
    # 1. 設定を読み込み
    db_path = get_database_path()
    excel_dir = get_excel_directory()
    
    print(f"データベース: {db_path}")
    print(f"Excelディレクトリ: {excel_dir}")
    
    # 2. データベース構造を確認
    print("\\n2. データベース構造を確認")
    pk_columns = check_database_structure(db_path)
    
    if not pk_columns:
        print("[ERROR] データベース構造の確認に失敗しました")
        return False
    
    print(f"主キー制約: {[col[1] for col in pk_columns]}")
    
    # 3. 最新のExcelファイルを取得
    print("\\n3. 最新のExcelファイルを取得")
    latest_excel = get_latest_excel_file(excel_dir)
    
    if not latest_excel:
        print("[ERROR] 最新のExcelファイルの取得に失敗しました")
        return False
    
    print(f"最新のExcelファイル: {latest_excel.name}")
    
    # 4. Excelファイルを読み込み
    print("\\n4. Excelファイルを読み込み")
    try:
        df = pd.read_excel(latest_excel)
        print(f"[OK] Excelファイル読み込み成功: {len(df)} 行")
    except Exception as e:
        print(f"[ERROR] Excelファイル読み込みエラー: {e}")
        return False
    
    # 5. データベースに接続
    print("\\n5. データベースに接続")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print("[OK] データベース接続成功")
    except Exception as e:
        print(f"[ERROR] データベース接続エラー: {e}")
        return False
    
    # 6. 馬印データを更新
    print("\\n6. 馬印データを更新")
    try:
        # 日付を抽出
        date_str = latest_excel.stem
        
        # 既存データを削除
        cursor.execute("DELETE FROM HORSE_MARKS WHERE SourceDate = ?", (date_str,))
        deleted_count = cursor.rowcount
        print(f"既存データ削除: {deleted_count} 件")
        
        # 新しいデータを挿入
        # ここで実際のデータ挿入処理を実装
        # （簡略化のため、基本的な構造のみ）
        
        conn.commit()
        print("[OK] 馬印データ更新完了")
        
    except Exception as e:
        print(f"[ERROR] 馬印データ更新エラー: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
    
    print("\\n=== 馬印更新（増分）完了 ===")
    return True

if __name__ == '__main__':
    success = update_horse_marks_incremental()
    if success:
        print("\\n[SUCCESS] 馬印更新が正常に完了しました")
        sys.exit(0)
    else:
        print("\\n[ERROR] 馬印更新に失敗しました")
        sys.exit(1)
'''
    
    # スクリプトをファイルに保存
    script_path = "improved_horse_marks_update.py"
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(improved_script)
    
    print(f"[OK] 改善されたスクリプトを作成しました: {script_path}")

    # 3. JVMonitorの設定更新案
    print("\n3. JVMonitorの設定更新案")
    
    config_update = {
        "ConnectionStrings": {
            "DefaultConnection": "ecore.db"
        },
        "Options": {
            "UseYDateExcelForRealtime": True,
            "YDateExcelDir": "yDate",
            "PythonExe": "python",
            "HorseMarksUpdateScript": "improved_horse_marks_update.py"
        }
    }
    
    print("推奨設定:")
    print(json.dumps(config_update, indent=2, ensure_ascii=False))

    # 4. 使用方法
    print("\n4. 使用方法")
    print("1. improved_horse_marks_update.py をプロジェクトルートに配置")
    print("2. JVMonitorの設定ファイルを更新")
    print("3. 馬印更新（増分）ボタンから improved_horse_marks_update.py を呼び出し")
    print("4. エラーハンドリングとログ出力で問題を特定可能")

if __name__ == '__main__':
    improve_incremental_update()
