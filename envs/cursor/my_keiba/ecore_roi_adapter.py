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

class EcoreROIAdapter:
    """ecore.db専用ROIアダプタ"""
    
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
    
    def create_minimal_schema(self):
        """最小スキーマ（3列）を追加"""
        print("=== 最小スキーマ（3列）を追加 ===")
        
        try:
            cursor = self.conn.cursor()
            
            # A) ROIに必要な列を追加（既存ならスキップでOK）
            cursor.execute("""
            ALTER TABLE N_UMA_RACE ADD COLUMN finish INTEGER
            """)
            print("finish列追加完了")
            
            cursor.execute("""
            ALTER TABLE N_UMA_RACE ADD COLUMN win_pay_yen_calc INTEGER
            """)
            print("win_pay_yen_calc列追加完了")
            
            cursor.execute("""
            ALTER TABLE N_UMA_RACE ADD COLUMN plc_pay_yen_low_calc INTEGER
            """)
            print("plc_pay_yen_low_calc列追加完了")
            
            # B) 成績から finish を埋める（KakuteiJyuni をそのまま使う）
            cursor.execute("""
            UPDATE N_UMA_RACE
            SET finish = CAST(KakuteiJyuni AS INTEGER)
            WHERE finish IS NULL AND KakuteiJyuni IS NOT NULL
            """)
            print("finish列更新完了")
            
            # C) 最終入力ビュー（ROIはこのビュー"だけ"参照）
            cursor.execute("""
            DROP VIEW IF EXISTS V_ROI_INPUT
            """)
            
            cursor.execute("""
            CREATE VIEW V_ROI_INPUT AS
            SELECT
              Year || MonthDay as race_id,
              KettoNum as horse_id,
              finish,
              win_pay_yen_calc AS win_pay_yen,
              plc_pay_yen_low_calc AS plc_pay_yen_low
            FROM N_UMA_RACE
            """)
            print("V_ROI_INPUTビュー作成完了")
            
            self.conn.commit()
            print("最小スキーマ追加完了")
            
            return True
            
        except Exception as e:
            print(f"最小スキーマ追加エラー: {e}")
            return False
    
    def normalize_win_pay_yen(self):
        """単勝：Odds → 払戻(円) に正規化（勝者だけ）"""
        print("=== 単勝：Odds → 払戻(円) に正規化 ===")
        
        try:
            cursor = self.conn.cursor()
            
            # 単位判定（"円っぽさ"の割合を測る）
            cursor.execute("""
            WITH stats AS (
              SELECT
                AVG(CASE WHEN CAST(Odds AS REAL) >= 150 AND CAST(Odds AS REAL) = CAST(CAST(Odds AS REAL) AS INTEGER) THEN 1.0 ELSE 0.0 END) AS p_yen_like
              FROM N_UMA_RACE
              WHERE Odds IS NOT NULL AND Odds != '0000'
            ),
            flag AS (
              SELECT CASE WHEN p_yen_like >= 0.7 THEN 1 ELSE 0 END AS is_yen FROM stats
            )
            UPDATE N_UMA_RACE
            SET win_pay_yen_calc = CASE
              WHEN finish = 1 THEN
                CASE WHEN (SELECT is_yen FROM flag)=1
                     THEN CAST(Odds AS INTEGER)                 -- 既に円
                     ELSE CAST(ROUND(CAST(Odds AS REAL) * 100) AS INTEGER)    -- 倍率→円
                END
              ELSE 0
            END
            """)
            
            self.conn.commit()
            print("単勝払戻正規化完了")
            
            return True
            
        except Exception as e:
            print(f"単勝払戻正規化エラー: {e}")
            return False
    
    def sanity_check(self):
        """サニティチェック（壊れていないか一撃判定）"""
        print("=== サニティチェック ===")
        
        try:
            # ① 負け馬に単勝払戻が入っていないか（0でなければNG）
            query1 = """
            SELECT COUNT(*) AS losers_with_winpay
            FROM N_UMA_RACE
            WHERE finish <> 1 AND win_pay_yen_calc > 0
            """
            result1 = pd.read_sql_query(query1, self.conn)
            losers_with_winpay = result1.iloc[0]['losers_with_winpay']
            
            print(f"負け馬に単勝払戻が入っている件数: {losers_with_winpay}")
            
            # ② 勝者の払戻が整数の"円"か＆レンジが妥当か
            query2 = """
            SELECT
              SUM(CASE WHEN finish=1 AND win_pay_yen_calc <> CAST(win_pay_yen_calc AS INTEGER) THEN 1 ELSE 0 END) AS non_integer_winner_rows,
              MIN(CASE WHEN finish=1 THEN win_pay_yen_calc END) AS min_winner_pay,
              MAX(CASE WHEN finish=1 THEN win_pay_yen_calc END) AS max_winner_pay
            FROM N_UMA_RACE
            """
            result2 = pd.read_sql_query(query2, self.conn)
            
            non_integer_winner_rows = result2.iloc[0]['non_integer_winner_rows']
            min_winner_pay = result2.iloc[0]['min_winner_pay']
            max_winner_pay = result2.iloc[0]['max_winner_pay']
            
            print(f"非整数勝者払戻件数: {non_integer_winner_rows}")
            print(f"最小勝者払戻: {min_winner_pay}円")
            print(f"最大勝者払戻: {max_winner_pay}円")
            
            # サニティチェック結果
            if losers_with_winpay == 0 and min_winner_pay >= 100 and max_winner_pay <= 1000000:
                print("✅ サニティチェック通過")
                return True
            else:
                print("❌ サニティチェック失敗")
                return False
            
        except Exception as e:
            print(f"サニティチェックエラー: {e}")
            return False
    
    def calculate_roi(self, start_date="2024-11-02", end_date="2025-09-28"):
        """KPI（黄金式：勝者だけ合算）"""
        print("=== KPI（黄金式：勝者だけ合算） ===")
        
        try:
            start_date_norm = start_date.replace('-', '')
            end_date_norm = end_date.replace('-', '')
            
            # 期間を1日だけで先にテスト
            query = f"""
            WITH scope AS (
              SELECT *
              FROM V_ROI_INPUT
              WHERE race_id >= '{start_date_norm[:8]}' AND race_id <= '{end_date_norm[:8]}'
            ),
            stake AS (SELECT COUNT(*)*100 AS stake_yen FROM scope),
            tansho_pay AS (
              SELECT SUM(CASE WHEN finish=1 THEN win_pay_yen ELSE 0 END) AS payoff_yen FROM scope
            ),
            fukusho_pay AS (
              SELECT SUM(CASE WHEN finish BETWEEN 1 AND 3 THEN plc_pay_yen_low ELSE 0 END) AS payoff_yen FROM scope
            )
            SELECT
              'tansho' AS bettype,
              (SELECT stake_yen FROM stake) AS stake_yen,
              (SELECT payoff_yen FROM tansho_pay) AS payoff_yen,
              ROUND(100.0 * (SELECT payoff_yen FROM tansho_pay) / NULLIF((SELECT stake_yen FROM stake)*1.0,0), 2) AS roi_pct
            UNION ALL
            SELECT
              'fukusho',
              (SELECT stake_yen FROM stake),
              (SELECT payoff_yen FROM fukusho_pay),
              ROUND(100.0 * (SELECT payoff_yen FROM fukusho_pay) / NULLIF((SELECT stake_yen FROM stake)*1.0,0), 2)
            """
            result = pd.read_sql_query(query, self.conn)
            
            print("KPI結果:")
            print(result.to_string(index=False))
            
            return result
            
        except Exception as e:
            print(f"KPI計算エラー: {e}")
            return None
    
    def show_sample_winners(self, sample_day="20241102"):
        """サンプル勝者データ表示"""
        print(f"=== サンプル勝者データ表示（{sample_day}） ===")
        
        try:
            query = f"""
            SELECT race_id, horse_id, finish, win_pay_yen_calc
            FROM N_UMA_RACE
            WHERE Year || MonthDay = '{sample_day}' AND finish = 1
            ORDER BY race_id, horse_id
            LIMIT 50
            """
            result = pd.read_sql_query(query, self.conn)
            
            print(f"サンプル勝者データ（{sample_day}）:")
            print(result.to_string(index=False))
            
            return result
            
        except Exception as e:
            print(f"サンプル勝者データ表示エラー: {e}")
            return None
    
    def run_ecore_roi_adapter(self, start_date="2024-11-02", end_date="2025-09-28"):
        """ecore.db専用ROIアダプタ実行"""
        print("=== ecore.db専用ROIアダプタ実行 ===")
        
        try:
            # 1) 最小スキーマ（3列）を追加
            if not self.create_minimal_schema():
                return False
            
            # 2) 単勝：Odds → 払戻(円) に正規化
            if not self.normalize_win_pay_yen():
                return False
            
            # 3) サニティチェック
            if not self.sanity_check():
                return False
            
            # 4) KPI計算
            roi_result = self.calculate_roi(start_date, end_date)
            if roi_result is None:
                return False
            
            # 5) サンプル勝者データ表示
            self.show_sample_winners()
            
            print("✅ ecore.db専用ROIアダプタ完了")
            return True
            
        except Exception as e:
            print(f"ecore.db専用ROIアダプタ実行エラー: {e}")
            return False

def main():
    adapter = EcoreROIAdapter()
    success = adapter.run_ecore_roi_adapter()
    
    if success:
        print("\n✅ ecore.db専用ROIアダプタ成功")
    else:
        print("\n❌ ecore.db専用ROIアダプタ失敗")

if __name__ == "__main__":
    main()




