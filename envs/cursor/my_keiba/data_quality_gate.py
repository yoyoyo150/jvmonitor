import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
import sys

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

class DataQualityGate:
    """データ完全性ゲート - データ不足で分析停止"""
    
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
    
    def check_data_completeness(self, start_date="2024-11-02", end_date="2025-09-28"):
        """データ完全性チェック"""
        print("=== データ完全性チェック開始 ===")
        
        # 日付の正規化
        start_date_norm = start_date.replace('-', '')
        end_date_norm = end_date.replace('-', '')
        
        errors = []
        
        # 1. 期間内データの存在確認
        query1 = """
        SELECT COUNT(*) as cnt
        FROM excel_marks
        WHERE SourceDate >= ? AND SourceDate <= ?
        """
        result1 = pd.read_sql_query(query1, self.conn, params=[start_date_norm, end_date_norm])
        if result1.iloc[0]['cnt'] == 0:
            errors.append("期間内データが存在しません")
        
        # 2. 必須カラムのNULL確認
        query2 = """
        SELECT COUNT(*) as cnt
        FROM excel_marks
        WHERE SourceDate >= ? AND SourceDate <= ?
        AND (HorseNameS IS NULL OR HorseNameS = '' OR
             Trainer_Name IS NULL OR Trainer_Name = '' OR
             Mark5 IS NULL OR Mark5 = '' OR
             Mark6 IS NULL OR Mark6 = '')
        """
        result2 = pd.read_sql_query(query2, self.conn, params=[start_date_norm, end_date_norm])
        if result2.iloc[0]['cnt'] > 0:
            errors.append(f"必須カラムにNULL値: {result2.iloc[0]['cnt']}件")
        
        # 3. Mark5/Mark6の数値変換確認
        query3 = """
        SELECT COUNT(*) as cnt
        FROM excel_marks
        WHERE SourceDate >= ? AND SourceDate <= ?
        AND (Mark5 = '?' OR Mark6 = '?' OR
             Mark5 NOT GLOB '[0-9]*' OR Mark6 NOT GLOB '[0-9]*')
        """
        result3 = pd.read_sql_query(query3, self.conn, params=[start_date_norm, end_date_norm])
        if result3.iloc[0]['cnt'] > 0:
            errors.append(f"Mark5/Mark6の数値変換エラー: {result3.iloc[0]['cnt']}件")
        
        # 4. 重複データの確認
        query4 = """
        SELECT SourceDate, HorseNameS, Trainer_Name, COUNT(*) as cnt
        FROM excel_marks
        WHERE SourceDate >= ? AND SourceDate <= ?
        GROUP BY SourceDate, HorseNameS, Trainer_Name
        HAVING COUNT(*) > 1
        """
        result4 = pd.read_sql_query(query4, self.conn, params=[start_date_norm, end_date_norm])
        if len(result4) > 0:
            errors.append(f"重複データ: {len(result4)}件")
        
        # 5. 期間内の日付分布確認
        query5 = """
        SELECT SourceDate, COUNT(*) as cnt
        FROM excel_marks
        WHERE SourceDate >= ? AND SourceDate <= ?
        GROUP BY SourceDate
        ORDER BY SourceDate
        """
        result5 = pd.read_sql_query(query5, self.conn, params=[start_date_norm, end_date_norm])
        if len(result5) == 0:
            errors.append("期間内にデータが存在しません")
        
        # エラーがある場合は停止
        if errors:
            error_msg = "データ完全性チェック失敗:\n" + "\n".join([f"- {error}" for error in errors])
            print(error_msg)
            return False, errors
        
        print("データ完全性チェック成功")
        return True, []
    
    def check_data_quality(self, start_date="2024-11-02", end_date="2025-09-28"):
        """データ品質チェック"""
        print("=== データ品質チェック開始 ===")
        
        # 日付の正規化
        start_date_norm = start_date.replace('-', '')
        end_date_norm = end_date.replace('-', '')
        
        # データ取得
        query = """
        SELECT 
            SourceDate,
            HorseNameS,
            Trainer_Name,
            Mark5,
            Mark6,
            Chaku,
            ZI_Index,
            ZM_Value
        FROM excel_marks
        WHERE SourceDate >= ? AND SourceDate <= ?
        AND Mark5 IS NOT NULL 
        AND Mark6 IS NOT NULL
        AND Mark5 != '?'
        AND Mark6 != '?'
        AND Trainer_Name IS NOT NULL
        AND Trainer_Name != ''
        """
        
        df = pd.read_sql_query(query, self.conn, params=[start_date_norm, end_date_norm])
        
        if df.empty:
            print("データ品質チェック失敗: データが空です")
            return False, None
        
        # Mark5, Mark6を数値に変換
        df['Mark5_numeric'] = pd.to_numeric(df['Mark5'], errors='coerce')
        df['Mark6_numeric'] = pd.to_numeric(df['Mark6'], errors='coerce')
        
        # Mark5+Mark6の合計を計算
        df['Mark5_Mark6_sum'] = df['Mark5_numeric'] + df['Mark6_numeric']
        
        # 条件適用（2以上6以下）
        df_filtered = df[
            (df['Mark5_Mark6_sum'] >= 2) & 
            (df['Mark5_Mark6_sum'] <= 6)
        ]
        
        if df_filtered.empty:
            print("データ品質チェック失敗: 条件適用後データが空です")
            return False, None
        
        print(f"データ品質チェック成功: {len(df_filtered)}件")
        return True, df_filtered
    
    def validate_period(self, start_date="2024-11-02", end_date="2025-09-28"):
        """期間の正規化チェック"""
        print("=== 期間正規化チェック開始 ===")
        
        # 日付の正規化
        start_date_norm = start_date.replace('-', '')
        end_date_norm = end_date.replace('-', '')
        
        # 期間内の日付分布確認
        query = """
        SELECT SourceDate, COUNT(*) as cnt
        FROM excel_marks
        WHERE SourceDate >= ? AND SourceDate <= ?
        GROUP BY SourceDate
        ORDER BY SourceDate
        """
        
        result = pd.read_sql_query(query, self.conn, params=[start_date_norm, end_date_norm])
        
        if result.empty:
            print("期間正規化チェック失敗: 期間内にデータが存在しません")
            return False, None
        
        # 日付の範囲確認
        min_date = result['SourceDate'].min()
        max_date = result['SourceDate'].max()
        
        print(f"期間: {min_date} ～ {max_date}")
        print(f"日数: {len(result)}日")
        print(f"総データ数: {result['cnt'].sum()}件")
        
        return True, result
    
    def run_quality_checks(self, start_date="2024-11-02", end_date="2025-09-28"):
        """品質チェック実行"""
        print("=== データ品質ゲート実行 ===")
        
        # 1. データ完全性チェック
        completeness_ok, completeness_errors = self.check_data_completeness(start_date, end_date)
        if not completeness_ok:
            print("❌ データ完全性チェック失敗 - 分析を停止します")
            return False, None, None
        
        # 2. データ品質チェック
        quality_ok, quality_data = self.check_data_quality(start_date, end_date)
        if not quality_ok:
            print("❌ データ品質チェック失敗 - 分析を停止します")
            return False, None, None
        
        # 3. 期間正規化チェック
        period_ok, period_data = self.validate_period(start_date, end_date)
        if not period_ok:
            print("❌ 期間正規化チェック失敗 - 分析を停止します")
            return False, None, None
        
        print("✅ すべての品質チェック成功 - 分析を実行します")
        return True, quality_data, period_data

def main():
    gate = DataQualityGate()
    success, quality_data, period_data = gate.run_quality_checks()
    
    if success:
        print("\n✅ データ品質ゲート成功")
        print(f"品質データ: {len(quality_data)}件")
        print(f"期間データ: {len(period_data)}日")
    else:
        print("\n❌ データ品質ゲート失敗")

if __name__ == "__main__":
    main()




