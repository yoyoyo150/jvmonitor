import sqlite3
import sys
import io
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

DB_PATH = 'ecore.db'

def recreate_nl_se_race_uma():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=== NL_SE_RACE_UMAテーブル再作成 ===\n")

    # 1. 既存テーブルの削除
    print("1. 既存テーブルの削除")
    cursor.execute("DROP TABLE IF EXISTS NL_SE_RACE_UMA")
    print("  [OK] NL_SE_RACE_UMAテーブルを削除しました")

    # 2. テーブルの再作成
    print("\n2. テーブルの再作成")
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

    # 3. 2023年データの移行（重複除去）
    print("\n3. 2023年データの移行（重複除去）")
    cursor.execute("""
        INSERT INTO NL_SE_RACE_UMA
        SELECT 
            Year, MonthDay, JyoCD, RaceNum, Wakuban, Umaban, KettoNum, Bamei,
            KisyuRyakusyo, ChokyosiRyakusyo, BaTaijyu, Odds, Ninki,
            Honsyokin, Fukasyokin, NyusenJyuni, KakuteiJyuni, Time, ChakusaCD
        FROM (
            SELECT DISTINCT
                Year, MonthDay, JyoCD, RaceNum, Wakuban, Umaban, KettoNum, Bamei,
                KisyuRyakusyo, ChokyosiRyakusyo, BaTaijyu, Odds, Ninki,
                Honsyokin, Fukasyokin, NyusenJyuni, KakuteiJyuni, Time, ChakusaCD
            FROM N_UMA_RACE
            WHERE Year = '2023'
        )
    """)
    print(f"  [OK] {conn.changes():,} 件の2023年データを移行しました")

    # 4. 移行後の確認
    print("\n4. 移行後の確認")
    cursor.execute("SELECT COUNT(*) FROM NL_SE_RACE_UMA WHERE Year = '2023'")
    new_2023_count = cursor.fetchone()[0]
    print(f"移行後のNL_SE_RACE_UMA 2023年データ: {new_2023_count:,} 件")

    # 5. プラダリアの2023年データ確認
    print("\n5. プラダリアの2023年データ確認")
    cursor.execute("""
        SELECT COUNT(*) FROM NL_SE_RACE_UMA 
        WHERE Bamei = 'プラダリア' AND Year = '2023'
    """)
    pradaria_2023_count = cursor.fetchone()[0]
    print(f"プラダリアの2023年データ: {pradaria_2023_count} 件")

    # 6. インデックスの作成
    print("\n6. インデックスの作成")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_nl_se_race_uma_2023 ON NL_SE_RACE_UMA (Year)")
    print("  [OK] 2023年インデックスを作成しました")

    conn.commit()
    conn.close()
    print("\n=== 再作成完了 ===")
    print("NL_SE_RACE_UMAテーブルが再作成され、2023年データが移行されました。")
    print("JVMonitorで2023年のデータが表示されるはずです。")

if __name__ == '__main__':
    recreate_nl_se_race_uma()
