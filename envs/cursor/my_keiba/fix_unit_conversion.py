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

class UnitConversionFix:
    """単位変換修正 - オッズと払戻金の混同を修正"""
    
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
    
    def detect_unit_type(self):
        """1) 単位の自動判定"""
        print("=== 単位の自動判定 ===")
        
        try:
            # 単勝の単位判定
            query_win = """
            SELECT
                AVG(CASE WHEN ZI_Index >= 150 AND ZI_Index = CAST(ZI_Index AS INTEGER) THEN 1.0 ELSE 0.0 END) AS p_yen_like,
                AVG(CASE WHEN ZI_Index < 50 AND ABS(ZI_Index - CAST(ZI_Index AS INTEGER)) > 0.0 THEN 1.0 ELSE 0.0 END) AS p_decimal_like,
                COUNT(*) as total_count,
                AVG(ZI_Index) as avg_value
            FROM SE_FE
            WHERE ZI_Index IS NOT NULL
            """
            result_win = pd.read_sql_query(query_win, self.conn)
            
            # 複勝の単位判定
            query_plc = """
            SELECT
                AVG(CASE WHEN ZM_Value >= 110 AND ZM_Value = CAST(ZM_Value AS INTEGER) THEN 1.0 ELSE 0.0 END) AS p_yen_like,
                AVG(CASE WHEN ZM_Value < 50 AND ABS(ZM_Value - CAST(ZM_Value AS INTEGER)) > 0.0 THEN 1.0 ELSE 0.0 END) AS p_decimal_like,
                COUNT(*) as total_count,
                AVG(ZM_Value) as avg_value
            FROM SE_FE
            WHERE ZM_Value IS NOT NULL
            """
            result_plc = pd.read_sql_query(query_plc, self.conn)
            
            print("単勝単位判定:")
            print(f"  円らしさ: {result_win.iloc[0]['p_yen_like']:.2f}")
            print(f"  小数らしさ: {result_win.iloc[0]['p_decimal_like']:.2f}")
            print(f"  平均値: {result_win.iloc[0]['avg_value']:.2f}")
            
            print("複勝単位判定:")
            print(f"  円らしさ: {result_plc.iloc[0]['p_yen_like']:.2f}")
            print(f"  小数らしさ: {result_plc.iloc[0]['p_decimal_like']:.2f}")
            print(f"  平均値: {result_plc.iloc[0]['avg_value']:.2f}")
            
            # 判定結果
            is_win_yen = result_win.iloc[0]['p_yen_like'] >= 0.8
            is_plc_yen = result_plc.iloc[0]['p_yen_like'] >= 0.8
            
            print(f"単勝は{'円' if is_win_yen else '倍率'}")
            print(f"複勝は{'円' if is_plc_yen else '倍率'}")
            
            return is_win_yen, is_plc_yen
            
        except Exception as e:
            print(f"単位判定エラー: {e}")
            return False, False
    
    def create_pay_yen_columns(self):
        """2) 円に統一した払戻列を作成"""
        print("=== 円統一列作成 ===")
        
        try:
            cursor = self.conn.cursor()
            
            # 列を追加
            try:
                cursor.execute("ALTER TABLE SE_FE ADD COLUMN win_pay_yen INTEGER")
                print("win_pay_yen列追加")
            except:
                print("win_pay_yen列は既に存在")
            
            try:
                cursor.execute("ALTER TABLE SE_FE ADD COLUMN plc_pay_yen_low INTEGER")
                print("plc_pay_yen_low列追加")
            except:
                print("plc_pay_yen_low列は既に存在")
            
            # 単位判定
            is_win_yen, is_plc_yen = self.detect_unit_type()
            
            # 単勝の円統一
            if is_win_yen:
                cursor.execute("""
                UPDATE SE_FE
                SET win_pay_yen = CASE
                    WHEN ZI_Index IS NULL THEN NULL
                    ELSE CAST(ZI_Index AS INTEGER)
                END
                """)
                print("単勝: 円のまま使用")
            else:
                cursor.execute("""
                UPDATE SE_FE
                SET win_pay_yen = CASE
                    WHEN ZI_Index IS NULL THEN NULL
                    ELSE CAST(ROUND(ZI_Index * 100) AS INTEGER)
                END
                """)
                print("単勝: 倍率×100円で変換")
            
            # 複勝の円統一
            if is_plc_yen:
                cursor.execute("""
                UPDATE SE_FE
                SET plc_pay_yen_low = CASE
                    WHEN ZM_Value IS NULL THEN NULL
                    ELSE CAST(ZM_Value AS INTEGER)
                END
                """)
                print("複勝: 円のまま使用")
            else:
                cursor.execute("""
                UPDATE SE_FE
                SET plc_pay_yen_low = CASE
                    WHEN ZM_Value IS NULL THEN NULL
                    ELSE CAST(ROUND(ZM_Value * 100) AS INTEGER)
                END
                """)
                print("複勝: 倍率×100円で変換")
            
            self.conn.commit()
            print("円統一列作成完了")
            
            return True
            
        except Exception as e:
            print(f"円統一列作成エラー: {e}")
            return False
    
    def calculate_corrected_kpi(self, start_date="2024-11-02", end_date="2025-09-28"):
        """3) 修正されたKPI計算（円基準）"""
        print("=== 修正KPI計算 ===")
        
        try:
            start_date_norm = start_date.replace('-', '')
            end_date_norm = end_date.replace('-', '')
            
            # 単勝KPI（円基準）
            query_tansho = """
            SELECT
                'tansho' AS bettype,
                COUNT(*) AS bets,
                COUNT(*) * 100 AS stake_yen,
                SUM(CASE WHEN CAST(Chaku AS INTEGER) = 1 AND win_pay_yen IS NOT NULL THEN win_pay_yen ELSE 0 END) AS payoff_yen,
                ROUND(100.0 * SUM(CASE WHEN CAST(Chaku AS INTEGER) = 1 AND win_pay_yen IS NOT NULL THEN win_pay_yen ELSE 0 END)
                      / NULLIF(COUNT(*) * 100.0, 0), 2) AS roi_pct,
                ROUND(AVG(mark5_missing_flag)*100.0,2) AS m5_missing_rate_pct,
                ROUND(AVG(mark6_missing_flag)*100.0,2) AS m6_missing_rate_pct
            FROM SE_FE
            WHERE SourceDate >= ? AND SourceDate <= ?
            AND win_pay_yen IS NOT NULL
            """
            result_tansho = pd.read_sql_query(query_tansho, self.conn, params=[start_date_norm, end_date_norm])
            
            # 複勝KPI（円基準）
            query_fukusho = """
            SELECT
                'fukusho' AS bettype,
                COUNT(*) AS bets,
                COUNT(*) * 100 AS stake_yen,
                SUM(CASE WHEN CAST(Chaku AS INTEGER) BETWEEN 1 AND 3 AND plc_pay_yen_low IS NOT NULL THEN plc_pay_yen_low ELSE 0 END) AS payoff_yen,
                ROUND(100.0 * SUM(CASE WHEN CAST(Chaku AS INTEGER) BETWEEN 1 AND 3 AND plc_pay_yen_low IS NOT NULL THEN plc_pay_yen_low ELSE 0 END)
                      / NULLIF(COUNT(*) * 100.0, 0), 2) AS roi_pct,
                ROUND(AVG(mark5_missing_flag)*100.0,2) AS m5_missing_rate_pct,
                ROUND(AVG(mark6_missing_flag)*100.0,2) AS m6_missing_rate_pct
            FROM SE_FE
            WHERE SourceDate >= ? AND SourceDate <= ?
            AND plc_pay_yen_low IS NOT NULL
            """
            result_fukusho = pd.read_sql_query(query_fukusho, self.conn, params=[start_date_norm, end_date_norm])
            
            # 結果を結合
            kpi_results = pd.concat([result_tansho, result_fukusho], ignore_index=True)
            
            print("修正KPI計算結果:")
            print(kpi_results.to_string(index=False))
            
            return kpi_results
            
        except Exception as e:
            print(f"修正KPI計算エラー: {e}")
            return None
    
    def check_plausible_range(self, kpi_results):
        """4) 現実チェック（自動ブレーキ）"""
        print("=== 現実チェック ===")
        
        try:
            if kpi_results is None or kpi_results.empty:
                print("KPI結果が空です")
                return False
            
            # 単勝のROIチェック
            tansho_roi = kpi_results[kpi_results['bettype'] == 'tansho']['roi_pct'].iloc[0]
            fukusho_roi = kpi_results[kpi_results['bettype'] == 'fukusho']['roi_pct'].iloc[0]
            
            print(f"単勝ROI: {tansho_roi}%")
            print(f"複勝ROI: {fukusho_roi}%")
            
            # 現実的なレンジチェック（30%未満 or 130%超でNG）
            if tansho_roi < 30 or tansho_roi > 130:
                print(f"❌ 単勝ROIが現実的でない: {tansho_roi}%")
                return False
            
            if fukusho_roi < 30 or fukusho_roi > 130:
                print(f"❌ 複勝ROIが現実的でない: {fukusho_roi}%")
                return False
            
            print("✅ ROIが現実的なレンジ内")
            return True
            
        except Exception as e:
            print(f"現実チェックエラー: {e}")
            return False
    
    def run_unit_fix(self):
        """単位変換修正実行"""
        print("=== 単位変換修正実行 ===")
        
        # 1) 円統一列作成
        if not self.create_pay_yen_columns():
            return False
        
        # 2) 修正KPI計算
        kpi_results = self.calculate_corrected_kpi()
        if kpi_results is None:
            return False
        
        # 3) 現実チェック
        if not self.check_plausible_range(kpi_results):
            return False
        
        print("✅ 単位変換修正完了")
        return True

def main():
    fixer = UnitConversionFix()
    success = fixer.run_unit_fix()
    
    if success:
        print("\n✅ 単位変換修正成功")
    else:
        print("\n❌ 単位変換修正失敗")

if __name__ == "__main__":
    main()




