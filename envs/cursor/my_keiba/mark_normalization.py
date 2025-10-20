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

class MarkNormalization:
    """Mark5/Mark6の非数値データ処理 - 再発防止システム"""
    
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
    
    def create_alias_dictionary(self):
        """① マッピング辞書を導入"""
        print("=== Mark5/Mark6辞書テーブル作成 ===")
        
        try:
            cursor = self.conn.cursor()
            
            # 辞書テーブル作成
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS MARK_ALIASES (
                raw_text TEXT PRIMARY KEY,
                value    REAL NOT NULL,
                note     TEXT
            )
            """)
            
            # よくある印字・表現を登録
            aliases = [
                ('◎', 5, '本命'),
                ('◉', 5, '本命バリアント'),
                ('○', 4, '対抗'),
                ('○ ', 4, '対抗(空白込)'),
                ('●', 4, '対抗バリアント'),
                ('▲', 3, '単穴'),
                ('△', 2, '連下'),
                ('☆', 2, '星'),
                ('×', 1, '穴'),
                ('無', 0, '無印'),
                ('—', 0, 'ダッシュ=無印扱い'),
                ('-', 0, 'ハイフン=無印扱い'),
                ('N/A', None, '情報なし'),
                ('?', None, '不明'),
                ('？', None, '全角不明'),
                ('NaN', None, '非数'),
                ('約', None, '曖昧表示除外'),
                ('－', 0, '全角ハイフン=無印'),
                ('ー', 0, '長音=無印'),
                ('S', 5, 'グレードS'),
                ('A', 4, 'グレードA'),
                ('B', 3, 'グレードB'),
                ('C', 2, 'グレードC'),
                ('D', 1, 'グレードD'),
                ('E', 0, 'グレードE')
            ]
            
            for raw_text, value, note in aliases:
                cursor.execute("""
                INSERT OR IGNORE INTO MARK_ALIASES (raw_text, value, note)
                VALUES (?, ?, ?)
                """, (raw_text, value, note))
            
            self.conn.commit()
            print(f"辞書登録完了: {len(aliases)}件")
            
            return True
            
        except Exception as e:
            print(f"辞書テーブル作成エラー: {e}")
            return False
    
    def create_normalized_view(self):
        """正規化ビュー作成"""
        print("=== 正規化ビュー作成 ===")
        
        try:
            cursor = self.conn.cursor()
            
            # 既存ビューを削除
            cursor.execute("DROP VIEW IF EXISTS V_NORMALIZED_MARKS")
            
            # 正規化ビュー作成
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
                    -- 全角→半角・余計な文言の除去
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
                    -- Mark5
                    COALESCE( 
                        (SELECT value FROM MARK_ALIASES WHERE raw_text = n.m5_s),
                        CASE
                            WHEN n.m5_s GLOB '*-*' THEN CAST(SUBSTR(n.m5_s,1,INSTR(n.m5_s,'-')-1) AS REAL)
                            WHEN n.m5_s IN ('', '-', '—', 'N/A', 'NaN', '?','？') THEN NULL
                            WHEN n.m5_s LIKE '%倍' THEN CAST(REPLACE(n.m5_s,'倍','') AS REAL)
                            ELSE CAST(n.m5_s AS REAL)
                        END
                    ) AS m5_val,
                    -- Mark6
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
            
            self.conn.commit()
            print("正規化ビュー作成完了")
            
            return True
            
        except Exception as e:
            print(f"正規化ビュー作成エラー: {e}")
            return False
    
    def update_mark_values(self):
        """Mark5/Mark6値を更新"""
        print("=== Mark5/Mark6値更新 ===")
        
        try:
            cursor = self.conn.cursor()
            
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
            print(f"Mark5/Mark6値更新エラー: {e}")
            return False
    
    def analyze_unparsed_tokens(self):
        """② 未解析トークンの棚卸し"""
        print("=== 未解析トークン分析 ===")
        
        try:
            # Mark5の未解析トークン
            query_m5 = """
            SELECT TRIM(Mark5) AS token, COUNT(*) AS freq
            FROM excel_marks
            WHERE Mark5 IS NOT NULL
              AND Mark5 <> ''
              AND Mark5_num IS NULL
            GROUP BY TRIM(Mark5)
            ORDER BY freq DESC
            LIMIT 50
            """
            result_m5 = pd.read_sql_query(query_m5, self.conn)
            
            print("Mark5未解析トークン（上位50）:")
            print(result_m5.to_string(index=False))
            
            # Mark6の未解析トークン
            query_m6 = """
            SELECT TRIM(Mark6) AS token, COUNT(*) AS freq
            FROM excel_marks
            WHERE Mark6 IS NOT NULL
              AND Mark6 <> ''
              AND Mark6_num IS NULL
            GROUP BY TRIM(Mark6)
            ORDER BY freq DESC
            LIMIT 50
            """
            result_m6 = pd.read_sql_query(query_m6, self.conn)
            
            print("\nMark6未解析トークン（上位50）:")
            print(result_m6.to_string(index=False))
            
            return result_m5, result_m6
            
        except Exception as e:
            print(f"未解析トークン分析エラー: {e}")
            return None, None
    
    def add_common_aliases(self):
        """よくある別名を辞書に追加"""
        print("=== よくある別名を辞書に追加 ===")
        
        try:
            cursor = self.conn.cursor()
            
            # よくある別名を追加
            additional_aliases = [
                ('0', 0, '数値0'),
                ('1', 1, '数値1'),
                ('2', 2, '数値2'),
                ('3', 3, '数値3'),
                ('4', 4, '数値4'),
                ('5', 5, '数値5'),
                ('6', 6, '数値6'),
                ('7', 7, '数値7'),
                ('8', 8, '数値8'),
                ('9', 9, '数値9'),
                ('10', 10, '数値10'),
                ('11', 11, '数値11'),
                ('12', 12, '数値12'),
                ('13', 13, '数値13'),
                ('14', 14, '数値14'),
                ('15', 15, '数値15'),
                ('16', 16, '数値16'),
                ('17', 17, '数値17'),
                ('18', 18, '数値18'),
                ('19', 19, '数値19'),
                ('20', 20, '数値20'),
                ('', None, '空文字'),
                (' ', None, '空白'),
                ('　', None, '全角空白'),
                ('null', None, 'null文字列'),
                ('NULL', None, 'NULL文字列'),
                ('undefined', None, 'undefined'),
                ('inf', None, '無限大'),
                ('-inf', None, '負の無限大'),
                ('nan', None, '非数値'),
                ('#N/A', None, 'Excel非数値'),
                ('#VALUE!', None, 'Excel値エラー'),
                ('#REF!', None, 'Excel参照エラー'),
                ('#DIV/0!', None, 'Excel除算エラー'),
                ('#NAME?', None, 'Excel名前エラー'),
                ('#NUM!', None, 'Excel数値エラー'),
                ('#NULL!', None, 'Excel空エラー'),
                ('#ERROR!', None, 'Excelエラー'),
                ('#N/A!', None, 'Excel非数値'),
                ('#VALUE!', None, 'Excel値エラー'),
                ('#REF!', None, 'Excel参照エラー'),
                ('#DIV/0!', None, 'Excel除算エラー'),
                ('#NAME?', None, 'Excel名前エラー'),
                ('#NUM!', None, 'Excel数値エラー'),
                ('#NULL!', None, 'Excel空エラー'),
                ('#ERROR!', None, 'Excelエラー')
            ]
            
            for raw_text, value, note in additional_aliases:
                cursor.execute("""
                INSERT OR IGNORE INTO MARK_ALIASES (raw_text, value, note)
                VALUES (?, ?, ?)
                """, (raw_text, value, note))
            
            self.conn.commit()
            print(f"追加辞書登録完了: {len(additional_aliases)}件")
            
            return True
            
        except Exception as e:
            print(f"追加辞書登録エラー: {e}")
            return False
    
    def check_quality_metrics(self):
        """③ 品質メトリクス確認"""
        print("=== 品質メトリクス確認 ===")
        
        try:
            query = """
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN Mark5 IS NOT NULL AND TRIM(Mark5) <> '' THEN 1 ELSE 0 END) AS m5_raw_filled,
                SUM(CASE WHEN Mark5_num IS NULL AND TRIM(Mark5) <> '' THEN 1 ELSE 0 END) AS m5_unparsed,
                ROUND(100.0 * SUM(CASE WHEN Mark5_num IS NULL AND TRIM(Mark5) <> '' THEN 1 ELSE 0 END) /
                         NULLIF(SUM(CASE WHEN Mark5 IS NOT NULL AND TRIM(Mark5) <> '' THEN 1 ELSE 0 END),0), 2) AS m5_unknown_pct,
                SUM(CASE WHEN Mark6 IS NOT NULL AND TRIM(Mark6) <> '' THEN 1 ELSE 0 END) AS m6_raw_filled,
                SUM(CASE WHEN Mark6_num IS NULL AND TRIM(Mark6) <> '' THEN 1 ELSE 0 END) AS m6_unparsed,
                ROUND(100.0 * SUM(CASE WHEN Mark6_num IS NULL AND TRIM(Mark6) <> '' THEN 1 ELSE 0 END) /
                         NULLIF(SUM(CASE WHEN Mark6 IS NOT NULL AND TRIM(Mark6) <> '' THEN 1 ELSE 0 END),0), 2) AS m6_unknown_pct
            FROM excel_marks
            """
            result = pd.read_sql_query(query, self.conn)
            
            print("品質メトリクス:")
            print(f"総件数: {result.iloc[0]['total']:,}")
            print(f"Mark5生データ: {result.iloc[0]['m5_raw_filled']:,}")
            print(f"Mark5未解析: {result.iloc[0]['m5_unparsed']:,}")
            print(f"Mark5未知率: {result.iloc[0]['m5_unknown_pct']:.2f}%")
            print(f"Mark6生データ: {result.iloc[0]['m6_raw_filled']:,}")
            print(f"Mark6未解析: {result.iloc[0]['m6_unparsed']:,}")
            print(f"Mark6未知率: {result.iloc[0]['m6_unknown_pct']:.2f}%")
            
            # 品質評価
            m5_unknown_pct = result.iloc[0]['m5_unknown_pct']
            m6_unknown_pct = result.iloc[0]['m6_unknown_pct']
            
            if m5_unknown_pct <= 5 and m6_unknown_pct <= 5:
                print("✅ 品質良好（未知率5%以下）")
                return True
            elif m5_unknown_pct <= 10 and m6_unknown_pct <= 10:
                print("⚠️ 品質注意（未知率10%以下）")
                return True
            else:
                print("❌ 品質不良（未知率10%超）")
                return False
                
        except Exception as e:
            print(f"品質メトリクス確認エラー: {e}")
            return False
    
    def run_normalization(self):
        """Mark5/Mark6正規化実行"""
        print("=== Mark5/Mark6正規化実行 ===")
        
        # ① 辞書テーブル作成
        if not self.create_alias_dictionary():
            return False
        
        # 正規化ビュー作成
        if not self.create_normalized_view():
            return False
        
        # Mark5/Mark6値更新
        if not self.update_mark_values():
            return False
        
        # よくある別名を追加
        if not self.add_common_aliases():
            return False
        
        # Mark5/Mark6値再更新
        if not self.update_mark_values():
            return False
        
        # ② 未解析トークン分析
        result_m5, result_m6 = self.analyze_unparsed_tokens()
        
        # ③ 品質メトリクス確認
        quality_ok = self.check_quality_metrics()
        
        return quality_ok

def main():
    normalizer = MarkNormalization()
    success = normalizer.run_normalization()
    
    if success:
        print("\n✅ Mark5/Mark6正規化完了")
    else:
        print("\n❌ Mark5/Mark6正規化失敗")

if __name__ == "__main__":
    main()




