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

class ROICalculationEcore:
    """ecore.dbを使用した正しいROI計算"""
    
    def __init__(self, db_path="ecore.db"):
        self.db_path = db_path
        self.conn = None
        self.connect()
    
    def connect(self):
        """データベース接続"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            print("ecore.db接続成功")
        except Exception as e:
            print(f"ecore.db接続エラー: {e}")
            return False
        return True
    
    def calculate_roi_from_ecore(self, start_date="2024-11-02", end_date="2025-09-28"):
        """ecore.dbから正しいROI計算"""
        print("=== ecore.dbから正しいROI計算 ===")
        
        try:
            start_date_norm = start_date.replace('-', '')
            end_date_norm = end_date.replace('-', '')
            
            # 単勝ROI計算（1着の本賞金を使用）
            query = f"""
            SELECT
                'tansho' AS bettype,
                COUNT(*) AS bets,
                COUNT(*) * 100 AS stake_yen,
                SUM(CASE 
                    WHEN CAST(KakuteiJyuni AS INTEGER) = 1 AND Honsyokin IS NOT NULL AND Honsyokin != '00000000'
                    THEN CAST(Honsyokin AS INTEGER) 
                    ELSE 0 
                END) AS payoff_yen,
                ROUND(100.0 * SUM(CASE 
                    WHEN CAST(KakuteiJyuni AS INTEGER) = 1 AND Honsyokin IS NOT NULL AND Honsyokin != '00000000'
                    THEN CAST(Honsyokin AS INTEGER) 
                    ELSE 0 
                END) / NULLIF(COUNT(*) * 100.0, 0), 2) AS roi_pct
            FROM N_UMA_RACE
            WHERE Year || MonthDay >= '{start_date_norm[:8]}' AND Year || MonthDay <= '{end_date_norm[:8]}'
            AND Honsyokin IS NOT NULL AND Honsyokin != '00000000'
            """
            result_tansho = pd.read_sql_query(query, self.conn)
            
            # 複勝ROI計算（1-3着の複勝賞金を使用）
            query_fukusho = f"""
            SELECT
                'fukusho' AS bettype,
                COUNT(*) AS bets,
                COUNT(*) * 100 AS stake_yen,
                SUM(CASE 
                    WHEN CAST(KakuteiJyuni AS INTEGER) BETWEEN 1 AND 3 AND Fukasyokin IS NOT NULL AND Fukasyokin != '00000000'
                    THEN CAST(Fukasyokin AS INTEGER) 
                    ELSE 0 
                END) AS payoff_yen,
                ROUND(100.0 * SUM(CASE 
                    WHEN CAST(KakuteiJyuni AS INTEGER) BETWEEN 1 AND 3 AND Fukasyokin IS NOT NULL AND Fukasyokin != '00000000'
                    THEN CAST(Fukasyokin AS INTEGER) 
                    ELSE 0 
                END) / NULLIF(COUNT(*) * 100.0, 0), 2) AS roi_pct
            FROM N_UMA_RACE
            WHERE Year || MonthDay >= '{start_date_norm[:8]}' AND Year || MonthDay <= '{end_date_norm[:8]}'
            AND Fukasyokin IS NOT NULL AND Fukasyokin != '00000000'
            """
            result_fukusho = pd.read_sql_query(query_fukusho, self.conn)
            
            # 結果を結合
            kpi_results = pd.concat([result_tansho, result_fukusho], ignore_index=True)
            
            print("ecore.dbから正しいROI計算結果:")
            print(kpi_results.to_string(index=False))
            
            return kpi_results
            
        except Exception as e:
            print(f"ecore.dbから正しいROI計算エラー: {e}")
            return None
    
    def check_sanity_range(self, kpi_results):
        """サニティレンジチェック"""
        print("=== サニティレンジチェック ===")
        
        try:
            if kpi_results is None or kpi_results.empty:
                print("KPI結果が空です")
                return False
            
            # 単勝・複勝のROIを取得
            tansho_roi = kpi_results[kpi_results['bettype'] == 'tansho']['roi_pct'].iloc[0]
            fukusho_roi = kpi_results[kpi_results['bettype'] == 'fukusho']['roi_pct'].iloc[0]
            
            print(f"単勝ROI: {tansho_roi}%")
            print(f"複勝ROI: {fukusho_roi}%")
            
            # サニティレンジチェック
            if tansho_roi < 30.0 or tansho_roi > 130.0:
                print(f"❌ 単勝ROIが異常範囲外: {tansho_roi}% (30-130%)")
                return False
            
            if fukusho_roi < 40.0 or fukusho_roi > 160.0:
                print(f"❌ 複勝ROIが異常範囲外: {fukusho_roi}% (40-160%)")
                return False
            
            print("✅ サニティレンジ内")
            return True
            
        except Exception as e:
            print(f"サニティレンジチェックエラー: {e}")
            return False
    
    def show_sample_data(self):
        """サンプルデータ表示"""
        print("=== サンプルデータ表示 ===")
        
        try:
            # 1着馬のサンプルデータ表示
            query = """
            SELECT 
                Year || MonthDay as race_date,
                JyoCD,
                RaceNum,
                KettoNum,
                Bamei,
                KakuteiJyuni,
                Odds,
                Honsyokin,
                Fukasyokin
            FROM N_UMA_RACE
            WHERE CAST(KakuteiJyuni AS INTEGER) = 1
            AND Honsyokin IS NOT NULL AND Honsyokin != '00000000'
            ORDER BY Year || MonthDay DESC
            LIMIT 10
            """
            result = pd.read_sql_query(query, self.conn)
            
            print("1着馬のサンプルデータ（10件）:")
            print(result.to_string(index=False))
            
            return result
            
        except Exception as e:
            print(f"サンプルデータ表示エラー: {e}")
            return None
    
    def run_roi_calculation_ecore(self, start_date="2024-11-02", end_date="2025-09-28"):
        """ecore.dbから正しいROI計算実行"""
        print("=== ecore.dbから正しいROI計算実行 ===")
        
        try:
            # 1) ecore.dbから正しいROI計算
            kpi_results = self.calculate_roi_from_ecore(start_date, end_date)
            if kpi_results is None:
                return False
            
            # 2) サニティレンジチェック
            if not self.check_sanity_range(kpi_results):
                print("❌ サニティレンジ外のため停止")
                return False
            
            # 3) サンプルデータ表示
            self.show_sample_data()
            
            print("✅ ecore.dbから正しいROI計算完了")
            return True
            
        except Exception as e:
            print(f"ecore.dbから正しいROI計算実行エラー: {e}")
            return False

def main():
    calculator = ROICalculationEcore()
    success = calculator.run_roi_calculation_ecore()
    
    if success:
        print("\n✅ ecore.dbから正しいROI計算成功")
    else:
        print("\n❌ ecore.dbから正しいROI計算失敗")

if __name__ == "__main__":
    main()




