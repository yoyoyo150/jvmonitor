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

class FixWinPayYenUltimateFinal:
    """win_pay_yen究極最終修正"""
    
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
    
    def fix_win_pay_yen_ultimate_final(self):
        """win_pay_yen究極最終修正（倍率×100円）"""
        print("=== win_pay_yen究極最終修正 ===")
        
        try:
            cursor = self.conn.cursor()
            
            # ZI_Indexを倍率として扱い、×100円で変換
            cursor.execute("""
            UPDATE SE_FE
            SET win_pay_yen = CASE
                WHEN ZI_Index IS NULL OR ZI_Index = '' OR ZI_Index = '0' OR ZI_Index = 0 THEN NULL
                ELSE CAST(ROUND(CAST(ZI_Index AS REAL) * 100) AS INTEGER)
            END
            """)
            
            self.conn.commit()
            print("win_pay_yen究極最終修正完了（倍率×100円）")
            
            return True
            
        except Exception as e:
            print(f"win_pay_yen究極最終修正エラー: {e}")
            return False
    
    def verify_ultimate_final_fix(self):
        """究極最終修正の検証"""
        print("=== 究極最終修正の検証 ===")
        
        try:
            # 修正後の統計
            query_stats = """
            SELECT 
                COUNT(*) as total_count,
                AVG(win_pay_yen) as avg_value,
                MIN(win_pay_yen) as min_value,
                MAX(win_pay_yen) as max_value,
                COUNT(CASE WHEN win_pay_yen > 1000 THEN 1 END) as over_1000_count,
                COUNT(CASE WHEN win_pay_yen > 10000 THEN 1 END) as over_10000_count
            FROM SE_FE
            WHERE win_pay_yen IS NOT NULL
            """
            result_stats = pd.read_sql_query(query_stats, self.conn)
            
            print("究極最終修正後win_pay_yen統計:")
            print(f"  総件数: {result_stats.iloc[0]['total_count']}")
            print(f"  平均値: {result_stats.iloc[0]['avg_value']:.2f}")
            print(f"  最小値: {result_stats.iloc[0]['min_value']:.2f}")
            print(f"  最大値: {result_stats.iloc[0]['max_value']:.2f}")
            print(f"  1,000円超: {result_stats.iloc[0]['over_1000_count']}")
            print(f"  10,000円超: {result_stats.iloc[0]['over_10000_count']}")
            
            # サンプルデータ
            query_sample = """
            SELECT 
                SourceDate, HorseNameS, Chaku, win_pay_yen, ZI_Index
            FROM SE_FE
            WHERE win_pay_yen IS NOT NULL
            ORDER BY win_pay_yen DESC
            LIMIT 10
            """
            result_sample = pd.read_sql_query(query_sample, self.conn)
            
            print("\n究極最終修正後サンプル（上位10件）:")
            print(result_sample.to_string(index=False))
            
            return result_stats, result_sample
            
        except Exception as e:
            print(f"究極最終修正検証エラー: {e}")
            return None, None
    
    def test_roi_calculation_ultimate_final(self, test_date="2024-11-02"):
        """ROI計算テスト（究極最終版）"""
        print(f"=== ROI計算テスト（究極最終版）（{test_date}） ===")
        
        try:
            query = f"""
            SELECT
              'tansho' AS bet, COUNT(*) bets, COUNT(*)*100 stake,
              SUM(CASE WHEN CAST(Chaku AS INTEGER)=1 AND win_pay_yen IS NOT NULL THEN win_pay_yen ELSE 0 END) payoff,
              ROUND(100.0*SUM(CASE WHEN CAST(Chaku AS INTEGER)=1 AND win_pay_yen IS NOT NULL THEN win_pay_yen ELSE 0 END)/NULLIF(COUNT(*)*100.0,0),2) roi_pct
            FROM SE_FE
            WHERE SourceDate = '{test_date.replace('-', '')}'
            AND win_pay_yen IS NOT NULL
            UNION ALL
            SELECT
              'fukusho', COUNT(*), COUNT(*)*100,
              SUM(CASE WHEN CAST(Chaku AS INTEGER) BETWEEN 1 AND 3 AND plc_pay_yen_low IS NOT NULL THEN plc_pay_yen_low ELSE 0 END),
              ROUND(100.0*SUM(CASE WHEN CAST(Chaku AS INTEGER) BETWEEN 1 AND 3 AND plc_pay_yen_low IS NOT NULL THEN plc_pay_yen_low ELSE 0 END)/NULLIF(COUNT(*)*100.0,0),2)
            FROM SE_FE
            WHERE SourceDate = '{test_date.replace('-', '')}'
            AND plc_pay_yen_low IS NOT NULL
            """
            result = pd.read_sql_query(query, self.conn)
            
            print("ROI計算テスト結果（究極最終版）:")
            print(result.to_string(index=False))
            
            # 常識圏チェック
            tansho_roi = result[result['bet'] == 'tansho']['roi_pct'].iloc[0]
            fukusho_roi = result[result['bet'] == 'fukusho']['roi_pct'].iloc[0]
            
            print(f"\n常識圏チェック:")
            print(f"  単勝ROI: {tansho_roi}% (目安: 70-95%)")
            print(f"  複勝ROI: {fukusho_roi}% (目安: 80-100%)")
            
            if 70 <= tansho_roi <= 95 and 80 <= fukusho_roi <= 100:
                print("✅ 現実レンジ内")
                return True
            else:
                print("❌ 現実レンジ外")
                return False
            
        except Exception as e:
            print(f"ROI計算テスト（究極最終版）エラー: {e}")
            return False
    
    def run_ultimate_final_fix(self):
        """究極最終修正実行"""
        print("=== win_pay_yen究極最終修正実行 ===")
        
        try:
            # 1) 究極最終修正実行
            if not self.fix_win_pay_yen_ultimate_final():
                return False
            
            # 2) 究極最終修正検証
            stats, sample = self.verify_ultimate_final_fix()
            if stats is None:
                return False
            
            # 3) ROI計算テスト（究極最終版）
            if not self.test_roi_calculation_ultimate_final():
                return False
            
            print("✅ win_pay_yen究極最終修正完了")
            return True
            
        except Exception as e:
            print(f"win_pay_yen究極最終修正実行エラー: {e}")
            return False

def main():
    fixer = FixWinPayYenUltimateFinal()
    success = fixer.run_ultimate_final_fix()
    
    if success:
        print("\n✅ win_pay_yen究極最終修正成功")
    else:
        print("\n❌ win_pay_yen究極最終修正失敗")

if __name__ == "__main__":
    main()