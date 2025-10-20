#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JVMonitor.exe用強化されたエクセルデータインポートスクリプト
"""
import sys
import os
import sqlite3
import argparse
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import json

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

class EnhancedExcelImporter:
    """強化されたエクセルデータインポーター"""
    
    def __init__(self):
        self.project_root = self._find_project_root()
        self.db_path = self.project_root / "excel_data.db"
        self.yDate_dir = self.project_root / "yDate"
        self.state_file = self.project_root / "import_state.json"
        
    def _find_project_root(self):
        """プロジェクトルートを検索"""
        current = Path.cwd()
        while current != current.parent:
            if (current / "yDate").exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def _load_import_state(self):
        """インポート状態を読み込み"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {"processed_files": [], "last_update": ""}
    
    def _save_import_state(self, state):
        """インポート状態を保存"""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    
    def _sort_key(self, path: Path):
        """Excelファイルを並び替えるキー"""
        date_raw = self._extract_date_from_filename(path)
        try:
            return datetime.strptime(date_raw, "%Y%m%d")
        except ValueError:
            return datetime.fromtimestamp(path.stat().st_mtime)

    def _get_latest_excel_files(self, mode="incremental", limit=None, lookback_days=None, processed_files=None):
        """最新のExcelファイルを取得"""
        if not self.yDate_dir.exists():
            print("❌ yDateディレクトリが見つかりません")
            return []
        
        if processed_files is None:
            processed_files = set()
        
        excel_files = sorted(self.yDate_dir.glob("*.xlsx"), key=self._sort_key, reverse=True)
        
        cutoff = None
        if lookback_days is not None and lookback_days > 0:
            cutoff = datetime.today() - timedelta(days=lookback_days)
        
        filtered_files = []
        for file_path in excel_files:
            extracted = self._extract_date_from_filename(file_path)
            within_lookback = True
            if cutoff is not None:
                try:
                    file_date = datetime.strptime(extracted, "%Y%m%d")
                except ValueError:
                    file_date = None
                within_lookback = True if file_date is None else file_date >= cutoff
            
            if mode == "incremental":
                if cutoff is not None:
                    if within_lookback:
                        filtered_files.append(file_path)
                    elif file_path.name not in processed_files:
                        filtered_files.append(file_path)
                else:
                    if file_path.name not in processed_files:
                        filtered_files.append(file_path)
            else:
                if cutoff is None or within_lookback:
                    filtered_files.append(file_path)
        
        if limit is not None and limit > 0:
            filtered_files = filtered_files[:limit]
        
        return filtered_files
    
    def _extract_date_from_filename(self, file_path):
        """ファイル名から日付を抽出"""
        name = file_path.stem
        
        # 20250928形式
        if len(name) >= 8 and name[:8].isdigit():
            return name[:8]
        
        # 250250621形式
        if len(name) >= 9 and name.startswith('250') and name[3:9].isdigit():
            return '20' + name[3:9]
        
        return "UNKNOWN"
    
    def _normalize_mark_data(self, mark_value):
        """馬印データの正規化"""
        if not mark_value or mark_value.strip() == "":
            return None
        
        mark_value = str(mark_value).strip()
        
        # 数値の場合はそのまま
        try:
            return int(mark_value)
        except:
            pass
        
        # 記号の場合はマッピング
        symbol_map = {
            "◎": 1, "○": 2, "▲": 3, "△": 4, "×": 5,
            "？": None, "?": None, "消": None, "止": None
        }
        
        return symbol_map.get(mark_value, None)
    
    def import_excel_data(self, mode="incremental", limit=None, lookback_days=None):
        """エクセルデータをインポート"""
        print(f"=== エクセルデータインポート開始 ({mode}モード) ===")
        print(f"プロジェクトルート: {self.project_root}")
        print(f"データベース: {self.db_path}")
        print(f"yDateディレクトリ: {self.yDate_dir}")
        if lookback_days is not None and lookback_days > 0:
            print(f"期間指定: 過去{lookback_days}日分")
        if limit is not None and limit > 0:
            print(f"上限ファイル数: {limit}")
        
        # データベース接続
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # 処理対象ファイルを取得
        state = self._load_import_state()
        processed_files = set(state.get("processed_files", []))
        if mode == "full":
            processed_files.clear()

        excel_files = self._get_latest_excel_files(mode, limit=limit, lookback_days=lookback_days, processed_files=processed_files)

        if not excel_files:
            print("✅ 処理対象のファイルがありません")
            conn.close()
            return True

        print(f"処理対象ファイル数: {len(excel_files)}")

        total_imported = 0
        processed_count = 0
        
        for file_path in excel_files:
            print(f"\n--- 処理中: {file_path.name} ---")
            
            try:
                # エクセルファイル読み込み
                df = pd.read_excel(file_path, dtype=str, engine='openpyxl').fillna("")
                print(f"  列数: {len(df.columns)}, 行数: {len(df)}")
                
                # テーブル名を動的に作成（ファイル名ベース）
                source_date = self._extract_date_from_filename(file_path)
                table_name = f"EXCEL_DATA_{source_date}"
                
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
                
                # 処理済みファイルとして記録
                processed_files.add(file_path.name)
                processed_count += 1
                
            except Exception as e:
                print(f"  ❌ エラー: {e}")
                continue
        
        # インポート状態を更新
        state["processed_files"] = list(processed_files)
        state["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._save_import_state(state)
        
        conn.close()
        
        print(f"\n✅ 総インポート件数: {total_imported:,}")
        print(f"✅ 処理ファイル数: {processed_count}")
        print("=== エクセルデータインポート完了 ===")
        
        return True

def main():
    """メイン関数"""
    try:
        parser = argparse.ArgumentParser(description="Excelデータのインポート")
        parser.add_argument("--mode", choices=["incremental", "full"], default="incremental")
        parser.add_argument("--limit", type=int, default=None)
        parser.add_argument("--lookback-days", type=int, default=None)
        args = parser.parse_args()

        importer = EnhancedExcelImporter()
        success = importer.import_excel_data(mode=args.mode, limit=args.limit, lookback_days=args.lookback_days)

        if success:
            print("✅ インポート完了")
            return 0
        else:
            print("❌ インポート失敗")
            return 1
            
    except Exception as e:
        print(f"エラー: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
