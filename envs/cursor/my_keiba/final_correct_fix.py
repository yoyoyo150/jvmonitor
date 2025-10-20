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

class FinalCorrectFix:
    """最終修正 - 正しい単位判定と修正"""
    
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
    
    def analyze_data_distribution(self):
        """データ分布の詳細分析"""
        print("=== データ分布の詳細分析 ===")
        
        try:
            # ZI_Indexの分布分析
            query_zi = """
            SELECT 
                ZI_Index,
                COUNT(*) as count
            FROM SE_FE
            WHERE ZI_Index IS NOT NULL AND ZI_Index != '' AND ZI_Index != '0' AND ZI_Index != 0
            GROUP BY ZI_Index
            ORDER BY CAST(ZI_Index AS REAL)
            LIMIT 20
            """
            result_zi = pd.read_sql_query(query_zi, self.conn)
            
            print("ZI_Index分布（上位20）:")
            print(result_zi.to_string(index=False))
            
            # ZM_Valueの分布分析
            query_zm = """
            SELECT 
                ZM_Value,
                COUNT(*) as count
            FROM SE_FE
            WHERE ZM_Value IS NOT NULL AND ZM_Value != '' AND ZM_Value != '0' AND ZM_Value != 0
            GROUP BY ZM_Value
            ORDER BY CAST(ZM_Value AS REAL)
            LIMIT 20
            """
            result_zm = pd.read_sql_query(query_zm, self.conn)
            
            print("\nZM_Value分布（上位20）:")
            print(result_zm.to_string(index=False))
            
            return result_zi, result_zm
            
        except Exception as e:
            print(f"データ分布分析エラー: {e}")
            return None, None
    
    def determine_final_units(self, result_zi, result_zm):
        """最終単位の判定"""
        print("\n=== 最終単位の判定 ===")
        
        try:
            # ZI_Indexの判定
            zi_values = result_zi['ZI_Index'].astype(float)
            zi_avg = zi_values.mean()
            zi_median = zi_values.median()
            zi_std = zi_values.std()
            
            print(f"ZI_Index統計:")
            print(f"  平均値: {zi_avg:.2f}")
            print(f"  中央値: {zi_median:.2f}")
            print(f"  標準偏差: {zi_std:.2f}")
            
            # ZI_Indexは「円」の可能性が高い（平均値が100前後、標準偏差が小さい）
            if zi_avg < 200 and zi_std < 50:
                zi_is_yen = True
                print("  → 円として判定（平均値が100前後、標準偏差が小さい）")
            else:
                zi_is_yen = False
                print("  → 倍率として判定")
            
            # ZM_Valueの判定
            zm_values = result_zm['ZM_Value'].astype(float)
            zm_avg = zm_values.mean()
            zm_median = zm_values.median()
            zm_std = zm_values.std()
            
            print(f"\nZM_Value統計:")
            print(f"  平均値: {zm_avg:.2f}")
            print(f"  中央値: {zm_median:.2f}")
            print(f"  標準偏差: {zm_std:.2f}")
            
            # ZM_Valueは「円」の可能性が高い（平均値が700前後）
            if zm_avg > 500:
                zm_is_yen = True
                print("  → 円として判定（平均値が700前後）")
            else:
                zm_is_yen = False
                print("  → 倍率として判定")
            
            return zi_is_yen, zm_is_yen
            
        except Exception as e:
            print(f"最終単位判定エラー: {e}")
            return False, False
    
    def apply_final_units(self, zi_is_yen, zm_is_yen):
        """最終単位の適用"""
        print("\n=== 最終単位の適用 ===")
        
        try:
            cursor = self.conn.cursor()
            
            # 単勝の単位適用
            if zi_is_yen:
                cursor.execute("""
                UPDATE SE_FE
                SET win_pay_yen = CASE
                    WHEN ZI_Index IS NULL OR ZI_Index = '' OR ZI_Index = '0' OR ZI_Index = 0 THEN NULL
                    ELSE CAST(ZI_Index AS INTEGER)
                END
                """)
                print("単勝: 円のまま使用")
            else:
                cursor.execute("""
                UPDATE SE_FE
                SET win_pay_yen = CASE
                    WHEN ZI_Index IS NULL OR ZI_Index = '' OR ZI_Index = '0' OR ZI_Index = 0 THEN NULL
                    ELSE CAST(ROUND(CAST(ZI_Index AS REAL) * 100) AS INTEGER)
                END
                """)
                print("単勝: 倍率×100円で変換")
            
            # 複勝の単位適用
            if zm_is_yen:
                cursor.execute("""
                UPDATE SE_FE
                SET plc_pay_yen_low = CASE
                    WHEN ZM_Value IS NULL OR ZM_Value = '' OR ZM_Value = '0' OR ZM_Value = 0 THEN NULL
                    ELSE CAST(ZM_Value AS INTEGER)
                END
                """)
                print("複勝: 円のまま使用")
            else:
                cursor.execute("""
                UPDATE SE_FE
                SET plc_pay_yen_low = CASE
                    WHEN ZM_Value IS NULL OR ZM_Value = '' OR ZM_Value = '0' OR ZM_Value = 0 THEN NULL
                    ELSE CAST(ROUND(CAST(ZM_Value AS REAL) * 100) AS INTEGER)
                END
                """)
                print("複勝: 倍率×100円で変換")
            
            self.conn.commit()
            print("最終単位の適用完了")
            
            return True
            
        except Exception as e:
            print(f"最終単位の適用エラー: {e}")
            return False
    
    def calculate_final_kpi(self, start_date="2024-11-02", end_date="2025-09-28"):
        """最終KPI計算"""
        print("\n=== 最終KPI計算 ===")
        
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
            
            print("最終KPI計算結果:")
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
            print(f"最終KPI計算エラー: {e}")
            return False
    
    def run_final_fix(self):
        """最終修正実行"""
        print("=== 最終修正実行 ===")
        
        # 1) データ分布の詳細分析
        result_zi, result_zm = self.analyze_data_distribution()
        if result_zi is None or result_zm is None:
            return False
        
        # 2) 最終単位の判定
        zi_is_yen, zm_is_yen = self.determine_final_units(result_zi, result_zm)
        
        # 3) 最終単位の適用
        if not self.apply_final_units(zi_is_yen, zm_is_yen):
            return False
        
        # 4) 最終KPI計算
        if not self.calculate_final_kpi():
            return False
        
        print("✅ 最終修正完了")
        return True

def main():
    fixer = FinalCorrectFix()
    success = fixer.run_final_fix()
    
    if success:
        print("\n✅ 最終修正成功")
    else:
        print("\n❌ 最終修正失敗")

if __name__ == "__main__":
    main()




