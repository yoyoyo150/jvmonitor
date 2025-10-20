import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
import json
import os
import sys
from pathlib import Path

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

class CheckExcelDataUpdateStatus:
    """エクセルデータの更新状況確認"""
    
    def __init__(self):
        self.ecore_db_path = "ecore.db"
        self.excel_db_path = "excel_data.db"
        self.yDate_path = "yDate"
        self.conn_ecore = None
        self.conn_excel = None
    
    def connect_databases(self):
        """データベース接続"""
        try:
            self.conn_ecore = sqlite3.connect(self.ecore_db_path)
            self.conn_excel = sqlite3.connect(self.excel_db_path)
            print("✅ データベース接続成功")
            return True
        except Exception as e:
            print(f"❌ データベース接続エラー: {e}")
            return False
    
    def check_yDate_files(self):
        """yDateディレクトリのファイル確認"""
        print("=== yDateディレクトリのファイル確認 ===")
        
        try:
            yDate_dir = Path(self.yDate_path)
            if not yDate_dir.exists():
                print(f"❌ yDateディレクトリが存在しません: {yDate_dir}")
                return None
            
            # Excelファイル一覧取得
            excel_files = list(yDate_dir.glob("*.xlsx")) + list(yDate_dir.glob("*.csv"))
            excel_files.sort()
            
            print(f"✅ yDateディレクトリ: {len(excel_files)}ファイル")
            print("最新10ファイル:")
            for file in excel_files[-10:]:
                stat = file.stat()
                print(f"  {file.name} ({stat.st_size:,} bytes, {datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')})")
            
            return excel_files
            
        except Exception as e:
            print(f"yDateディレクトリ確認エラー: {e}")
            return None
    
    def check_excel_db_status(self):
        """excel_data.dbの状況確認"""
        print("=== excel_data.dbの状況確認 ===")
        
        try:
            # テーブル一覧確認
            cursor = self.conn_excel.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            print(f"✅ テーブル数: {len(tables)}")
            for table in tables:
                print(f"  - {table[0]}")
            
            # データ件数確認
            if tables:
                for table in tables:
                    table_name = table[0]
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    print(f"  {table_name}: {count:,}件")
            
            return True
            
        except Exception as e:
            print(f"excel_data.db状況確認エラー: {e}")
            return False
    
    def check_import_status(self):
        """インポート状況確認"""
        print("=== インポート状況確認 ===")
        
        try:
            # 最新のインポート日時確認
            cursor = self.conn_excel.cursor()
            cursor.execute("""
                SELECT 
                    SourceDate,
                    COUNT(*) as record_count,
                    MAX(ImportedAt) as latest_import
                FROM excel_marks 
                GROUP BY SourceDate 
                ORDER BY SourceDate DESC 
                LIMIT 10
            """)
            results = cursor.fetchall()
            
            print("最新10日分のインポート状況:")
            print("日付 | レコード数 | 最新インポート時刻")
            print("-" * 60)
            
            for row in results:
                print(f"{row[0]} | {row[1]:,} | {row[2]}")
            
            return results
            
        except Exception as e:
            print(f"インポート状況確認エラー: {e}")
            return None
    
    def check_missing_dates(self):
        """欠損日付の確認"""
        print("=== 欠損日付の確認 ===")
        
        try:
            # yDateディレクトリの日付一覧
            yDate_dir = Path(self.yDate_path)
            excel_files = list(yDate_dir.glob("*.xlsx")) + list(yDate_dir.glob("*.csv"))
            
            # ファイル名から日付を抽出
            file_dates = []
            for file in excel_files:
                filename = file.stem
                # 日付パターンを抽出（YYYYMMDD形式）
                if len(filename) >= 8 and filename[:8].isdigit():
                    date_str = filename[:8]
                    file_dates.append(date_str)
            
            file_dates.sort()
            
            # データベースの日付一覧
            cursor = self.conn_excel.cursor()
            cursor.execute("SELECT DISTINCT SourceDate FROM excel_marks ORDER BY SourceDate")
            db_dates = [row[0] for row in cursor.fetchall()]
            
            # 欠損日付の確認
            missing_dates = []
            for file_date in file_dates:
                if file_date not in db_dates:
                    missing_dates.append(file_date)
            
            print(f"✅ yDateファイル数: {len(file_dates)}")
            print(f"✅ データベース日付数: {len(db_dates)}")
            print(f"⚠️ 欠損日付数: {len(missing_dates)}")
            
            if missing_dates:
                print("欠損日付:")
                for date in missing_dates[:10]:  # 最新10件のみ表示
                    print(f"  {date}")
                if len(missing_dates) > 10:
                    print(f"  ... 他{len(missing_dates) - 10}件")
            
            return missing_dates
            
        except Exception as e:
            print(f"欠損日付確認エラー: {e}")
            return None
    
    def check_latest_data_quality(self):
        """最新データの品質確認"""
        print("=== 最新データの品質確認 ===")
        
        try:
            # 最新のデータを取得
            cursor = self.conn_excel.cursor()
            cursor.execute("""
                SELECT 
                    SourceDate,
                    COUNT(*) as total_records,
                    COUNT(CASE WHEN Mark5 IS NOT NULL AND Mark5 != '' THEN 1 END) as mark5_count,
                    COUNT(CASE WHEN Mark6 IS NOT NULL AND Mark6 != '' THEN 1 END) as mark6_count,
                    COUNT(CASE WHEN ZI_INDEX IS NOT NULL AND ZI_INDEX != '' THEN 1 END) as zi_count,
                    COUNT(CASE WHEN ZM_VALUE IS NOT NULL AND ZM_VALUE != '' THEN 1 END) as zm_count
                FROM excel_marks 
                WHERE SourceDate = (SELECT MAX(SourceDate) FROM excel_marks)
                GROUP BY SourceDate
            """)
            result = cursor.fetchone()
            
            if result:
                print(f"最新データ ({result[0]}):")
                print(f"  総レコード数: {result[1]:,}")
                print(f"  Mark5データ: {result[2]:,} ({result[2]/result[1]*100:.1f}%)")
                print(f"  Mark6データ: {result[3]:,} ({result[3]/result[1]*100:.1f}%)")
                print(f"  ZI_INDEXデータ: {result[4]:,} ({result[4]/result[1]*100:.1f}%)")
                print(f"  ZM_VALUEデータ: {result[5]:,} ({result[5]/result[1]*100:.1f}%)")
            else:
                print("❌ データが見つかりません")
            
            return result
            
        except Exception as e:
            print(f"最新データ品質確認エラー: {e}")
            return None
    
    def run_update_status_check(self):
        """更新状況確認実行"""
        print("=== エクセルデータ更新状況確認実行 ===")
        
        try:
            # 1) データベース接続
            if not self.connect_databases():
                return False
            
            # 2) yDateファイル確認
            excel_files = self.check_yDate_files()
            if excel_files is None:
                return False
            
            # 3) excel_data.db状況確認
            if not self.check_excel_db_status():
                return False
            
            # 4) インポート状況確認
            import_status = self.check_import_status()
            if import_status is None:
                return False
            
            # 5) 欠損日付確認
            missing_dates = self.check_missing_dates()
            if missing_dates is None:
                return False
            
            # 6) 最新データ品質確認
            quality = self.check_latest_data_quality()
            if quality is None:
                return False
            
            print("✅ エクセルデータ更新状況確認完了")
            return True
            
        except Exception as e:
            print(f"更新状況確認実行エラー: {e}")
            return False

def main():
    checker = CheckExcelDataUpdateStatus()
    success = checker.run_update_status_check()
    
    if success:
        print("\n✅ エクセルデータ更新状況確認成功")
    else:
        print("\n❌ エクセルデータ更新状況確認失敗")

if __name__ == "__main__":
    main()




