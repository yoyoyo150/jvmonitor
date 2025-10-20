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

class RootCauseInvestigator:
    """根本原因の調査"""
    
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
    
    def investigate_original_data(self):
        """元のデータの調査"""
        print("=== 元のデータの調査 ===")
        
        try:
            # 元のexcel_marksテーブルの調査
            query_original = """
            SELECT 
                COUNT(*) as total_count,
                COUNT(CASE WHEN ZI_Index IS NOT NULL AND ZI_Index != '' THEN 1 END) as zi_not_null,
                COUNT(CASE WHEN ZM_Value IS NOT NULL AND ZM_Value != '' THEN 1 END) as zm_not_null,
                COUNT(CASE WHEN ZI_Index = '0' OR ZI_Index = 0 THEN 1 END) as zi_zero,
                COUNT(CASE WHEN ZM_Value = '0' OR ZM_Value = 0 THEN 1 END) as zm_zero,
                COUNT(CASE WHEN ZI_Index IS NOT NULL AND ZI_Index != '' AND ZI_Index != '0' AND ZI_Index != 0 THEN 1 END) as zi_non_zero,
                COUNT(CASE WHEN ZM_Value IS NOT NULL AND ZM_Value != '' AND ZM_Value != '0' AND ZM_Value != 0 THEN 1 END) as zm_non_zero
            FROM excel_marks
            """
            result_original = pd.read_sql_query(query_original, self.conn)
            
            print("元のexcel_marksテーブル:")
            print(f"  総件数: {result_original.iloc[0]['total_count']}")
            print(f"  ZI_Index非NULL: {result_original.iloc[0]['zi_not_null']}")
            print(f"  ZM_Value非NULL: {result_original.iloc[0]['zm_not_null']}")
            print(f"  ZI_Index=0: {result_original.iloc[0]['zi_zero']}")
            print(f"  ZM_Value=0: {result_original.iloc[0]['zm_zero']}")
            print(f"  ZI_Index非0: {result_original.iloc[0]['zi_non_zero']}")
            print(f"  ZM_Value非0: {result_original.iloc[0]['zm_non_zero']}")
            
            # 元のデータのサンプル
            query_sample = """
            SELECT 
                ZI_Index, 
                ZM_Value, 
                Chaku,
                SourceDate
            FROM excel_marks 
            WHERE ZI_Index IS NOT NULL AND ZI_Index != '' AND ZI_Index != '0' AND ZI_Index != 0
            ORDER BY SourceDate DESC
            LIMIT 10
            """
            result_sample = pd.read_sql_query(query_sample, self.conn)
            
            print("\n元のデータサンプル（非0値）:")
            print(result_sample.to_string(index=False))
            
            return result_original, result_sample
            
        except Exception as e:
            print(f"元のデータ調査エラー: {e}")
            return None, None
    
    def investigate_se_fe_data(self):
        """SE_FEテーブルの調査"""
        print("\n=== SE_FEテーブルの調査 ===")
        
        try:
            # SE_FEテーブルの調査
            query_se_fe = """
            SELECT 
                COUNT(*) as total_count,
                COUNT(CASE WHEN ZI_Index IS NOT NULL AND ZI_Index != '' THEN 1 END) as zi_not_null,
                COUNT(CASE WHEN ZM_Value IS NOT NULL AND ZM_Value != '' THEN 1 END) as zm_not_null,
                COUNT(CASE WHEN ZI_Index = '0' OR ZI_Index = 0 THEN 1 END) as zi_zero,
                COUNT(CASE WHEN ZM_Value = '0' OR ZM_Value = 0 THEN 1 END) as zm_zero,
                COUNT(CASE WHEN ZI_Index IS NOT NULL AND ZI_Index != '' AND ZI_Index != '0' AND ZI_Index != 0 THEN 1 END) as zi_non_zero,
                COUNT(CASE WHEN ZM_Value IS NOT NULL AND ZM_Value != '' AND ZM_Value != '0' AND ZM_Value != 0 THEN 1 END) as zm_non_zero
            FROM SE_FE
            """
            result_se_fe = pd.read_sql_query(query_se_fe, self.conn)
            
            print("SE_FEテーブル:")
            print(f"  総件数: {result_se_fe.iloc[0]['total_count']}")
            print(f"  ZI_Index非NULL: {result_se_fe.iloc[0]['zi_not_null']}")
            print(f"  ZM_Value非NULL: {result_se_fe.iloc[0]['zm_not_null']}")
            print(f"  ZI_Index=0: {result_se_fe.iloc[0]['zi_zero']}")
            print(f"  ZM_Value=0: {result_se_fe.iloc[0]['zm_zero']}")
            print(f"  ZI_Index非0: {result_se_fe.iloc[0]['zi_non_zero']}")
            print(f"  ZM_Value非0: {result_se_fe.iloc[0]['zm_non_zero']}")
            
            # SE_FEのサンプル
            query_sample = """
            SELECT 
                ZI_Index, 
                ZM_Value, 
                Chaku,
                SourceDate
            FROM SE_FE 
            WHERE ZI_Index IS NOT NULL AND ZI_Index != '' AND ZI_Index != '0' AND ZI_Index != 0
            ORDER BY SourceDate DESC
            LIMIT 10
            """
            result_sample = pd.read_sql_query(query_sample, self.conn)
            
            print("\nSE_FEサンプル（非0値）:")
            print(result_sample.to_string(index=False))
            
            return result_se_fe, result_sample
            
        except Exception as e:
            print(f"SE_FEテーブル調査エラー: {e}")
            return None, None
    
    def investigate_data_migration(self):
        """データ移行の調査"""
        print("\n=== データ移行の調査 ===")
        
        try:
            # 元のテーブルとSE_FEの比較
            query_comparison = """
            SELECT 
                'excel_marks' as table_name,
                COUNT(*) as total_count,
                COUNT(CASE WHEN ZI_Index IS NOT NULL AND ZI_Index != '' AND ZI_Index != '0' AND ZI_Index != 0 THEN 1 END) as zi_non_zero,
                COUNT(CASE WHEN ZM_Value IS NOT NULL AND ZM_Value != '' AND ZM_Value != '0' AND ZM_Value != 0 THEN 1 END) as zm_non_zero
            FROM excel_marks
            UNION ALL
            SELECT 
                'SE_FE' as table_name,
                COUNT(*) as total_count,
                COUNT(CASE WHEN ZI_Index IS NOT NULL AND ZI_Index != '' AND ZI_Index != '0' AND ZI_Index != 0 THEN 1 END) as zi_non_zero,
                COUNT(CASE WHEN ZM_Value IS NOT NULL AND ZM_Value != '' AND ZM_Value != '0' AND ZM_Value != 0 THEN 1 END) as zm_non_zero
            FROM SE_FE
            """
            result_comparison = pd.read_sql_query(query_comparison, self.conn)
            
            print("テーブル比較:")
            print(result_comparison.to_string(index=False))
            
            return result_comparison
            
        except Exception as e:
            print(f"データ移行調査エラー: {e}")
            return None
    
    def run_investigation(self):
        """調査実行"""
        print("=== 根本原因調査実行 ===")
        
        # 1) 元のデータの調査
        result_original, sample_original = self.investigate_original_data()
        if result_original is None:
            return False
        
        # 2) SE_FEテーブルの調査
        result_se_fe, sample_se_fe = self.investigate_se_fe_data()
        if result_se_fe is None:
            return False
        
        # 3) データ移行の調査
        result_comparison = self.investigate_data_migration()
        if result_comparison is None:
            return False
        
        print("\n✅ 根本原因調査完了")
        return True

def main():
    investigator = RootCauseInvestigator()
    success = investigator.run_investigation()
    
    if success:
        print("\n✅ 根本原因調査成功")
    else:
        print("\n❌ 根本原因調査失敗")

if __name__ == "__main__":
    main()




