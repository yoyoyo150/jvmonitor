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

class DebugROIInputCorrect:
    """正しいROI入力デバッグ"""
    
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
    
    def show_v_roi_input_sample(self):
        """V_ROI_INPUT_CORRECTの10行表示"""
        print("=== V_ROI_INPUT_CORRECTの10行表示 ===")
        
        try:
            query = """
            SELECT 
              race_id,
              horse_id,
              finish,
              win_pay_yen,
              plc_pay_yen_low
            FROM V_ROI_INPUT_CORRECT
            WHERE finish IS NOT NULL
            ORDER BY race_id DESC
            LIMIT 10
            """
            result = pd.read_sql_query(query, self.conn)
            
            print("V_ROI_INPUT_CORRECTサンプル（10行）:")
            print(result.to_string(index=False))
            
            return result
            
        except Exception as e:
            print(f"V_ROI_INPUT_CORRECTサンプル表示エラー: {e}")
            return None
    
    def analyze_win_pay_yen_distribution(self):
        """win_pay_yen分布分析"""
        print("=== win_pay_yen分布分析 ===")
        
        try:
            query = """
            SELECT 
              COUNT(*) as total_count,
              AVG(win_pay_yen) as avg_value,
              MIN(win_pay_yen) as min_value,
              MAX(win_pay_yen) as max_value,
              COUNT(CASE WHEN win_pay_yen > 1000 THEN 1 END) as over_1000_count,
              COUNT(CASE WHEN win_pay_yen > 10000 THEN 1 END) as over_10000_count,
              COUNT(CASE WHEN win_pay_yen > 50000 THEN 1 END) as over_50000_count
            FROM V_ROI_INPUT_CORRECT
            WHERE win_pay_yen IS NOT NULL
            """
            result = pd.read_sql_query(query, self.conn)
            
            print("win_pay_yen分布:")
            print(f"  総件数: {result.iloc[0]['total_count']}")
            print(f"  平均値: {result.iloc[0]['avg_value']:.2f}")
            print(f"  最小値: {result.iloc[0]['min_value']:.2f}")
            print(f"  最大値: {result.iloc[0]['max_value']:.2f}")
            print(f"  1,000円超: {result.iloc[0]['over_1000_count']}")
            print(f"  10,000円超: {result.iloc[0]['over_10000_count']}")
            print(f"  50,000円超: {result.iloc[0]['over_50000_count']}")
            
            return result
            
        except Exception as e:
            print(f"win_pay_yen分布分析エラー: {e}")
            return None
    
    def show_abnormal_values(self):
        """異常値の表示"""
        print("=== 異常値の表示 ===")
        
        try:
            query = """
            SELECT 
              race_id,
              horse_id,
              finish,
              win_pay_yen,
              plc_pay_yen_low
            FROM V_ROI_INPUT_CORRECT
            WHERE win_pay_yen > 10000
            ORDER BY win_pay_yen DESC
            LIMIT 10
            """
            result = pd.read_sql_query(query, self.conn)
            
            print("異常値サンプル（10,000円超）:")
            print(result.to_string(index=False))
            
            return result
            
        except Exception as e:
            print(f"異常値表示エラー: {e}")
            return None
    
    def run_debug(self):
        """デバッグ実行"""
        print("=== 正しいROI入力デバッグ実行 ===")
        
        try:
            # 1) V_ROI_INPUT_CORRECTの10行表示
            sample = self.show_v_roi_input_sample()
            if sample is None:
                return False
            
            # 2) win_pay_yen分布分析
            distribution = self.analyze_win_pay_yen_distribution()
            if distribution is None:
                return False
            
            # 3) 異常値の表示
            abnormal = self.show_abnormal_values()
            if abnormal is None:
                return False
            
            print("✅ デバッグ完了")
            return True
            
        except Exception as e:
            print(f"デバッグ実行エラー: {e}")
            return False

def main():
    debugger = DebugROIInputCorrect()
    success = debugger.run_debug()
    
    if success:
        print("\n✅ デバッグ成功")
    else:
        print("\n❌ デバッグ失敗")

if __name__ == "__main__":
    main()




