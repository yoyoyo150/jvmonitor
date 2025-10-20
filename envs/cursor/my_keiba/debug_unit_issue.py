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

class UnitIssueDebugger:
    """単位問題のデバッグ"""
    
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
    
    def debug_zi_index(self):
        """ZI_Indexの詳細分析"""
        print("=== ZI_Index詳細分析 ===")
        
        try:
            # ZI_Indexの分布分析
            query = """
            SELECT
                COUNT(*) as total_count,
                AVG(ZI_Index) as avg_value,
                MIN(ZI_Index) as min_value,
                MAX(ZI_Index) as max_value,
                COUNT(CASE WHEN ZI_Index >= 150 AND ZI_Index = CAST(ZI_Index AS INTEGER) THEN 1 END) as yen_like_count,
                COUNT(CASE WHEN ZI_Index < 50 AND ABS(ZI_Index - CAST(ZI_Index AS INTEGER)) > 0.0 THEN 1 END) as decimal_like_count,
                COUNT(CASE WHEN ZI_Index BETWEEN 100 AND 200 THEN 1 END) as range_100_200,
                COUNT(CASE WHEN ZI_Index BETWEEN 200 AND 500 THEN 1 END) as range_200_500,
                COUNT(CASE WHEN ZI_Index > 500 THEN 1 END) as range_over_500
            FROM SE_FE
            WHERE ZI_Index IS NOT NULL
            """
            result = pd.read_sql_query(query, self.conn)
            
            print("ZI_Index統計:")
            print(f"  総件数: {result.iloc[0]['total_count']}")
            print(f"  平均値: {result.iloc[0]['avg_value']:.2f}")
            print(f"  最小値: {result.iloc[0]['min_value']:.2f}")
            print(f"  最大値: {result.iloc[0]['max_value']:.2f}")
            print(f"  円らしい件数: {result.iloc[0]['yen_like_count']}")
            print(f"  小数らしい件数: {result.iloc[0]['decimal_like_count']}")
            print(f"  100-200円範囲: {result.iloc[0]['range_100_200']}")
            print(f"  200-500円範囲: {result.iloc[0]['range_200_500']}")
            print(f"  500円超: {result.iloc[0]['range_over_500']}")
            
            # サンプルデータ表示
            query_sample = """
            SELECT ZI_Index, win_pay_yen, Chaku
            FROM SE_FE
            WHERE ZI_Index IS NOT NULL
            ORDER BY ZI_Index
            LIMIT 20
            """
            sample = pd.read_sql_query(query_sample, self.conn)
            print("\nZI_Indexサンプル:")
            print(sample.to_string(index=False))
            
            return result
            
        except Exception as e:
            print(f"ZI_Index分析エラー: {e}")
            return None
    
    def debug_zm_value(self):
        """ZM_Valueの詳細分析"""
        print("\n=== ZM_Value詳細分析 ===")
        
        try:
            # ZM_Valueの分布分析
            query = """
            SELECT
                COUNT(*) as total_count,
                AVG(ZM_Value) as avg_value,
                MIN(ZM_Value) as min_value,
                MAX(ZM_Value) as max_value,
                COUNT(CASE WHEN ZM_Value >= 110 AND ZM_Value = CAST(ZM_Value AS INTEGER) THEN 1 END) as yen_like_count,
                COUNT(CASE WHEN ZM_Value < 50 AND ABS(ZM_Value - CAST(ZM_Value AS INTEGER)) > 0.0 THEN 1 END) as decimal_like_count,
                COUNT(CASE WHEN ZM_Value BETWEEN 100 AND 200 THEN 1 END) as range_100_200,
                COUNT(CASE WHEN ZM_Value BETWEEN 200 AND 500 THEN 1 END) as range_200_500,
                COUNT(CASE WHEN ZM_Value > 500 THEN 1 END) as range_over_500
            FROM SE_FE
            WHERE ZM_Value IS NOT NULL
            """
            result = pd.read_sql_query(query, self.conn)
            
            print("ZM_Value統計:")
            print(f"  総件数: {result.iloc[0]['total_count']}")
            print(f"  平均値: {result.iloc[0]['avg_value']:.2f}")
            print(f"  最小値: {result.iloc[0]['min_value']:.2f}")
            print(f"  最大値: {result.iloc[0]['max_value']:.2f}")
            print(f"  円らしい件数: {result.iloc[0]['yen_like_count']}")
            print(f"  小数らしい件数: {result.iloc[0]['decimal_like_count']}")
            print(f"  100-200円範囲: {result.iloc[0]['range_100_200']}")
            print(f"  200-500円範囲: {result.iloc[0]['range_200_500']}")
            print(f"  500円超: {result.iloc[0]['range_over_500']}")
            
            # サンプルデータ表示
            query_sample = """
            SELECT ZM_Value, plc_pay_yen_low, Chaku
            FROM SE_FE
            WHERE ZM_Value IS NOT NULL
            ORDER BY ZM_Value
            LIMIT 20
            """
            sample = pd.read_sql_query(query_sample, self.conn)
            print("\nZM_Valueサンプル:")
            print(sample.to_string(index=False))
            
            return result
            
        except Exception as e:
            print(f"ZM_Value分析エラー: {e}")
            return None
    
    def fix_zi_index_unit(self):
        """ZI_Indexの単位修正"""
        print("\n=== ZI_Index単位修正 ===")
        
        try:
            cursor = self.conn.cursor()
            
            # ZI_Indexが実際は「円」である可能性が高い
            # 平均値99.40は「円」の値
            # 倍率×100を元に戻す
            cursor.execute("""
            UPDATE SE_FE
            SET win_pay_yen = CASE
                WHEN ZI_Index IS NULL THEN NULL
                ELSE CAST(ZI_Index AS INTEGER)
            END
            """)
            
            self.conn.commit()
            print("ZI_Indexを「円」として修正")
            
            return True
            
        except Exception as e:
            print(f"ZI_Index単位修正エラー: {e}")
            return False
    
    def recalculate_kpi(self, start_date="2024-11-02", end_date="2025-09-28"):
        """修正後のKPI再計算"""
        print("\n=== 修正後KPI再計算 ===")
        
        try:
            start_date_norm = start_date.replace('-', '')
            end_date_norm = end_date.replace('-', '')
            
            # 単勝KPI（修正後）
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
            
            # 複勝KPI（修正後）
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
            
            print("修正後KPI計算結果:")
            print(kpi_results.to_string(index=False))
            
            # 現実チェック
            tansho_roi = kpi_results[kpi_results['bettype'] == 'tansho']['roi_pct'].iloc[0]
            fukusho_roi = kpi_results[kpi_results['bettype'] == 'fukusho']['roi_pct'].iloc[0]
            
            print(f"\n現実チェック:")
            print(f"単勝ROI: {tansho_roi}%")
            print(f"複勝ROI: {fukusho_roi}%")
            
            if 30 <= tansho_roi <= 130 and 30 <= fukusho_roi <= 130:
                print("✅ ROIが現実的なレンジ内")
                return True
            else:
                print("❌ ROIが現実的でない")
                return False
            
        except Exception as e:
            print(f"修正後KPI再計算エラー: {e}")
            return False
    
    def run_debug_and_fix(self):
        """デバッグと修正実行"""
        print("=== デバッグと修正実行 ===")
        
        # 1) ZI_Index分析
        self.debug_zi_index()
        
        # 2) ZM_Value分析
        self.debug_zm_value()
        
        # 3) ZI_Index単位修正
        if not self.fix_zi_index_unit():
            return False
        
        # 4) 修正後KPI再計算
        if not self.recalculate_kpi():
            return False
        
        print("✅ デバッグと修正完了")
        return True

def main():
    debugger = UnitIssueDebugger()
    success = debugger.run_debug_and_fix()
    
    if success:
        print("\n✅ デバッグと修正成功")
    else:
        print("\n❌ デバッグと修正失敗")

if __name__ == "__main__":
    main()




