import sqlite3
import sys
import io
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

DB_PATH = 'ecore.db'

def fix_nl_se_race_uma_2023():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=== NL_SE_RACE_UMA 2023年データ修正 ===\n")

    # 1. 現在のNL_SE_RACE_UMAの2023年データ確認
    print("1. 現在のNL_SE_RACE_UMAの2023年データ確認")
    cursor.execute("SELECT COUNT(*) FROM NL_SE_RACE_UMA WHERE Year = '2023'")
    current_2023_count = cursor.fetchone()[0]
    print(f"現在のNL_SE_RACE_UMA 2023年データ: {current_2023_count:,} 件")

    # 2. N_UMA_RACEの2023年データ確認
    print("\n2. N_UMA_RACEの2023年データ確認")
    cursor.execute("SELECT COUNT(*) FROM N_UMA_RACE WHERE Year = '2023'")
    n_uma_race_2023_count = cursor.fetchone()[0]
    print(f"N_UMA_RACE 2023年データ: {n_uma_race_2023_count:,} 件")

    # 3. 既存のデータを完全にクリア
    print("\n3. 既存のデータを完全にクリア")
    cursor.execute("DELETE FROM NL_SE_RACE_UMA")
    print(f"  [OK] 既存のデータを完全にクリアしました")

    # 4. 2023年データをNL_SE_RACE_UMAに移行
    print("\n4. 2023年データをNL_SE_RACE_UMAに移行")
    cursor.execute("""
        INSERT INTO NL_SE_RACE_UMA
        SELECT
            Year, MonthDay, JyoCD, RaceNum, Wakuban, Umaban, KettoNum, Bamei,
            KisyuRyakusyo, ChokyosiRyakusyo, BaTaijyu, Odds, Ninki,
            Honsyokin, Fukasyokin, NyusenJyuni, KakuteiJyuni, Time, ChakusaCD
        FROM N_UMA_RACE
        WHERE Year = '2023'
    """)
    print(f"  [OK] {conn.changes():,} 件の2023年データを移行しました")

    # 5. 移行後の確認
    print("\n5. 移行後の確認")
    cursor.execute("SELECT COUNT(*) FROM NL_SE_RACE_UMA WHERE Year = '2023'")
    new_2023_count = cursor.fetchone()[0]
    print(f"移行後のNL_SE_RACE_UMA 2023年データ: {new_2023_count:,} 件")

    # 6. プラダリアの2023年データ確認
    print("\n6. プラダリアの2023年データ確認")
    cursor.execute("""
        SELECT COUNT(*) FROM NL_SE_RACE_UMA 
        WHERE Bamei = 'プラダリア' AND Year = '2023'
    """)
    pradaria_2023_count = cursor.fetchone()[0]
    print(f"プラダリアの2023年データ: {pradaria_2023_count} 件")

    # 7. インデックスの作成
    print("\n7. インデックスの作成")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_nl_se_race_uma_2023 ON NL_SE_RACE_UMA (Year)")
    print("  [OK] 2023年インデックスを作成しました")

    conn.commit()
    conn.close()
    print("\n=== 修正完了 ===")
    print("NL_SE_RACE_UMAに2023年データが移行されました。")
    print("JVMonitorで2023年のデータが表示されるはずです。")

if __name__ == '__main__':
    fix_nl_se_race_uma_2023()
