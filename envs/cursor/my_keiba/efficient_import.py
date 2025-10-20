#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
効率的な馬印データインポート処理
更新日付で管理し、最新の10ファイルのみを処理
"""

import sqlite3
import sys
import io
import pandas as pd
import os
import json
from datetime import datetime, timedelta
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

DB_PATH = 'ecore.db'
YDATE_DIR = r"C:\my_project_folder\envs\cursor\my_keiba\yDate"
CONFIG_FILE = 'import_config.json'

def load_config():
    """設定ファイルを読み込み"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARNING] 設定ファイル読み込みエラー: {e}")
    
    # デフォルト設定
    return {
        "last_import_date": None,
        "processed_files": [],
        "max_files": 10
    }

def save_config(config):
    """設定ファイルを保存"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[ERROR] 設定ファイル保存エラー: {e}")

def get_latest_excel_files(max_files=10):
    """最新のExcelファイルを取得（更新日付順）"""
    try:
        excel_path = Path(YDATE_DIR)
        if not excel_path.exists():
            print(f"[ERROR] Excelディレクトリが存在しません: {YDATE_DIR}")
            return []
        
        # .xlsxファイルを取得
        excel_files = list(excel_path.glob("*.xlsx"))
        
        # ファイルの更新日時でソート（新しい順）
        file_info = []
        for file in excel_files:
            try:
                # ファイル名から日付を抽出
                date_str = file.stem
                if date_str.isdigit() and len(date_str) == 8:
                    mod_time = datetime.fromtimestamp(file.stat().st_mtime)
                    file_info.append({
                        'file': file,
                        'date': date_str,
                        'mod_time': mod_time,
                        'size': file.stat().st_size
                    })
            except Exception as e:
                print(f"[WARNING] ファイル情報取得エラー {file.name}: {e}")
                continue
        
        # 更新日時でソート（新しい順）
        file_info.sort(key=lambda x: x['mod_time'], reverse=True)
        
        # 最新のmax_files件を返す
        return file_info[:max_files]
        
    except Exception as e:
        print(f"[ERROR] Excelファイル取得エラー: {e}")
        return []

def check_file_needs_import(file_info, config):
    """ファイルがインポートが必要かチェック"""
    date_str = file_info['date']
    mod_time = file_info['mod_time']
    
    # 設定ファイルに記録されている最終インポート日時と比較
    if config.get('last_import_date'):
        try:
            last_import = datetime.fromisoformat(config['last_import_date'])
            if mod_time <= last_import:
                return False, "既にインポート済み"
        except Exception as e:
            print(f"[WARNING] 日付比較エラー: {e}")
    
    # データベースで確認
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 該当日付のデータが存在するかチェック
        cursor.execute("SELECT COUNT(*) FROM HORSE_MARKS WHERE SourceDate = ?", (date_str,))
        count = cursor.fetchone()[0]
        
        if count > 0:
            # インポート時刻をチェック
            cursor.execute("SELECT MAX(ImportedAt) FROM HORSE_MARKS WHERE SourceDate = ?", (date_str,))
            import_time = cursor.fetchone()[0]
            
            if import_time:
                try:
                    import_dt = datetime.fromisoformat(import_time.replace(' ', 'T'))
                    if mod_time <= import_dt:
                        conn.close()
                        return False, "データベースに最新データが存在"
                except Exception as e:
                    print(f"[WARNING] インポート時刻比較エラー: {e}")
        
        conn.close()
        return True, "インポートが必要"
        
    except Exception as e:
        print(f"[ERROR] データベース確認エラー: {e}")
        return True, "エラーのためインポートが必要"

def import_excel_file(file_info):
    """Excelファイルをインポート"""
    file_path = file_info['file']
    date_str = file_info['date']
    
    try:
        print(f"--- 処理中: {file_path.name} ---")
        
        # UTF-8エンコーディングでExcelファイルを読み込み
        df = pd.read_excel(file_path, engine='openpyxl')
        print(f"Excelファイル読み込み成功: {len(df)} 行")
        
        # データベースに接続
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 既存データを削除
        cursor.execute("DELETE FROM HORSE_MARKS WHERE SourceDate = ?", (date_str,))
        deleted_count = cursor.rowcount
        print(f"既存データ削除: {deleted_count} 件")
        
        # 新しいデータを挿入
        inserted_count = 0
        for index, row in df.iterrows():
            try:
                cursor.execute("""
                    INSERT INTO HORSE_MARKS (
                        SourceDate, HorseName, NormalizedHorseName, 
                        Mark1, Mark2, Mark3, Mark4, Mark5, Mark6, Mark7, Mark8,
                        SourceFile, ImportedAt
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    date_str,
                    row.get('馬名S', ''),
                    row.get('馬名S', ''),
                    row.get('馬印1', ''),
                    row.get('馬印2', ''),
                    row.get('馬印3', ''),
                    row.get('馬印4', ''),
                    row.get('馬印5', ''),
                    row.get('馬印6', ''),
                    row.get('馬印7', ''),
                    row.get('馬印8', ''),
                    file_path.name,
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))
                inserted_count += 1
            except Exception as e:
                print(f"行 {index} の挿入エラー: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        print(f"✅ {inserted_count}件インポート完了")
        return True, inserted_count
        
    except Exception as e:
        print(f"❌ インポートエラー: {e}")
        return False, 0

def efficient_import():
    """効率的なインポート処理"""
    print("=== 効率的な馬印データインポート ===\n")
    
    # 1. 設定を読み込み
    config = load_config()
    max_files = config.get('max_files', 10)
    print(f"最大処理ファイル数: {max_files}")
    
    # 2. 最新のExcelファイルを取得
    print("\n1. 最新のExcelファイルを取得")
    latest_files = get_latest_excel_files(max_files)
    
    if not latest_files:
        print("処理対象のExcelファイルがありません")
        return
    
    print(f"取得したファイル数: {len(latest_files)} 件")
    
    # 3. インポートが必要なファイルを特定
    print("\n2. インポートが必要なファイルを特定")
    files_to_import = []
    
    for file_info in latest_files:
        needs_import, reason = check_file_needs_import(file_info, config)
        status = "✅" if needs_import else "⏭️"
        print(f"{status} {file_info['date']}: {reason}")
        
        if needs_import:
            files_to_import.append(file_info)
    
    if not files_to_import:
        print("インポートが必要なファイルはありません")
        return
    
    print(f"\nインポート対象: {len(files_to_import)} 件")
    
    # 4. インポート処理を実行
    print("\n3. インポート処理を実行")
    total_imported = 0
    successful_imports = []
    
    for file_info in files_to_import:
        success, count = import_excel_file(file_info)
        if success:
            total_imported += count
            successful_imports.append(file_info)
    
    # 5. 設定を更新
    if successful_imports:
        config['last_import_date'] = datetime.now().isoformat()
        config['processed_files'] = [f['date'] for f in successful_imports]
        save_config(config)
        print(f"\n✅ 設定を更新しました")
    
    # 6. 結果サマリー
    print(f"\n=== インポート完了 ===")
    print(f"処理対象ファイル: {len(files_to_import)} 件")
    print(f"成功: {len(successful_imports)} 件")
    print(f"総インポート件数: {total_imported} 件")
    
    if successful_imports:
        print("インポートされた日付:")
        for file_info in successful_imports:
            print(f"  {file_info['date']}: {file_info['mod_time'].strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    efficient_import()

