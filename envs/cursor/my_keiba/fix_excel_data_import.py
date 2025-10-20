import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
import json
import os
import sys
import argparse
from pathlib import Path

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

class FixExcelDataImport:
    """エクセルデータインポートの修正"""
    
    def __init__(self):
        self.yDate_path = "yDate"
        self.excel_db_path = "excel_data.db"
    
    def create_correct_schema(self, mode='full'):
        """正しいスキーマ作成"""
        print("=== 正しいスキーマ作成 ===")
        
        try:
            conn = sqlite3.connect(self.excel_db_path)
            cursor = conn.cursor()
            
            if mode == 'full':
                print("フルモード: 既存テーブルを削除します")
                cursor.execute("DROP TABLE IF EXISTS HORSE_MARKS")
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS HORSE_MARKS (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    SourceDate TEXT,
                    HorseName TEXT,
                    NormalizedHorseName TEXT,
                    RaceId TEXT,
                    RaceName TEXT,
                    JyoCD TEXT,
                    Kaiji TEXT,
                    Nichiji TEXT,
                    RaceNum TEXT,
                    Umaban TEXT,
                    MorningOdds TEXT,
                    Mark1 TEXT,
                    Mark2 TEXT,
                    Mark3 TEXT,
                    Mark4 TEXT,
                    Mark5 TEXT,
                    Mark6 TEXT,
                    Mark7 TEXT,
                    Mark8 TEXT,
                    ZI_INDEX TEXT,
                    ZM_VALUE TEXT,
                    SHIBA_DA TEXT,
                    KYORI_M TEXT,
                    R_MARK1 TEXT,
                    R_MARK2 TEXT,
                    R_MARK3 TEXT,
                    SourceFile TEXT,
                    ImportedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(SourceFile, NormalizedHorseName, RaceId)
                )
            """)
            
            conn.commit()
            conn.close()
            
            print("✅ スキーマ準備完了")
            return True
            
        except Exception as e:
            print(f"スキーマ作成エラー: {e}")
            return False
    
    def import_excel_data_manually(self, mode='full'):
        """エクセルデータの手動インポート"""
        print("=== エクセルデータの手動インポート ===")
        
        try:
            conn = sqlite3.connect(self.excel_db_path)
            cursor = conn.cursor()
            
            yDate_dir = Path(self.yDate_path)
            all_files = sorted(list(yDate_dir.glob("*.xlsx")) + list(yDate_dir.glob("*.csv")))
            
            files_to_process = []
            if mode == 'incremental':
                cursor.execute("SELECT DISTINCT SourceFile FROM HORSE_MARKS")
                existing_files = {row[0] for row in cursor.fetchall()}
                files_to_process = [f for f in all_files if f.name not in existing_files]
                print(f"増分モード: {len(all_files)}ファイル中、{len(files_to_process)}個の新規ファイルを処理します")
            else:
                files_to_process = all_files
                print(f"フルモード: {len(all_files)}個のファイルをすべて処理します")

            if not files_to_process:
                print("✅ 処理対象の新しいファイルはありませんでした。")
                return True

            total_imported = 0
            
            for file_path in files_to_process:
                print(f"--- 処理中: {file_path.name} ---")
                
                try:
                    if file_path.suffix == '.xlsx':
                        df = pd.read_excel(file_path, dtype=str, engine='openpyxl').fillna("")
                    elif file_path.suffix == '.csv':
                        df = pd.read_csv(file_path, dtype=str).fillna("")
                    else:
                        continue
                    
                    df.columns = [str(col).strip() for col in df.columns]
                    
                    records_to_insert = []
                    for index, row in df.iterrows():
                        horse_name = str(row.get("馬名S", "") or "").strip()
                        if not horse_name:
                            continue
                        
                        race_id = str(row.get("レースID(新)", "") or "").strip()
                        source_date = race_id[:8] if race_id else file_path.stem[:8]

                        record = {
                            'SourceDate': source_date,
                            'HorseName': horse_name,
                            'NormalizedHorseName': horse_name,
                            'RaceId': race_id,
                            'RaceName': str(row.get("レース名", "") or "").strip(),
                            'JyoCD': str(row.get("場", "") or "").strip(),
                            'Kaiji': "",
                            'Nichiji': "",
                            'RaceNum': str(row.get("R", "") or "").strip(),
                            'Umaban': str(row.get("馬番", "") or "").strip(),
                            'MorningOdds': str(row.get("朝オッズ", "") or "").strip(),
                            'Mark1': str(row.get("馬印1", "") or "").strip(),
                            'Mark2': str(row.get("馬印2", "") or "").strip(),
                            'Mark3': str(row.get("馬印3", "") or "").strip(),
                            'Mark4': str(row.get("馬印4", "") or "").strip(),
                            'Mark5': str(row.get("馬印5", "") or "").strip(),
                            'Mark6': str(row.get("馬印6", "") or "").strip(),
                            'Mark7': str(row.get("馬印7", "") or "").strip(),
                            'Mark8': str(row.get("馬印8", "") or "").strip(),
                            'ZI_INDEX': str(row.get("ZI指数", "") or "").strip(),
                            'ZM_VALUE': str(row.get("ZM", "") or "").strip(),
                            'SHIBA_DA': str(row.get("芝ダ", "") or "").strip(),
                            'KYORI_M': str(row.get("距離", "") or "").strip(),
                            'R_MARK1': str(row.get("R印1", "") or "").strip(),
                            'R_MARK2': str(row.get("R印2", "") or "").strip(),
                            'R_MARK3': str(row.get("R印3", "") or "").strip(),
                            'SourceFile': file_path.name,
                            'ImportedAt': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        records_to_insert.append(record)
                    
                    if records_to_insert:
                        column_names = list(records_to_insert[0].keys())
                        placeholders = ", ".join(f":{name}" for name in column_names)
                        
                        sql = f"""
                            INSERT OR IGNORE INTO HORSE_MARKS ({", ".join(column_names)})
                            VALUES ({placeholders})
                        """
                        
                        cursor.executemany(sql, records_to_insert)
                        conn.commit()
                        
                        print(f"  ✅ {len(records_to_insert)}件インポート完了")
                        total_imported += len(records_to_insert)
                    else:
                        print(f"  ⚠️ インポート対象データなし")
                
                except Exception as e:
                    print(f"  ❌ エラー: {e}")
                    continue
            
            conn.close()
            
            print(f"✅ 総インポート件数: {total_imported:,}")
            return True
            
        except Exception as e:
            print(f"エクセルデータ手動インポートエラー: {e}")
            return False
    
    def verify_import_results(self):
        """インポート結果確認"""
        # (This method remains unchanged)
        print("=== インポート結果確認 ===")
        try:
            conn = sqlite3.connect(self.excel_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM HORSE_MARKS")
            count = cursor.fetchone()[0]
            print(f"✅ 総レコード数: {count:,}")
            cursor.execute("SELECT SourceDate, COUNT(*) as record_count FROM HORSE_MARKS GROUP BY SourceDate ORDER BY SourceDate DESC LIMIT 10")
            results = cursor.fetchall()
            print("最新10日分のデータ:")
            print("日付 | レコード数")
            print("-" * 30)
            for row in results:
                print(f"{row[0]} | {row[1]:,}")
            conn.close()
            return True
        except Exception as e:
            print(f"インポート結果確認エラー: {e}")
            return False
    
    def run_fix_excel_data_import(self, mode='full'):
        """エクセルデータインポート修正実行"""
        print(f"=== エクセルデータインポート修正実行 (mode: {mode}) ===")
        
        try:
            if not self.create_correct_schema(mode=mode):
                return False
            if not self.import_excel_data_manually(mode=mode):
                return False
            if not self.verify_import_results():
                return False
            
            print("✅ エクセルデータインポート修正完了")
            return True
            
        except Exception as e:
            print(f"エクセルデータインポート修正実行エラー: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description="Fix and import Excel data.")
    parser.add_argument("--mode", choices=['full', 'incremental'], default='full', help="Import mode: 'full' to overwrite, 'incremental' to add new files.")
    args = parser.parse_args()

    fixer = FixExcelDataImport()
    success = fixer.run_fix_excel_data_import(mode=args.mode)
    
    if success:
        print("\n✅ エクセルデータインポート修正成功")
    else:
        print("\n❌ エクセルデータインポート修正失敗")

if __name__ == "__main__":
    main()



