import sqlite3
import sys
import io
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

DB_PATH = 'ecore.db'

def fix_duplicates_and_migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=== 重複データ修正と移行 ===\n")

    # 1. 重複データの詳細確認
    print("1. 重複データの詳細確認")
    cursor.execute("""
        SELECT Year, MonthDay, JyoCD, RaceNum, Umaban, COUNT(*) as cnt 
        FROM N_UMA_RACE 
        WHERE Year = '2023' 
        GROUP BY Year, MonthDay, JyoCD, RaceNum, Umaban 
        HAVING COUNT(*) > 1
    """)
    duplicates = cursor.fetchall()
    
    print(f"重複データ: {len(duplicates)} 件")
    for dup in duplicates:
        print(f"  {dup[0]}{dup[1]} 場{dup[2]} {dup[3]}R {dup[4]}番: {dup[5]}件")

    # 2. 重複データの削除（最新のレコードのみ残す）
    print("\n2. 重複データの削除")
    cursor.execute("""
        DELETE FROM N_UMA_RACE 
        WHERE Year = '2023' 
        AND (Year, MonthDay, JyoCD, RaceNum, Umaban) IN (
            SELECT Year, MonthDay, JyoCD, RaceNum, Umaban 
            FROM N_UMA_RACE 
            WHERE Year = '2023' 
            GROUP BY Year, MonthDay, JyoCD, RaceNum, Umaban 
            HAVING COUNT(*) > 1
        )
        AND ROWID NOT IN (
            SELECT MAX(ROWID) 
            FROM N_UMA_RACE 
            WHERE Year = '2023' 
            GROUP BY Year, MonthDay, JyoCD, RaceNum, Umaban 
            HAVING COUNT(*) > 1
        )
    """)
    deleted_count = cursor.rowcount
    print(f"  [OK] {deleted_count} 件の重複データを削除しました")

    # 3. 削除後の確認
    print("\n3. 削除後の確認")
    cursor.execute("SELECT COUNT(*) FROM N_UMA_RACE WHERE Year = '2023'")
    remaining_count = cursor.fetchone()[0]
    print(f"2023年残存レコード数: {remaining_count:,} 件")

    # 4. NL_SE_RACE_UMAテーブルの再作成
    print("\n4. NL_SE_RACE_UMAテーブルの再作成")
    cursor.execute("DROP TABLE IF EXISTS NL_SE_RACE_UMA")
    cursor.execute("""
        CREATE TABLE NL_SE_RACE_UMA (
            Year VARCHAR(4),
            MonthDay VARCHAR(4),
            JyoCD VARCHAR(2),
            RaceNum VARCHAR(2),
            Wakuban VARCHAR(1),
            Umaban VARCHAR(2),
            KettoNum VARCHAR(10),
            Bamei VARCHAR(36),
            KisyuRyakusyo VARCHAR(8),
            ChokyosiRyakusyo VARCHAR(8),
            BaTaijyu VARCHAR(3),
            Odds VARCHAR(4),
            Ninki VARCHAR(2),
            Honsyokin VARCHAR(8),
            Fukasyokin VARCHAR(8),
            NyusenJyuni VARCHAR(2),
            KakuteiJyuni VARCHAR(2),
            Time VARCHAR(4),
            ChakusaCD VARCHAR(3),
            PRIMARY KEY (Year, MonthDay, JyoCD, RaceNum, Umaban)
        )
    """)
    print("  [OK] NL_SE_RACE_UMAテーブルを作成しました")

    # 5. 2023年データの移行
    print("\n5. 2023年データの移行")
    cursor.execute("""
        INSERT INTO NL_SE_RACE_UMA
        SELECT
            Year, MonthDay, JyoCD, RaceNum, Wakuban, Umaban, KettoNum, Bamei,
            KisyuRyakusyo, ChokyosiRyakusyo, BaTaijyu, Odds, Ninki,
            Honsyokin, Fukasyokin, NyusenJyuni, KakuteiJyuni, Time, ChakusaCD
        FROM N_UMA_RACE
        WHERE Year = '2023'
    """)
    migrated_count = cursor.rowcount
    print(f"  [OK] {migrated_count:,} 件の2023年データを移行しました")

    # 6. 移行後の確認
    print("\n6. 移行後の確認")
    cursor.execute("SELECT COUNT(*) FROM NL_SE_RACE_UMA WHERE Year = '2023'")
    nl_se_count = cursor.fetchone()[0]
    print(f"NL_SE_RACE_UMA 2023年データ: {nl_se_count:,} 件")

    # 7. プラダリアの2023年データ確認
    print("\n7. プラダリアの2023年データ確認")
    cursor.execute("""
        SELECT COUNT(*) FROM NL_SE_RACE_UMA 
        WHERE Bamei = 'プラダリア' AND Year = '2023'
    """)
    pradaria_count = cursor.fetchone()[0]
    print(f"プラダリアの2023年データ: {pradaria_count} 件")

    # 8. インデックスの作成
    print("\n8. インデックスの作成")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_nl_se_race_uma_2023 ON NL_SE_RACE_UMA (Year)")
    print("  [OK] 2023年インデックスを作成しました")

    conn.commit()
    conn.close()
    print("\n=== 修正完了 ===")
    print("重複データが修正され、NL_SE_RACE_UMAに2023年データが移行されました。")
    print("JVMonitorで2023年のデータが表示されるはずです。")

if __name__ == '__main__':
    fix_duplicates_and_migrate()
