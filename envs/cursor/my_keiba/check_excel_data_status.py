import sqlite3
import sys
from pathlib import Path

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def check_excel_data_status():
    """excel_data.dbの状況確認"""
    print("=== excel_data.dbの状況確認 ===")
    
    try:
        # データベース接続
        conn = sqlite3.connect('excel_data.db')
        cursor = conn.cursor()
        
        # テーブル一覧
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print("テーブル一覧:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # HORSE_MARKSテーブルの確認
        if any('HORSE_MARKS' in str(table) for table in tables):
            print("\n=== HORSE_MARKSテーブルの確認 ===")
            
            # レコード数
            cursor.execute("SELECT COUNT(*) FROM HORSE_MARKS")
            count = cursor.fetchone()[0]
            print(f"総レコード数: {count:,}")
            
            # 最新のデータ
            cursor.execute("""
                SELECT SourceDate, HorseName, Mark5, Mark6, ZI_INDEX, ZM_VALUE, SourceFile
                FROM HORSE_MARKS 
                ORDER BY ImportedAt DESC 
                LIMIT 5
            """)
            recent_data = cursor.fetchall()
            
            print("\n最新のデータ（上位5件）:")
            for row in recent_data:
                print(f"  日付: {row[0]}, 馬名: {row[1]}, Mark5: {row[2]}, Mark6: {row[3]}, ZI: {row[4]}, ZM: {row[5]}, ファイル: {row[6]}")
            
            # 馬印データの統計
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN Mark5 IS NOT NULL AND Mark5 != '' THEN 1 END) as mark5_count,
                    COUNT(CASE WHEN Mark6 IS NOT NULL AND Mark6 != '' THEN 1 END) as mark6_count,
                    COUNT(CASE WHEN ZI_INDEX IS NOT NULL AND ZI_INDEX != '' THEN 1 END) as zi_count,
                    COUNT(CASE WHEN ZM_VALUE IS NOT NULL AND ZM_VALUE != '' THEN 1 END) as zm_count
                FROM HORSE_MARKS
            """)
            stats = cursor.fetchone()
            
            print(f"\n馬印データ統計:")
            print(f"  総レコード数: {stats[0]:,}")
            print(f"  Mark5データ: {stats[1]:,} ({stats[1]/stats[0]*100:.1f}%)")
            print(f"  Mark6データ: {stats[2]:,} ({stats[2]/stats[0]*100:.1f}%)")
            print(f"  ZI_INDEXデータ: {stats[3]:,} ({stats[3]/stats[0]*100:.1f}%)")
            print(f"  ZM_VALUEデータ: {stats[4]:,} ({stats[4]/stats[0]*100:.1f}%)")
            
        else:
            print("❌ HORSE_MARKSテーブルが見つかりません")
        
        conn.close()
        
    except Exception as e:
        print(f"エラー: {e}")

if __name__ == "__main__":
    check_excel_data_status()




