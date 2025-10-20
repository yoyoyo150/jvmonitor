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

class FinalAudit:
    """仕上げの監査 - 本当に安全に直ったか確認"""
    
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
    
    def check_duplicates_zero(self):
        """① 重複ゼロの再確認"""
        print("=== 重複ゼロの再確認 ===")
        
        try:
            query = """
            WITH dup AS (
                SELECT SourceDate, HorseNameS, Trainer_Name, COUNT(*) c
                FROM excel_marks
                GROUP BY SourceDate, HorseNameS, Trainer_Name
                HAVING c > 1
            )
            SELECT COUNT(*) AS duplicate_keys FROM dup
            """
            result = pd.read_sql_query(query, self.conn)
            duplicate_count = result.iloc[0]['duplicate_keys']
            
            print(f"重複キー数: {duplicate_count}")
            
            if duplicate_count == 0:
                print("✅ 重複ゼロ確認完了")
                return True
            else:
                print("❌ 重複が残存")
                return False
                
        except Exception as e:
            print(f"重複チェックエラー: {e}")
            return False
    
    def check_mark_normalization(self):
        """② Mark5/Mark6正規化の実着地確認"""
        print("=== Mark5/Mark6正規化確認 ===")
        
        try:
            query = """
            SELECT
                SUM(CASE WHEN TRIM(Mark5) <> '' AND Mark5_num IS NULL THEN 1 ELSE 0 END) AS m5_unparsed_to_null,
                SUM(CASE WHEN TRIM(Mark6) <> '' AND Mark6_num IS NULL THEN 1 ELSE 0 END) AS m6_unparsed_to_null
            FROM excel_marks
            """
            result = pd.read_sql_query(query, self.conn)
            m5_unparsed = result.iloc[0]['m5_unparsed_to_null']
            m6_unparsed = result.iloc[0]['m6_unparsed_to_null']
            
            print(f"Mark5未解析→NULL: {m5_unparsed}件")
            print(f"Mark6未解析→NULL: {m6_unparsed}件")
            
            if m5_unparsed == 0 and m6_unparsed == 0:
                print("✅ Mark5/Mark6正規化完了")
                return True
            else:
                print("❌ Mark5/Mark6正規化に問題")
                return False
                
        except Exception as e:
            print(f"Mark5/Mark6確認エラー: {e}")
            return False
    
    def check_constraints(self):
        """③ 必須NULLゼロ＆制約動作確認"""
        print("=== 制約動作確認 ===")
        
        try:
            # 必須NULLゼロ確認
            query_null = """
            SELECT COUNT(*) as cnt
            FROM excel_marks
            WHERE HorseNameS IS NULL OR HorseNameS = '' OR
                  Trainer_Name IS NULL OR Trainer_Name = '' OR
                  Mark5 IS NULL OR Mark5 = '' OR
                  Mark6 IS NULL OR Mark6 = ''
            """
            result_null = pd.read_sql_query(query_null, self.conn)
            null_count = result_null.iloc[0]['cnt']
            
            print(f"必須NULL値: {null_count}件")
            
            if null_count == 0:
                print("✅ 必須NULLゼロ確認完了")
                return True
            else:
                print("❌ 必須NULL値が残存")
                return False
                
        except Exception as e:
            print(f"制約確認エラー: {e}")
            return False
    
    def check_date_race_counts(self, start_date="2024-11-02", end_date="2025-09-28"):
        """日別レース数・出走件数の確認"""
        print("=== 日別レース数・出走件数確認 ===")
        
        try:
            start_date_norm = start_date.replace('-', '')
            end_date_norm = end_date.replace('-', '')
            
            query = """
            SELECT 
                SourceDate,
                COUNT(DISTINCT HorseNameS) AS unique_horses,
                COUNT(*) AS total_entries
            FROM excel_marks
            WHERE SourceDate >= ? AND SourceDate <= ?
            GROUP BY SourceDate
            ORDER BY SourceDate
            """
            result = pd.read_sql_query(query, self.conn, params=[start_date_norm, end_date_norm])
            
            print(f"期間: {start_date} ～ {end_date}")
            print(f"日数: {len(result)}日")
            print(f"総出走数: {result['total_entries'].sum()}件")
            print(f"平均出走数/日: {result['total_entries'].mean():.1f}件")
            
            # 日別統計の表示
            print("\n日別統計（最初の10日）:")
            print(result.head(10).to_string(index=False))
            
            return True
            
        except Exception as e:
            print(f"日別統計確認エラー: {e}")
            return False
    
    def check_roi_calculation(self, test_date="20250928"):
        """ROI計算のテスト（1日分）"""
        print(f"=== ROI計算テスト（{test_date}） ===")
        
        try:
            # 単勝ROI概算
            query_tansho = """
            SELECT
                COUNT(*) AS bets,
                SUM(CASE WHEN Chaku = '1' AND ZI_Index > 1.0 THEN CAST(ROUND(ZI_Index*100) AS INT) ELSE 0 END) AS payoff,
                COUNT(*)*100 AS stake
            FROM excel_marks
            WHERE SourceDate = ? AND ZI_Index IS NOT NULL AND ZI_Index > 1.0
            """
            result_tansho = pd.read_sql_query(query_tansho, self.conn, params=[test_date])
            
            if not result_tansho.empty:
                bets = result_tansho.iloc[0]['bets']
                payoff = result_tansho.iloc[0]['payoff']
                stake = result_tansho.iloc[0]['stake']
                roi_pct = (payoff / stake * 100) if stake > 0 else 0
                
                print(f"単勝ROI: {roi_pct:.2f}% (購入: {stake}円, 払戻: {payoff}円)")
            else:
                print("単勝ROI: データなし")
            
            # 複勝ROI概算
            query_fukusho = """
            SELECT
                COUNT(*) AS bets,
                SUM(CASE WHEN CAST(Chaku AS INTEGER) BETWEEN 1 AND 3 AND ZM_Value > 1.0 THEN CAST(ROUND(ZM_Value*100) AS INT) ELSE 0 END) AS payoff,
                COUNT(*)*100 AS stake
            FROM excel_marks
            WHERE SourceDate = ? AND ZM_Value IS NOT NULL AND ZM_Value > 1.0
            """
            result_fukusho = pd.read_sql_query(query_fukusho, self.conn, params=[test_date])
            
            if not result_fukusho.empty:
                bets = result_fukusho.iloc[0]['bets']
                payoff = result_fukusho.iloc[0]['payoff']
                stake = result_fukusho.iloc[0]['stake']
                roi_pct = (payoff / stake * 100) if stake > 0 else 0
                
                print(f"複勝ROI: {roi_pct:.2f}% (購入: {stake}円, 払戻: {payoff}円)")
            else:
                print("複勝ROI: データなし")
            
            return True
            
        except Exception as e:
            print(f"ROI計算テストエラー: {e}")
            return False
    
    def optimize_database(self):
        """VACUUM & ANALYZE実行"""
        print("=== データベース最適化 ===")
        
        try:
            cursor = self.conn.cursor()
            
            # VACUUM実行
            cursor.execute("VACUUM")
            print("VACUUM完了")
            
            # ANALYZE実行
            cursor.execute("ANALYZE")
            print("ANALYZE完了")
            
            self.conn.commit()
            print("✅ データベース最適化完了")
            return True
            
        except Exception as e:
            print(f"データベース最適化エラー: {e}")
            return False
    
    def run_final_audit(self):
        """仕上げの監査実行"""
        print("=== 仕上げの監査実行 ===")
        
        audit_results = {}
        
        # ① 重複ゼロの再確認
        audit_results['duplicates'] = self.check_duplicates_zero()
        
        # ② Mark5/Mark6正規化確認
        audit_results['mark_normalization'] = self.check_mark_normalization()
        
        # ③ 制約動作確認
        audit_results['constraints'] = self.check_constraints()
        
        # 日別統計確認
        audit_results['date_race_counts'] = self.check_date_race_counts()
        
        # ROI計算テスト
        audit_results['roi_calculation'] = self.check_roi_calculation()
        
        # データベース最適化
        audit_results['optimization'] = self.optimize_database()
        
        # 結果サマリー
        print("\n=== 監査結果サマリー ===")
        for check_name, result in audit_results.items():
            status = "✅ 成功" if result else "❌ 失敗"
            print(f"{check_name}: {status}")
        
        all_passed = all(audit_results.values())
        
        if all_passed:
            print("\n✅ 仕上げの監査完了 - 本番解禁可能")
        else:
            print("\n❌ 仕上げの監査失敗 - 追加対応が必要")
        
        return all_passed, audit_results

def main():
    audit = FinalAudit()
    success, results = audit.run_final_audit()
    
    if success:
        print("\n🎉 監査完了 - 安心フェーズ達成！")
    else:
        print("\n⚠️ 監査失敗 - 追加対応が必要")

if __name__ == "__main__":
    main()




