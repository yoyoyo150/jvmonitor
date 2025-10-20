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

class MarkImputation:
    """Mark5/Mark6の補完システム - 推奨ポリシー実装"""
    
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
    
    def add_question_mark_aliases(self):
        """1) '？' を辞書で NULL に統一"""
        print("=== '？' を辞書で NULL に統一 ===")
        
        try:
            cursor = self.conn.cursor()
            
            # '？' を辞書に追加
            cursor.execute("""
            INSERT OR IGNORE INTO MARK_ALIASES (raw_text, value, note) VALUES
            ('？', NULL, 'unknown fullwidth question'),
            ('?',  NULL, 'unknown halfwidth question')
            """)
            
            self.conn.commit()
            print("'？' 辞書追加完了")
            
            # 正規化ビュー再作成
            cursor.execute("DROP VIEW IF EXISTS V_NORMALIZED_MARKS")
            
            # 正規化ビュー再作成
            cursor.execute("""
            CREATE VIEW V_NORMALIZED_MARKS AS
            WITH base AS (
                SELECT
                    rowid,
                    TRIM(Mark5) AS m5_raw,
                    TRIM(Mark6) AS m6_raw
                FROM excel_marks
            ),
            norm AS (
                SELECT
                    rowid,
                    TRIM(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(
                        REPLACE(REPLACE(m5_raw,'０','0'),'１','1'),'２','2'),'３','3'),'４','4'),
                        '５','5'),'６','6'),'７','7'),'８','8'),'９','9'),'．','.'),'　','')) AS m5_s,
                    TRIM(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(
                        REPLACE(REPLACE(m6_raw,'０','0'),'１','1'),'２','2'),'３','3'),'４','4'),
                        '５','5'),'６','6'),'７','7'),'８','8'),'９','9'),'．','.'),'　','')) AS m6_s
                FROM base
            ),
            dict_or_num AS (
                SELECT
                    n.rowid,
                    COALESCE( 
                        (SELECT value FROM MARK_ALIASES WHERE raw_text = n.m5_s),
                        CASE
                            WHEN n.m5_s GLOB '*-*' THEN CAST(SUBSTR(n.m5_s,1,INSTR(n.m5_s,'-')-1) AS REAL)
                            WHEN n.m5_s IN ('', '-', '—', 'N/A', 'NaN', '?','？') THEN NULL
                            WHEN n.m5_s LIKE '%倍' THEN CAST(REPLACE(n.m5_s,'倍','') AS REAL)
                            ELSE CAST(n.m5_s AS REAL)
                        END
                    ) AS m5_val,
                    COALESCE( 
                        (SELECT value FROM MARK_ALIASES WHERE raw_text = n.m6_s),
                        CASE
                            WHEN n.m6_s GLOB '*-*' THEN CAST(SUBSTR(n.m6_s,1,INSTR(n.m6_s,'-')-1) AS REAL)
                            WHEN n.m6_s IN ('', '-', '—', 'N/A', 'NaN', '?','？') THEN NULL
                            WHEN n.m6_s LIKE '%倍' THEN CAST(REPLACE(n.m6_s,'倍','') AS REAL)
                            ELSE CAST(n.m6_s AS REAL)
                        END
                    ) AS m6_val
                FROM norm n
            )
            SELECT * FROM dict_or_num
            """)
            
            # Mark5/Mark6値を更新
            cursor.execute("""
            UPDATE excel_marks
            SET Mark5_num = (SELECT m5_val FROM V_NORMALIZED_MARKS v WHERE v.rowid = excel_marks.rowid),
                Mark6_num = (SELECT m6_val FROM V_NORMALIZED_MARKS v WHERE v.rowid = excel_marks.rowid)
            """)
            
            self.conn.commit()
            print(f"Mark5/Mark6値更新完了: {cursor.rowcount}件")
            
            return True
            
        except Exception as e:
            print(f"'？' 辞書追加エラー: {e}")
            return False
    
    def create_derived_table(self):
        """3) 派生テーブル（分析用）を作る：補完＆フラグ付き"""
        print("=== 派生テーブル作成 ===")
        
        try:
            cursor = self.conn.cursor()
            
            # 既存テーブルを削除
            cursor.execute("DROP TABLE IF EXISTS SE_FE")
            
            # 派生テーブル作成（SourceDateをrace_idとして使用）
            cursor.execute("""
            CREATE TABLE SE_FE AS
            WITH med5 AS (
                SELECT SourceDate, AVG(mark5_num) AS med5
                FROM (
                    SELECT SourceDate, mark5_num,
                           ROW_NUMBER() OVER (PARTITION BY SourceDate ORDER BY mark5_num) AS rn,
                           COUNT(*)     OVER (PARTITION BY SourceDate)                     AS cnt
                    FROM excel_marks WHERE mark5_num IS NOT NULL
                )
                WHERE rn IN ( (cnt + 1)/2, (cnt + 2)/2 )
                GROUP BY SourceDate
            ),
            med6 AS (
                SELECT SourceDate, AVG(mark6_num) AS med6
                FROM (
                    SELECT SourceDate, mark6_num,
                           ROW_NUMBER() OVER (PARTITION BY SourceDate ORDER BY mark6_num) AS rn,
                           COUNT(*)     OVER (PARTITION BY SourceDate)                     AS cnt
                    FROM excel_marks WHERE mark6_num IS NOT NULL
                )
                WHERE rn IN ( (cnt + 1)/2, (cnt + 2)/2 )
                GROUP BY SourceDate
            ),
            gmed AS (
                SELECT
                    (SELECT AVG(mark5_num) FROM excel_marks WHERE mark5_num IS NOT NULL) AS gmed5,
                    (SELECT AVG(mark6_num) FROM excel_marks WHERE mark6_num IS NOT NULL) AS gmed6
            )
            SELECT
                se.*,
                -- 欠損フラグ
                CASE WHEN se.mark5_num IS NULL THEN 1 ELSE 0 END AS mark5_missing_flag,
                CASE WHEN se.mark6_num IS NULL THEN 1 ELSE 0 END AS mark6_missing_flag,
                -- 補完値（レース中央値→全体中央値→0）
                CASE
                    WHEN se.mark5_num IS NOT NULL THEN se.mark5_num
                    WHEN m5.med5 IS NOT NULL        THEN m5.med5
                    WHEN g.gmed5 IS NOT NULL        THEN g.gmed5
                    ELSE 0
                END AS mark5_imp,
                CASE
                    WHEN se.mark6_num IS NOT NULL THEN se.mark6_num
                    WHEN m6.med6 IS NOT NULL      THEN m6.med6
                    WHEN g.gmed6 IS NOT NULL      THEN g.gmed6
                    ELSE 0
                END AS mark6_imp
            FROM excel_marks se
            LEFT JOIN med5 m5 ON m5.SourceDate = se.SourceDate
            LEFT JOIN med6 m6 ON m6.SourceDate = se.SourceDate
            CROSS JOIN gmed g
            """)
            
            self.conn.commit()
            print("派生テーブル SE_FE 作成完了")
            
            return True
            
        except Exception as e:
            print(f"派生テーブル作成エラー: {e}")
            return False
    
    def check_quality_metrics(self):
        """4) DQゲートの基準を2段に分離"""
        print("=== 品質メトリクス確認 ===")
        
        try:
            # 生データ未知率
            query_raw = """
            SELECT
                ROUND(100.0 * SUM(CASE WHEN mark5_num IS NULL AND TRIM(COALESCE(Mark5,'')) <> '' THEN 1 ELSE 0 END)
                / NULLIF(SUM(CASE WHEN TRIM(COALESCE(Mark5,'')) <> '' THEN 1 ELSE 0 END),0), 2) AS m5_unknown_pct,
                ROUND(100.0 * SUM(CASE WHEN mark6_num IS NULL AND TRIM(COALESCE(Mark6,'')) <> '' THEN 1 ELSE 0 END)
                / NULLIF(SUM(CASE WHEN TRIM(COALESCE(Mark6,'')) <> '' THEN 1 ELSE 0 END),0), 2) AS m6_unknown_pct
            FROM excel_marks
            """
            result_raw = pd.read_sql_query(query_raw, self.conn)
            
            print("生データ未知率:")
            print(f"Mark5未知率: {result_raw.iloc[0]['m5_unknown_pct']:.2f}%")
            print(f"Mark6未知率: {result_raw.iloc[0]['m6_unknown_pct']:.2f}%")
            
            # 派生側（理論上0%）
            query_imp = """
            SELECT
                SUM(CASE WHEN mark5_imp IS NULL THEN 1 ELSE 0 END) AS m5_imp_nulls,
                SUM(CASE WHEN mark6_imp IS NULL THEN 1 ELSE 0 END) AS m6_imp_nulls
            FROM SE_FE
            """
            result_imp = pd.read_sql_query(query_imp, self.conn)
            
            print("派生側未知率:")
            print(f"Mark5_imp NULL: {result_imp.iloc[0]['m5_imp_nulls']}件")
            print(f"Mark6_imp NULL: {result_imp.iloc[0]['m6_imp_nulls']}件")
            
            # 欠損フラグの比率（監視用）
            query_missing = """
            SELECT
                ROUND(AVG(mark5_missing_flag) * 100.0, 2) AS m5_missing_rate_pct,
                ROUND(AVG(mark6_missing_flag) * 100.0, 2) AS m6_missing_rate_pct
            FROM SE_FE
            """
            result_missing = pd.read_sql_query(query_missing, self.conn)
            
            print("欠損フラグ比率:")
            print(f"Mark5欠損率: {result_missing.iloc[0]['m5_missing_rate_pct']:.2f}%")
            print(f"Mark6欠損率: {result_missing.iloc[0]['m6_missing_rate_pct']:.2f}%")
            
            # 品質評価
            m5_unknown_pct = result_raw.iloc[0]['m5_unknown_pct']
            m6_unknown_pct = result_raw.iloc[0]['m6_unknown_pct']
            m5_imp_nulls = result_imp.iloc[0]['m5_imp_nulls']
            m6_imp_nulls = result_imp.iloc[0]['m6_imp_nulls']
            
            # 生データ未知率の評価
            if m5_unknown_pct <= 30 and m6_unknown_pct <= 30:
                print("✅ 生データ未知率: 良好（30%以下）")
                raw_ok = True
            elif m5_unknown_pct <= 60 and m6_unknown_pct <= 60:
                print("⚠️ 生データ未知率: 注意（60%以下）")
                raw_ok = True
            else:
                print("❌ 生データ未知率: 不良（60%超）")
                raw_ok = False
            
            # 派生側未知率の評価
            if m5_imp_nulls == 0 and m6_imp_nulls == 0:
                print("✅ 派生側未知率: 完璧（0%）")
                imp_ok = True
            else:
                print("❌ 派生側未知率: 問題あり")
                imp_ok = False
            
            return raw_ok and imp_ok
            
        except Exception as e:
            print(f"品質メトリクス確認エラー: {e}")
            return False
    
    def run_imputation(self):
        """Mark5/Mark6補完実行"""
        print("=== Mark5/Mark6補完実行 ===")
        
        # 1) '？' を辞書で NULL に統一
        if not self.add_question_mark_aliases():
            return False
        
        # 3) 派生テーブル作成
        if not self.create_derived_table():
            return False
        
        # 4) 品質メトリクス確認
        quality_ok = self.check_quality_metrics()
        
        return quality_ok

def main():
    imputer = MarkImputation()
    success = imputer.run_imputation()
    
    if success:
        print("\n✅ Mark5/Mark6補完完了")
    else:
        print("\n❌ Mark5/Mark6補完失敗")

if __name__ == "__main__":
    main()
