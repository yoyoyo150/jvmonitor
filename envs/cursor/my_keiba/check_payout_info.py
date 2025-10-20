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

class CheckPayoutInfo:
    """払い戻し情報の確認"""
    
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
    
    def check_payout_columns(self):
        """払い戻し列の確認"""
        print("=== 払い戻し列の確認 ===")
        
        try:
            # 払い戻し関連列の確認
            query_payout = """
            SELECT 
                COUNT(*) as total_records,
                COUNT(win_pay_yen) as win_pay_count,
                COUNT(plc_pay_yen_low) as plc_pay_count,
                AVG(win_pay_yen) as win_pay_avg,
                AVG(plc_pay_yen_low) as plc_pay_avg,
                MIN(win_pay_yen) as win_pay_min,
                MAX(win_pay_yen) as win_pay_max,
                MIN(plc_pay_yen_low) as plc_pay_min,
                MAX(plc_pay_yen_low) as plc_pay_max
            FROM SE_FE
            WHERE win_pay_yen IS NOT NULL OR plc_pay_yen_low IS NOT NULL
            """
            result_payout = pd.read_sql_query(query_payout, self.conn)
            
            print("払い戻し列状況:")
            print(f"  総レコード数: {result_payout.iloc[0]['total_records']}")
            print(f"  win_pay_yen列数: {result_payout.iloc[0]['win_pay_count']}")
            print(f"  plc_pay_yen_low列数: {result_payout.iloc[0]['plc_pay_count']}")
            print(f"  win_pay_yen平均: {result_payout.iloc[0]['win_pay_avg']:.2f}")
            print(f"  plc_pay_yen_low平均: {result_payout.iloc[0]['plc_pay_avg']:.2f}")
            print(f"  win_pay_yen範囲: {result_payout.iloc[0]['win_pay_min']:.2f} - {result_payout.iloc[0]['win_pay_max']:.2f}")
            print(f"  plc_pay_yen_low範囲: {result_payout.iloc[0]['plc_pay_min']:.2f} - {result_payout.iloc[0]['plc_pay_max']:.2f}")
            
            return result_payout
            
        except Exception as e:
            print(f"払い戻し列確認エラー: {e}")
            return None
    
    def check_winning_horses_payout(self):
        """1着馬の払い戻し確認"""
        print("=== 1着馬の払い戻し確認 ===")
        
        try:
            # 1着馬の払い戻し確認
            query_winning = """
            SELECT 
                SourceDate,
                HorseNameS,
                Chaku,
                Tansho_Odds,
                win_pay_yen,
                plc_pay_yen_low
            FROM SE_FE
            WHERE CAST(Chaku AS INTEGER) = 1
            AND (Tansho_Odds IS NOT NULL OR win_pay_yen IS NOT NULL)
            ORDER BY SourceDate DESC
            LIMIT 10
            """
            result_winning = pd.read_sql_query(query_winning, self.conn)
            
            print("1着馬の払い戻しサンプル（10件）:")
            print(result_winning.to_string(index=False))
            
            return result_winning
            
        except Exception as e:
            print(f"1着馬の払い戻し確認エラー: {e}")
            return None
    
    def calculate_correct_roi_with_payout(self):
        """正しいROI計算（払い戻し情報使用）"""
        print("=== 正しいROI計算（払い戻し情報使用） ===")
        
        try:
            # 単勝ROI計算（1着の払い戻しを使用）
            query_tansho = """
            SELECT
                'tansho' AS bettype,
                COUNT(*) AS bets,
                COUNT(*) * 100 AS stake_yen,
                SUM(CASE 
                    WHEN CAST(Chaku AS INTEGER) = 1 AND win_pay_yen IS NOT NULL 
                    THEN win_pay_yen 
                    ELSE 0 
                END) AS payoff_yen,
                ROUND(100.0 * SUM(CASE 
                    WHEN CAST(Chaku AS INTEGER) = 1 AND win_pay_yen IS NOT NULL 
                    THEN win_pay_yen 
                    ELSE 0 
                END) / NULLIF(COUNT(*) * 100.0, 0), 2) AS roi_pct
            FROM SE_FE
            WHERE win_pay_yen IS NOT NULL
            """
            result_tansho = pd.read_sql_query(query_tansho, self.conn)
            
            # 複勝ROI計算（1-3着の払い戻しを使用）
            query_fukusho = """
            SELECT
                'fukusho' AS bettype,
                COUNT(*) AS bets,
                COUNT(*) * 100 AS stake_yen,
                SUM(CASE 
                    WHEN CAST(Chaku AS INTEGER) BETWEEN 1 AND 3 AND plc_pay_yen_low IS NOT NULL 
                    THEN plc_pay_yen_low 
                    ELSE 0 
                END) AS payoff_yen,
                ROUND(100.0 * SUM(CASE 
                    WHEN CAST(Chaku AS INTEGER) BETWEEN 1 AND 3 AND plc_pay_yen_low IS NOT NULL 
                    THEN plc_pay_yen_low 
                    ELSE 0 
                END) / NULLIF(COUNT(*) * 100.0, 0), 2) AS roi_pct
            FROM SE_FE
            WHERE plc_pay_yen_low IS NOT NULL
            """
            result_fukusho = pd.read_sql_query(query_fukusho, self.conn)
            
            # 結果を結合
            kpi_results = pd.concat([result_tansho, result_fukusho], ignore_index=True)
            
            print("正しいROI計算結果（払い戻し情報使用）:")
            print(kpi_results.to_string(index=False))
            
            return kpi_results
            
        except Exception as e:
            print(f"正しいROI計算エラー: {e}")
            return None
    
    def run_payout_info_check(self):
        """払い戻し情報確認実行"""
        print("=== 払い戻し情報確認実行 ===")
        
        try:
            # 1) 払い戻し列の確認
            payout_result = self.check_payout_columns()
            if payout_result is None:
                return False
            
            # 2) 1着馬の払い戻し確認
            winning_result = self.check_winning_horses_payout()
            if winning_result is None:
                return False
            
            # 3) 正しいROI計算
            roi_result = self.calculate_correct_roi_with_payout()
            if roi_result is None:
                return False
            
            print("✅ 払い戻し情報確認完了")
            return True
            
        except Exception as e:
            print(f"払い戻し情報確認実行エラー: {e}")
            return False

def main():
    checker = CheckPayoutInfo()
    success = checker.run_payout_info_check()
    
    if success:
        print("\n✅ 払い戻し情報確認成功")
    else:
        print("\n❌ 払い戻し情報確認失敗")

if __name__ == "__main__":
    main()




