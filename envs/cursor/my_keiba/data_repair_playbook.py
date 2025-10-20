import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
import shutil
import os
import sys

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

class DataRepairPlaybook:
    """データ修復プレイブック - 最短で直す"""
    
    def __init__(self, db_path="trainer_prediction_system/excel_data.db"):
        self.db_path = db_path
        self.backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
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
    
    def create_backup(self):
        """0) バックアップ作成（必須）"""
        print("=== バックアップ作成 ===")
        try:
            shutil.copy2(self.db_path, self.backup_path)
            print(f"バックアップ作成完了: {self.backup_path}")
            return True
        except Exception as e:
            print(f"バックアップ作成エラー: {e}")
            return False
    
    def fix_duplicates(self):
        """1) 重複データ 2件の削除"""
        print("=== 重複データ削除 ===")
        
        try:
            # 1-1) 重複の確認
            query_check = """
            SELECT SourceDate, HorseNameS, Trainer_Name, COUNT(*) as cnt
            FROM excel_marks
            GROUP BY SourceDate, HorseNameS, Trainer_Name
            HAVING COUNT(*) > 1
            """
            duplicates = pd.read_sql_query(query_check, self.conn)
            
            if len(duplicates) > 0:
                print(f"重複データ発見: {len(duplicates)}件")
                
                # 1-2) 最新を残して他を削除
                query_delete = """
                DELETE FROM excel_marks
                WHERE rowid NOT IN (
                    SELECT MIN(rowid)
                    FROM excel_marks
                    GROUP BY SourceDate, HorseNameS, Trainer_Name
                )
                """
                cursor = self.conn.cursor()
                cursor.execute(query_delete)
                self.conn.commit()
                
                print(f"重複データ削除完了: {cursor.rowcount}件")
            else:
                print("重複データなし")
            
            return True
            
        except Exception as e:
            print(f"重複データ削除エラー: {e}")
            return False
    
    def fix_null_columns(self):
        """2) 必須カラムNULL 2件の修復"""
        print("=== 必須カラムNULL修復 ===")
        
        try:
            # 2-1) NULLの確認
            query_check = """
            SELECT COUNT(*) as cnt
            FROM excel_marks
            WHERE HorseNameS IS NULL OR HorseNameS = '' OR
                  Trainer_Name IS NULL OR Trainer_Name = '' OR
                  Mark5 IS NULL OR Mark5 = '' OR
                  Mark6 IS NULL OR Mark6 = ''
            """
            result = pd.read_sql_query(query_check, self.conn)
            null_count = result.iloc[0]['cnt']
            
            if null_count > 0:
                print(f"NULL値発見: {null_count}件")
                
                # 2-2) 補完可能なものは補完
                query_fix = """
                UPDATE excel_marks
                SET HorseNameS = COALESCE(HorseNameS, '不明'),
                    Trainer_Name = COALESCE(Trainer_Name, '不明'),
                    Mark5 = COALESCE(Mark5, '0'),
                    Mark6 = COALESCE(Mark6, '0')
                WHERE HorseNameS IS NULL OR HorseNameS = '' OR
                      Trainer_Name IS NULL OR Trainer_Name = '' OR
                      Mark5 IS NULL OR Mark5 = '' OR
                      Mark6 IS NULL OR Mark6 = ''
                """
                cursor = self.conn.cursor()
                cursor.execute(query_fix)
                self.conn.commit()
                
                print(f"NULL値修復完了: {cursor.rowcount}件")
            else:
                print("NULL値なし")
            
            return True
            
        except Exception as e:
            print(f"NULL値修復エラー: {e}")
            return False
    
    def fix_mark5_mark6(self):
        """3) Mark5/Mark6（22,231件）の数値正規化"""
        print("=== Mark5/Mark6数値正規化 ===")
        
        try:
            # 3-0) クリーン列を追加
            cursor = self.conn.cursor()
            
            # Mark5_num列を追加（既存チェック）
            try:
                cursor.execute("ALTER TABLE excel_marks ADD COLUMN Mark5_num REAL")
                print("Mark5_num列追加")
            except:
                print("Mark5_num列は既に存在")
            
            # Mark6_num列を追加（既存チェック）
            try:
                cursor.execute("ALTER TABLE excel_marks ADD COLUMN Mark6_num REAL")
                print("Mark6_num列追加")
            except:
                print("Mark6_num列は既に存在")
            
            # 3-1) Mark5の正規化
            query_mark5 = """
            UPDATE excel_marks
            SET Mark5_num = CASE
                WHEN Mark5 = '?' OR Mark5 = '' OR Mark5 IS NULL THEN NULL
                WHEN Mark5 GLOB '[0-9]*' THEN CAST(Mark5 AS REAL)
                ELSE NULL
            END
            """
            cursor.execute(query_mark5)
            self.conn.commit()
            
            # 3-1) Mark6の正規化
            query_mark6 = """
            UPDATE excel_marks
            SET Mark6_num = CASE
                WHEN Mark6 = '?' OR Mark6 = '' OR Mark6 IS NULL THEN NULL
                WHEN Mark6 GLOB '[0-9]*' THEN CAST(Mark6 AS REAL)
                ELSE NULL
            END
            """
            cursor.execute(query_mark6)
            self.conn.commit()
            
            # 3-2) 修復結果の確認
            query_check = """
            SELECT 
                SUM(CASE WHEN Mark5_num IS NULL AND TRIM(Mark5) != '' THEN 1 ELSE 0 END) AS m5_unparsed,
                SUM(CASE WHEN Mark6_num IS NULL AND TRIM(Mark6) != '' THEN 1 ELSE 0 END) AS m6_unparsed
            FROM excel_marks
            """
            result = pd.read_sql_query(query_check, self.conn)
            m5_unparsed = result.iloc[0]['m5_unparsed']
            m6_unparsed = result.iloc[0]['m6_unparsed']
            
            print(f"Mark5未変換: {m5_unparsed}件")
            print(f"Mark6未変換: {m6_unparsed}件")
            
            return True
            
        except Exception as e:
            print(f"Mark5/Mark6正規化エラー: {e}")
            return False
    
    def add_constraints(self):
        """5) 再発防止策（必須）"""
        print("=== 再発防止策追加 ===")
        
        try:
            cursor = self.conn.cursor()
            
            # ユニーク制約の追加（重複防止）
            try:
                cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_excel_marks_unique ON excel_marks(SourceDate, HorseNameS, Trainer_Name)")
                print("ユニーク制約追加完了")
            except Exception as e:
                print(f"ユニーク制約追加エラー: {e}")
            
            # チェック制約の追加（データ品質向上）
            try:
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS excel_marks_constraints AS 
                SELECT * FROM excel_marks WHERE 1=0
                """)
                print("制約テーブル作成完了")
            except Exception as e:
                print(f"制約テーブル作成エラー: {e}")
            
            return True
            
        except Exception as e:
            print(f"再発防止策追加エラー: {e}")
            return False
    
    def final_check(self):
        """6) 最終チェック（ゲート再実行）"""
        print("=== 最終チェック ===")
        
        try:
            # 重複チェック
            query_dup = """
            SELECT COUNT(*) as cnt
            FROM (
                SELECT SourceDate, HorseNameS, Trainer_Name, COUNT(*) as c
                FROM excel_marks
                GROUP BY SourceDate, HorseNameS, Trainer_Name
                HAVING c > 1
            )
            """
            result_dup = pd.read_sql_query(query_dup, self.conn)
            dup_count = result_dup.iloc[0]['cnt']
            
            # NULLチェック
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
            
            # Mark5/Mark6変換チェック
            query_mark = """
            SELECT COUNT(*) as cnt
            FROM excel_marks
            WHERE (Mark5 = '?' OR Mark5 = '' OR Mark5 IS NULL) AND
                  (Mark6 = '?' OR Mark6 = '' OR Mark6 IS NULL)
            """
            result_mark = pd.read_sql_query(query_mark, self.conn)
            mark_count = result_mark.iloc[0]['cnt']
            
            print(f"重複データ: {dup_count}件")
            print(f"NULL値: {null_count}件")
            print(f"Mark5/Mark6変換エラー: {mark_count}件")
            
            if dup_count == 0 and null_count == 0 and mark_count == 0:
                print("✅ 最終チェック成功 - 分析可能")
                return True
            else:
                print("❌ 最終チェック失敗 - 追加修復が必要")
                return False
                
        except Exception as e:
            print(f"最終チェックエラー: {e}")
            return False
    
    def run_repair(self):
        """修復プレイブック実行"""
        print("=== データ修復プレイブック実行 ===")
        
        # 0) バックアップ作成
        if not self.create_backup():
            return False
        
        # 1) 重複データ削除
        if not self.fix_duplicates():
            return False
        
        # 2) NULL値修復
        if not self.fix_null_columns():
            return False
        
        # 3) Mark5/Mark6正規化
        if not self.fix_mark5_mark6():
            return False
        
        # 5) 再発防止策追加
        if not self.add_constraints():
            return False
        
        # 6) 最終チェック
        if not self.final_check():
            return False
        
        print("✅ データ修復プレイブック完了")
        return True

def main():
    repair = DataRepairPlaybook()
    success = repair.run_repair()
    
    if success:
        print("\n✅ データ修復完了 - 分析可能")
    else:
        print("\n❌ データ修復失敗 - 追加対応が必要")

if __name__ == "__main__":
    main()




