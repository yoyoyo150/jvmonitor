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

class UltimateUltimateFix:
    """究極の究極の修正 - 正しい単位判定と修正"""
    
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
    
    def analyze_ultimate_ultimate_units(self):
        """究極の究極の単位分析"""
        print("=== 究極の究極の単位分析 ===")
        
        try:
            # ZI_Indexの分析
            query_zi = """
            SELECT 
                COUNT(*) as total_count,
                AVG(CAST(ZI_Index AS REAL)) as avg_value,
                MIN(CAST(ZI_Index AS REAL)) as min_value,
                MAX(CAST(ZI_Index AS REAL)) as max_value
            FROM SE_FE
            WHERE ZI_Index IS NOT NULL AND ZI_Index != '' AND ZI_Index != '0' AND ZI_Index != 0
            """
            result_zi = pd.read_sql_query(query_zi, self.conn)
            
            print("ZI_Index統計:")
            print(f"  総件数: {result_zi.iloc[0]['total_count']}")
            print(f"  平均値: {result_zi.iloc[0]['avg_value']:.2f}")
            print(f"  最小値: {result_zi.iloc[0]['min_value']:.2f}")
            print(f"  最大値: {result_zi.iloc[0]['max_value']:.2f}")
            
            # ZM_Valueの分析
            query_zm = """
            SELECT 
                COUNT(*) as total_count,
                AVG(CAST(ZM_Value AS REAL)) as avg_value,
                MIN(CAST(ZM_Value AS REAL)) as min_value,
                MAX(CAST(ZM_Value AS REAL)) as max_value
            FROM SE_FE
            WHERE ZM_Value IS NOT NULL AND ZM_Value != '' AND ZM_Value != '0' AND ZM_Value != 0
            """
            result_zm = pd.read_sql_query(query_zm, self.conn)
            
            print("\nZM_Value統計:")
            print(f"  総件数: {result_zm.iloc[0]['total_count']}")
            print(f"  平均値: {result_zm.iloc[0]['avg_value']:.2f}")
            print(f"  最小値: {result_zm.iloc[0]['min_value']:.2f}")
            print(f"  最大値: {result_zm.iloc[0]['max_value']:.2f}")
            
            return result_zi, result_zm
            
        except Exception as e:
            print(f"究極の究極の単位分析エラー: {e}")
            return None, None
    
    def determine_ultimate_ultimate_units(self, result_zi, result_zm):
        """究極の究極の単位判定"""
        print("\n=== 究極の究極の単位判定 ===")
        
        try:
            # ZI_Indexの判定
            zi_avg = result_zi.iloc[0]['avg_value']
            zi_min = result_zi.iloc[0]['min_value']
            zi_max = result_zi.iloc[0]['max_value']
            
            print(f"ZI_Index判定:")
            print(f"  平均値: {zi_avg:.2f}")
            print(f"  範囲: {zi_min:.2f} - {zi_max:.2f}")
            
            # ZI_Indexは「倍率」の可能性が高い（平均値が100前後、範囲が60-150）
            if zi_avg < 200 and zi_max < 200:
                zi_is_yen = False
                print("  → 倍率として判定（平均値が100前後、範囲が60-150）")
            else:
                zi_is_yen = True
                print("  → 円として判定")
            
            # ZM_Valueの判定
            zm_avg = result_zm.iloc[0]['avg_value']
            zm_min = result_zm.iloc[0]['min_value']
            zm_max = result_zm.iloc[0]['max_value']
            
            print(f"\nZM_Value判定:")
            print(f"  平均値: {zm_avg:.2f}")
            print(f"  範囲: {zm_min:.2f} - {zm_max:.2f}")
            
            # ZM_Valueは「円」の可能性が高い（平均値が700前後、範囲が10-9999）
            if zm_avg > 500:
                zm_is_yen = True
                print("  → 円として判定（平均値が700前後、範囲が10-9999）")
            else:
                zm_is_yen = False
                print("  → 倍率として判定")
            
            return zi_is_yen, zm_is_yen
            
        except Exception as e:
            print(f"究極の究極の単位判定エラー: {e}")
            return False, False
    
    def apply_ultimate_ultimate_units(self, zi_is_yen, zm_is_yen):
        """究極の究極の単位の適用"""
        print("\n=== 究極の究極の単位の適用 ===")
        
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
            print("究極の究極の単位の適用完了")
            
            return True
            
        except Exception as e:
            print(f"究極の究極の単位の適用エラー: {e}")
            return False
    
    def calculate_ultimate_ultimate_kpi(self, start_date="2024-11-02", end_date="2025-09-28"):
        """究極の究極のKPI計算"""
        print("\n=== 究極の究極のKPI計算 ===")
        
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
            
            print("究極の究極のKPI計算結果:")
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
            print(f"究極の究極のKPI計算エラー: {e}")
            return False
    
    def run_ultimate_ultimate_fix(self):
        """究極の究極の修正実行"""
        print("=== 究極の究極の修正実行 ===")
        
        # 1) 究極の究極の単位分析
        result_zi, result_zm = self.analyze_ultimate_ultimate_units()
        if result_zi is None or result_zm is None:
            return False
        
        # 2) 究極の究極の単位の判定
        zi_is_yen, zm_is_yen = self.determine_ultimate_ultimate_units(result_zi, result_zm)
        
        # 3) 究極の究極の単位の適用
        if not self.apply_ultimate_ultimate_units(zi_is_yen, zm_is_yen):
            return False
        
        # 4) 究極の究極のKPI計算
        if not self.calculate_ultimate_ultimate_kpi():
            return False
        
        print("✅ 究極の究極の修正完了")
        return True

def main():
    fixer = UltimateUltimateFix()
    success = fixer.run_ultimate_ultimate_fix()
    
    if success:
        print("\n✅ 究極の究極の修正成功")
    else:
        print("\n❌ 究極の究極の修正失敗")

if __name__ == "__main__":
    main()




