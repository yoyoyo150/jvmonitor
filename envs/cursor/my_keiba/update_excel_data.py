import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
import json
import os
import sys
import subprocess
from pathlib import Path

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

class UpdateExcelData:
    """エクセルデータの更新実行"""
    
    def __init__(self):
        self.yDate_path = "yDate"
        self.excel_db_path = "excel_data.db"
        self.import_script = "tools/import_excel_marks.py"
    
    def check_prerequisites(self):
        """前提条件確認"""
        print("=== 前提条件確認 ===")
        
        try:
            # yDateディレクトリ確認
            yDate_dir = Path(self.yDate_path)
            if not yDate_dir.exists():
                print(f"❌ yDateディレクトリが存在しません: {yDate_dir}")
                return False
            
            # エクセルファイル確認
            excel_files = list(yDate_dir.glob("*.xlsx")) + list(yDate_dir.glob("*.csv"))
            if not excel_files:
                print(f"❌ yDateディレクトリにエクセルファイルがありません")
                return False
            
            print(f"✅ yDateディレクトリ: {len(excel_files)}ファイル")
            
            # インポートスクリプト確認
            import_script_path = Path(self.import_script)
            if not import_script_path.exists():
                print(f"❌ インポートスクリプトが存在しません: {import_script_path}")
                return False
            
            print(f"✅ インポートスクリプト: {import_script_path}")
            
            return True
            
        except Exception as e:
            print(f"前提条件確認エラー: {e}")
            return False
    
    def create_excel_database(self):
        """excel_data.db作成"""
        print("=== excel_data.db作成 ===")
        
        try:
            # データベース接続
            conn = sqlite3.connect(self.excel_db_path)
            cursor = conn.cursor()
            
            # テーブル作成
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
                    ImportedAt DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            
            print("✅ excel_data.db作成成功")
            return True
            
        except Exception as e:
            print(f"excel_data.db作成エラー: {e}")
            return False
    
    def run_import_script(self):
        """インポートスクリプト実行"""
        print("=== インポートスクリプト実行 ===")
        
        try:
            # インポートスクリプト実行
            cmd = [
                "python",
                self.import_script,
                "--mode", "full",
                "--excel-dir", self.yDate_path,
                "--db", self.excel_db_path
            ]
            
            print(f"実行コマンド: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            print("=== 実行結果 ===")
            print("STDOUT:")
            print(result.stdout)
            print("STDERR:")
            print(result.stderr)
            print(f"終了コード: {result.returncode}")
            
            if result.returncode == 0:
                print("✅ インポートスクリプト実行成功")
                return True
            else:
                print("❌ インポートスクリプト実行失敗")
                return False
            
        except Exception as e:
            print(f"インポートスクリプト実行エラー: {e}")
            return False
    
    def verify_import_results(self):
        """インポート結果確認"""
        print("=== インポート結果確認 ===")
        
        try:
            # データベース接続
            conn = sqlite3.connect(self.excel_db_path)
            cursor = conn.cursor()
            
            # テーブル確認
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"✅ テーブル数: {len(tables)}")
            
            # データ件数確認
            cursor.execute("SELECT COUNT(*) FROM HORSE_MARKS")
            count = cursor.fetchone()[0]
            print(f"✅ 総レコード数: {count:,}")
            
            # 日付別件数確認
            cursor.execute("""
                SELECT 
                    SourceDate,
                    COUNT(*) as record_count
                FROM HORSE_MARKS 
                GROUP BY SourceDate 
                ORDER BY SourceDate DESC 
                LIMIT 10
            """)
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
    
    def run_excel_data_update(self):
        """エクセルデータ更新実行"""
        print("=== エクセルデータ更新実行 ===")
        
        try:
            # 1) 前提条件確認
            if not self.check_prerequisites():
                return False
            
            # 2) excel_data.db作成
            if not self.create_excel_database():
                return False
            
            # 3) インポートスクリプト実行
            if not self.run_import_script():
                return False
            
            # 4) インポート結果確認
            if not self.verify_import_results():
                return False
            
            print("✅ エクセルデータ更新完了")
            return True
            
        except Exception as e:
            print(f"エクセルデータ更新実行エラー: {e}")
            return False

def main():
    updater = UpdateExcelData()
    success = updater.run_excel_data_update()
    
    if success:
        print("\n✅ エクセルデータ更新成功")
        print("🎯 過去データが更新されました")
    else:
        print("\n❌ エクセルデータ更新失敗")

if __name__ == "__main__":
    main()




