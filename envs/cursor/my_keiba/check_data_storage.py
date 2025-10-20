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

class CheckDataStorage:
    """正確格納DBのチェック"""
    
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
    
    def check_basic_data_storage(self):
        """基本データ格納チェック"""
        print("=== 基本データ格納チェック ===")
        
        try:
            # 1) テーブル存在確認
            cursor = self.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            print(f"存在テーブル: {tables}")
            
            # 2) SE_FEテーブルの基本情報
            query_basic = """
            SELECT 
                COUNT(*) as total_records,
                COUNT(DISTINCT SourceDate) as unique_dates,
                COUNT(DISTINCT HorseNameS) as unique_horses,
                COUNT(DISTINCT Trainer_Name) as unique_trainers
            FROM SE_FE
            """
            result_basic = pd.read_sql_query(query_basic, self.conn)
            
            print("\nSE_FEテーブル基本情報:")
            print(f"  総レコード数: {result_basic.iloc[0]['total_records']}")
            print(f"  ユニーク日付数: {result_basic.iloc[0]['unique_dates']}")
            print(f"  ユニーク馬数: {result_basic.iloc[0]['unique_horses']}")
            print(f"  ユニーク調教師数: {result_basic.iloc[0]['unique_trainers']}")
            
            return result_basic
            
        except Exception as e:
            print(f"基本データ格納チェックエラー: {e}")
            return None
    
    def check_m5m6_data_quality(self):
        """M5/M6データ品質チェック"""
        print("=== M5/M6データ品質チェック ===")
        
        try:
            # M5/M6の分布
            query_m5m6 = """
            SELECT 
                COUNT(*) as total_records,
                COUNT(mark5_imp) as m5_filled,
                COUNT(mark6_imp) as m6_filled,
                COUNT(mark5_missing_flag) as m5_missing_flag_count,
                COUNT(mark6_missing_flag) as m6_missing_flag_count,
                AVG(mark5_imp) as m5_avg,
                AVG(mark6_imp) as m6_avg,
                MIN(mark5_imp) as m5_min,
                MAX(mark5_imp) as m5_max,
                MIN(mark6_imp) as m6_min,
                MAX(mark6_imp) as m6_max
            FROM SE_FE
            """
            result_m5m6 = pd.read_sql_query(query_m5m6, self.conn)
            
            print("M5/M6データ品質:")
            print(f"  総レコード数: {result_m5m6.iloc[0]['total_records']}")
            print(f"  M5埋まり数: {result_m5m6.iloc[0]['m5_filled']}")
            print(f"  M6埋まり数: {result_m5m6.iloc[0]['m6_filled']}")
            print(f"  M5欠損フラグ数: {result_m5m6.iloc[0]['m5_missing_flag_count']}")
            print(f"  M6欠損フラグ数: {result_m5m6.iloc[0]['m6_missing_flag_count']}")
            print(f"  M5平均: {result_m5m6.iloc[0]['m5_avg']:.2f}")
            print(f"  M6平均: {result_m5m6.iloc[0]['m6_avg']:.2f}")
            print(f"  M5範囲: {result_m5m6.iloc[0]['m5_min']:.2f} - {result_m5m6.iloc[0]['m5_max']:.2f}")
            print(f"  M6範囲: {result_m5m6.iloc[0]['m6_min']:.2f} - {result_m5m6.iloc[0]['m6_max']:.2f}")
            
            return result_m5m6
            
        except Exception as e:
            print(f"M5/M6データ品質チェックエラー: {e}")
            return None
    
    def check_roi_columns(self):
        """ROI計算用列チェック"""
        print("=== ROI計算用列チェック ===")
        
        try:
            # ROI計算用の3列の状況
            query_roi = """
            SELECT 
                COUNT(*) as total_records,
                COUNT(finish) as finish_count,
                COUNT(win_pay_yen) as win_pay_count,
                COUNT(plc_pay_yen_low) as plc_pay_count,
                COUNT(CASE WHEN finish = 1 THEN 1 END) as win_count,
                COUNT(CASE WHEN finish BETWEEN 1 AND 3 THEN 1 END) as place_count,
                AVG(win_pay_yen) as win_pay_avg,
                AVG(plc_pay_yen_low) as plc_pay_avg
            FROM SE_FE
            """
            result_roi = pd.read_sql_query(query_roi, self.conn)
            
            print("ROI計算用列状況:")
            print(f"  総レコード数: {result_roi.iloc[0]['total_records']}")
            print(f"  finish列数: {result_roi.iloc[0]['finish_count']}")
            print(f"  win_pay_yen列数: {result_roi.iloc[0]['win_pay_count']}")
            print(f"  plc_pay_yen_low列数: {result_roi.iloc[0]['plc_pay_count']}")
            print(f"  1着数: {result_roi.iloc[0]['win_count']}")
            print(f"  1-3着数: {result_roi.iloc[0]['place_count']}")
            print(f"  win_pay_yen平均: {result_roi.iloc[0]['win_pay_avg']:.2f}")
            print(f"  plc_pay_yen_low平均: {result_roi.iloc[0]['plc_pay_avg']:.2f}")
            
            return result_roi
            
        except Exception as e:
            print(f"ROI計算用列チェックエラー: {e}")
            return None
    
    def show_sample_data(self):
        """サンプルデータ表示"""
        print("=== サンプルデータ表示 ===")
        
        try:
            # サンプルデータ（10行）
            query_sample = """
            SELECT 
                SourceDate,
                HorseNameS,
                Trainer_Name,
                Chaku,
                mark5_imp,
                mark6_imp,
                win_pay_yen,
                plc_pay_yen_low
            FROM SE_FE
            ORDER BY SourceDate DESC
            LIMIT 10
            """
            result_sample = pd.read_sql_query(query_sample, self.conn)
            
            print("サンプルデータ（10行）:")
            print(result_sample.to_string(index=False))
            
            return result_sample
            
        except Exception as e:
            print(f"サンプルデータ表示エラー: {e}")
            return None
    
    def run_data_storage_check(self):
        """データ格納チェック実行"""
        print("=== データ格納チェック実行 ===")
        
        try:
            # 1) 基本データ格納チェック
            basic_result = self.check_basic_data_storage()
            if basic_result is None:
                return False
            
            # 2) M5/M6データ品質チェック
            m5m6_result = self.check_m5m6_data_quality()
            if m5m6_result is None:
                return False
            
            # 3) ROI計算用列チェック
            roi_result = self.check_roi_columns()
            if roi_result is None:
                return False
            
            # 4) サンプルデータ表示
            sample_result = self.show_sample_data()
            if sample_result is None:
                return False
            
            print("✅ データ格納チェック完了")
            return True
            
        except Exception as e:
            print(f"データ格納チェック実行エラー: {e}")
            return False

def main():
    checker = CheckDataStorage()
    success = checker.run_data_storage_check()
    
    if success:
        print("\n✅ データ格納チェック成功")
    else:
        print("\n❌ データ格納チェック失敗")

if __name__ == "__main__":
    main()




