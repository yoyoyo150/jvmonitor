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

class SampleDataInvestigator:
    """サンプルデータの調査"""
    
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
    
    def investigate_win_pay_yen(self):
        """win_pay_yenの詳細調査"""
        print("=== win_pay_yenの詳細調査 ===")
        
        try:
            # win_pay_yenの統計
            query_stats = """
            SELECT 
                COUNT(*) as total_count,
                COUNT(CASE WHEN win_pay_yen IS NOT NULL THEN 1 END) as not_null_count,
                AVG(win_pay_yen) as avg_value,
                MIN(win_pay_yen) as min_value,
                MAX(win_pay_yen) as max_value,
                COUNT(CASE WHEN win_pay_yen > 10000 THEN 1 END) as over_10000_count,
                COUNT(CASE WHEN win_pay_yen > 50000 THEN 1 END) as over_50000_count
            FROM SE_FE
            WHERE win_pay_yen IS NOT NULL
            """
            result_stats = pd.read_sql_query(query_stats, self.conn)
            
            print("win_pay_yen統計:")
            print(f"  総件数: {result_stats.iloc[0]['total_count']}")
            print(f"  非NULL件数: {result_stats.iloc[0]['not_null_count']}")
            print(f"  平均値: {result_stats.iloc[0]['avg_value']:.2f}")
            print(f"  最小値: {result_stats.iloc[0]['min_value']:.2f}")
            print(f"  最大値: {result_stats.iloc[0]['max_value']:.2f}")
            print(f"  10,000円超: {result_stats.iloc[0]['over_10000_count']}")
            print(f"  50,000円超: {result_stats.iloc[0]['over_50000_count']}")
            
            # 異常値のサンプル
            query_abnormal = """
            SELECT 
                race_id,
                horse_id,
                finish,
                win_pay_yen,
                ZI_Index,
                ZM_Value
            FROM SE_FE
            WHERE win_pay_yen > 10000
            ORDER BY win_pay_yen DESC
            LIMIT 10
            """
            result_abnormal = pd.read_sql_query(query_abnormal, self.conn)
            
            print("\n異常値サンプル（10,000円超）:")
            print(result_abnormal.to_string(index=False))
            
            return result_stats, result_abnormal
            
        except Exception as e:
            print(f"win_pay_yen調査エラー: {e}")
            return None, None
    
    def investigate_plc_pay_yen_low(self):
        """plc_pay_yen_lowの詳細調査"""
        print("\n=== plc_pay_yen_lowの詳細調査 ===")
        
        try:
            # plc_pay_yen_lowの統計
            query_stats = """
            SELECT 
                COUNT(*) as total_count,
                COUNT(CASE WHEN plc_pay_yen_low IS NOT NULL THEN 1 END) as not_null_count,
                AVG(plc_pay_yen_low) as avg_value,
                MIN(plc_pay_yen_low) as min_value,
                MAX(plc_pay_yen_low) as max_value,
                COUNT(CASE WHEN plc_pay_yen_low > 10000 THEN 1 END) as over_10000_count,
                COUNT(CASE WHEN plc_pay_yen_low > 50000 THEN 1 END) as over_50000_count
            FROM SE_FE
            WHERE plc_pay_yen_low IS NOT NULL
            """
            result_stats = pd.read_sql_query(query_stats, self.conn)
            
            print("plc_pay_yen_low統計:")
            print(f"  総件数: {result_stats.iloc[0]['total_count']}")
            print(f"  非NULL件数: {result_stats.iloc[0]['not_null_count']}")
            print(f"  平均値: {result_stats.iloc[0]['avg_value']:.2f}")
            print(f"  最小値: {result_stats.iloc[0]['min_value']:.2f}")
            print(f"  最大値: {result_stats.iloc[0]['max_value']:.2f}")
            print(f"  10,000円超: {result_stats.iloc[0]['over_10000_count']}")
            print(f"  50,000円超: {result_stats.iloc[0]['over_50000_count']}")
            
            # 異常値のサンプル
            query_abnormal = """
            SELECT 
                race_id,
                horse_id,
                finish,
                plc_pay_yen_low,
                ZI_Index,
                ZM_Value
            FROM SE_FE
            WHERE plc_pay_yen_low > 10000
            ORDER BY plc_pay_yen_low DESC
            LIMIT 10
            """
            result_abnormal = pd.read_sql_query(query_abnormal, self.conn)
            
            print("\n異常値サンプル（10,000円超）:")
            print(result_abnormal.to_string(index=False))
            
            return result_stats, result_abnormal
            
        except Exception as e:
            print(f"plc_pay_yen_low調査エラー: {e}")
            return None, None
    
    def investigate_original_columns(self):
        """元の列の調査"""
        print("\n=== 元の列の調査 ===")
        
        try:
            # ZI_IndexとZM_Valueの統計
            query_original = """
            SELECT 
                COUNT(*) as total_count,
                AVG(CAST(ZI_Index AS REAL)) as zi_avg,
                MIN(CAST(ZI_Index AS REAL)) as zi_min,
                MAX(CAST(ZI_Index AS REAL)) as zi_max,
                AVG(CAST(ZM_Value AS REAL)) as zm_avg,
                MIN(CAST(ZM_Value AS REAL)) as zm_min,
                MAX(CAST(ZM_Value AS REAL)) as zm_max
            FROM SE_FE
            WHERE ZI_Index IS NOT NULL AND ZI_Index != '' AND ZI_Index != '0' AND ZI_Index != 0
            AND ZM_Value IS NOT NULL AND ZM_Value != '' AND ZM_Value != '0' AND ZM_Value != 0
            """
            result_original = pd.read_sql_query(query_original, self.conn)
            
            print("元の列統計:")
            print(f"  総件数: {result_original.iloc[0]['total_count']}")
            print(f"  ZI_Index平均: {result_original.iloc[0]['zi_avg']:.2f}")
            print(f"  ZI_Index範囲: {result_original.iloc[0]['zi_min']:.2f} - {result_original.iloc[0]['zi_max']:.2f}")
            print(f"  ZM_Value平均: {result_original.iloc[0]['zm_avg']:.2f}")
            print(f"  ZM_Value範囲: {result_original.iloc[0]['zm_min']:.2f} - {result_original.iloc[0]['zm_max']:.2f}")
            
            return result_original
            
        except Exception as e:
            print(f"元の列調査エラー: {e}")
            return None
    
    def run_investigation(self):
        """調査実行"""
        print("=== サンプルデータ調査実行 ===")
        
        # 1) win_pay_yenの詳細調査
        stats_win, abnormal_win = self.investigate_win_pay_yen()
        if stats_win is None:
            return False
        
        # 2) plc_pay_yen_lowの詳細調査
        stats_plc, abnormal_plc = self.investigate_plc_pay_yen_low()
        if stats_plc is None:
            return False
        
        # 3) 元の列の調査
        original = self.investigate_original_columns()
        if original is None:
            return False
        
        print("\n✅ サンプルデータ調査完了")
        return True

def main():
    investigator = SampleDataInvestigator()
    success = investigator.run_investigation()
    
    if success:
        print("\n✅ サンプルデータ調査成功")
    else:
        print("\n❌ サンプルデータ調査失敗")

if __name__ == "__main__":
    main()




