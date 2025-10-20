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

class WinPayYenFixer:
    """win_pay_yen修正"""
    
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
    
    def fix_win_pay_yen(self):
        """win_pay_yen修正（円のまま使用）"""
        print("=== win_pay_yen修正 ===")
        
        try:
            cursor = self.conn.cursor()
            
            # ZI_Indexを円のまま使用（×100しない）
            cursor.execute("""
            UPDATE SE_FE
            SET win_pay_yen = CASE
                WHEN ZI_Index IS NULL OR ZI_Index = '' OR ZI_Index = '0' OR ZI_Index = 0 THEN NULL
                ELSE CAST(ZI_Index AS INTEGER)
            END
            """)
            
            self.conn.commit()
            print("win_pay_yen修正完了（円のまま使用）")
            
            return True
            
        except Exception as e:
            print(f"win_pay_yen修正エラー: {e}")
            return False
    
    def verify_fix(self):
        """修正の検証"""
        print("=== 修正の検証 ===")
        
        try:
            # 修正後の統計
            query_stats = """
            SELECT 
                COUNT(*) as total_count,
                AVG(win_pay_yen) as avg_value,
                MIN(win_pay_yen) as min_value,
                MAX(win_pay_yen) as max_value,
                COUNT(CASE WHEN win_pay_yen > 1000 THEN 1 END) as over_1000_count,
                COUNT(CASE WHEN win_pay_yen > 5000 THEN 1 END) as over_5000_count
            FROM SE_FE
            WHERE win_pay_yen IS NOT NULL
            """
            result_stats = pd.read_sql_query(query_stats, self.conn)
            
            print("修正後win_pay_yen統計:")
            print(f"  総件数: {result_stats.iloc[0]['total_count']}")
            print(f"  平均値: {result_stats.iloc[0]['avg_value']:.2f}")
            print(f"  最小値: {result_stats.iloc[0]['min_value']:.2f}")
            print(f"  最大値: {result_stats.iloc[0]['max_value']:.2f}")
            print(f"  1,000円超: {result_stats.iloc[0]['over_1000_count']}")
            print(f"  5,000円超: {result_stats.iloc[0]['over_5000_count']}")
            
            # サンプルデータ
            query_sample = """
            SELECT 
                SourceDate,
                HorseNameS,
                CAST(Chaku AS INTEGER) as finish,
                win_pay_yen,
                ZI_Index
            FROM SE_FE
            WHERE win_pay_yen IS NOT NULL
            ORDER BY win_pay_yen DESC
            LIMIT 10
            """
            result_sample = pd.read_sql_query(query_sample, self.conn)
            
            print("\n修正後サンプル（上位10件）:")
            print(result_sample.to_string(index=False))
            
            return result_stats, result_sample
            
        except Exception as e:
            print(f"修正検証エラー: {e}")
            return None, None
    
    def calculate_fixed_roi(self, start_date="2024-11-02", end_date="2025-09-28"):
        """修正後のROI計算"""
        print("=== 修正後のROI計算 ===")
        
        try:
            start_date_norm = start_date.replace('-', '')
            end_date_norm = end_date.replace('-', '')
            
            # 単勝KPI
            query_tansho = """
            SELECT
                'tansho' AS bettype,
                COUNT(*) AS bets,
                COUNT(*) * 100 AS stake_yen,
                SUM(CASE WHEN CAST(Chaku AS INTEGER) = 1 AND win_pay_yen IS NOT NULL THEN win_pay_yen ELSE 0 END) AS payoff_yen,
                ROUND(100.0 * SUM(CASE WHEN CAST(Chaku AS INTEGER) = 1 AND win_pay_yen IS NOT NULL THEN win_pay_yen ELSE 0 END)
                      / NULLIF(COUNT(*) * 100.0, 0), 2) AS roi_pct
            FROM SE_FE
            WHERE SourceDate >= ? AND SourceDate <= ?
            AND win_pay_yen IS NOT NULL
            """
            result_tansho = pd.read_sql_query(query_tansho, self.conn, params=[start_date_norm, end_date_norm])
            
            # 複勝KPI
            query_fukusho = """
            SELECT
                'fukusho' AS bettype,
                COUNT(*) AS bets,
                COUNT(*) * 100 AS stake_yen,
                SUM(CASE WHEN CAST(Chaku AS INTEGER) BETWEEN 1 AND 3 AND plc_pay_yen_low IS NOT NULL THEN plc_pay_yen_low ELSE 0 END) AS payoff_yen,
                ROUND(100.0 * SUM(CASE WHEN CAST(Chaku AS INTEGER) BETWEEN 1 AND 3 AND plc_pay_yen_low IS NOT NULL THEN plc_pay_yen_low ELSE 0 END)
                      / NULLIF(COUNT(*) * 100.0, 0), 2) AS roi_pct
            FROM SE_FE
            WHERE SourceDate >= ? AND SourceDate <= ?
            AND plc_pay_yen_low IS NOT NULL
            """
            result_fukusho = pd.read_sql_query(query_fukusho, self.conn, params=[start_date_norm, end_date_norm])
            
            # 結果を結合
            kpi_results = pd.concat([result_tansho, result_fukusho], ignore_index=True)
            
            print("修正後ROI計算結果:")
            print(kpi_results.to_string(index=False))
            
            # 現実チェック
            tansho_roi = kpi_results[kpi_results['bettype'] == 'tansho']['roi_pct'].iloc[0]
            fukusho_roi = kpi_results[kpi_results['bettype'] == 'fukusho']['roi_pct'].iloc[0]
            
            print(f"\n現実チェック:")
            print(f"単勝ROI: {tansho_roi}%")
            print(f"複勝ROI: {fukusho_roi}%")
            
            if 30 <= tansho_roi <= 130 and 40 <= fukusho_roi <= 160:
                print("✅ ROIが常識レンジ内")
                return True
            else:
                print("❌ ROIが常識レンジ外")
                return False
            
        except Exception as e:
            print(f"修正後ROI計算エラー: {e}")
            return False
    
    def run_fix(self):
        """修正実行"""
        print("=== win_pay_yen修正実行 ===")
        
        # 1) win_pay_yen修正
        if not self.fix_win_pay_yen():
            return False
        
        # 2) 修正の検証
        stats, sample = self.verify_fix()
        if stats is None:
            return False
        
        # 3) 修正後のROI計算
        if not self.calculate_fixed_roi():
            return False
        
        print("✅ win_pay_yen修正完了")
        return True

def main():
    fixer = WinPayYenFixer()
    success = fixer.run_fix()
    
    if success:
        print("\n✅ win_pay_yen修正成功")
    else:
        print("\n❌ win_pay_yen修正失敗")

if __name__ == "__main__":
    main()




