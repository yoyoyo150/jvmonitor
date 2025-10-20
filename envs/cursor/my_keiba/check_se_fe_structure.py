import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
import json
import os
import sys

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

class CheckSEFEStructure:
    """SE_FEテーブル構造チェック"""
    
    def __init__(self, db_path="trainer_prediction_system/excel_data.db"):
        self.db_path = db_path
        self.conn = None
        self.connect()
    
    def connect(self):
        """データベース接続"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            print("データベース接続成功")
        except Exception as e:
            print(f"データベース接続エラー: {e}")
            return False
        return True
    
    def check_se_fe_columns(self):
        """SE_FEテーブルの列構造チェック"""
        print("=== SE_FEテーブル列構造チェック ===")
        
        try:
            # 列名一覧取得
            cursor = self.conn.cursor()
            cursor.execute("PRAGMA table_info(SE_FE)")
            columns_info = cursor.fetchall()
            
            print("SE_FEテーブルの列構造:")
            for col in columns_info:
                print(f"  {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL OK'}")
            
            # 列名リスト
            column_names = [col[1] for col in columns_info]
            print(f"\n列名リスト: {column_names}")
            
            return column_names
            
        except Exception as e:
            print(f"SE_FEテーブル列構造チェックエラー: {e}")
            return None
    
    def check_roi_related_columns(self, column_names):
        """ROI関連列の存在チェック"""
        print("=== ROI関連列の存在チェック ===")
        
        try:
            # ROI計算に必要な列の存在確認
            required_columns = ['finish', 'win_pay_yen', 'plc_pay_yen_low']
            existing_columns = []
            missing_columns = []
            
            for col in required_columns:
                if col in column_names:
                    existing_columns.append(col)
                else:
                    missing_columns.append(col)
            
            print(f"存在するROI関連列: {existing_columns}")
            print(f"存在しないROI関連列: {missing_columns}")
            
            # 代替列の確認
            alternative_columns = []
            for col in column_names:
                if 'chaku' in col.lower() or 'finish' in col.lower():
                    alternative_columns.append(col)
                elif 'win' in col.lower() and 'pay' in col.lower():
                    alternative_columns.append(col)
                elif 'plc' in col.lower() and 'pay' in col.lower():
                    alternative_columns.append(col)
            
            print(f"代替候補列: {alternative_columns}")
            
            return existing_columns, missing_columns, alternative_columns
            
        except Exception as e:
            print(f"ROI関連列の存在チェックエラー: {e}")
            return None, None, None
    
    def show_sample_data(self):
        """サンプルデータ表示"""
        print("=== サンプルデータ表示 ===")
        
        try:
            # サンプルデータ（5行）
            query_sample = """
            SELECT *
            FROM SE_FE
            ORDER BY SourceDate DESC
            LIMIT 5
            """
            result_sample = pd.read_sql_query(query_sample, self.conn)
            
            print("SE_FEサンプルデータ（5行）:")
            print(result_sample.to_string(index=False))
            
            return result_sample
            
        except Exception as e:
            print(f"サンプルデータ表示エラー: {e}")
            return None
    
    def run_structure_check(self):
        """構造チェック実行"""
        print("=== SE_FEテーブル構造チェック実行 ===")
        
        try:
            # 1) 列構造チェック
            column_names = self.check_se_fe_columns()
            if column_names is None:
                return False
            
            # 2) ROI関連列チェック
            existing, missing, alternatives = self.check_roi_related_columns(column_names)
            if existing is None:
                return False
            
            # 3) サンプルデータ表示
            sample_result = self.show_sample_data()
            if sample_result is None:
                return False
            
            print("✅ SE_FEテーブル構造チェック完了")
            return True
            
        except Exception as e:
            print(f"SE_FEテーブル構造チェック実行エラー: {e}")
            return False

def main():
    checker = CheckSEFEStructure()
    success = checker.run_structure_check()
    
    if success:
        print("\n✅ SE_FEテーブル構造チェック成功")
    else:
        print("\n❌ SE_FEテーブル構造チェック失敗")

if __name__ == "__main__":
    main()




