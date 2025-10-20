# -*- coding: utf-8 -*-
import sqlite3
import sys
import io

# UTF-8エンコーディング設定
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def fix_jvmonitor_database():
    """JVMonitorのデータベースエラーを修正"""
    conn = sqlite3.connect('ecore.db')
    cursor = conn.cursor()
    
    print("=== JVMonitorデータベースエラー修正 ===\n")
    
    # 1. 不足しているテーブルの確認
    print("1. 不足しているテーブルの確認")
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name LIKE '%SE_RACE_UMA%'
    """)
    se_tables = cursor.fetchall()
    print(f"SE_RACE_UMA関連テーブル: {len(se_tables)} 件")
    
    # 2. 速報系テーブルの状況確認
    print("\n2. 速報系テーブルの状況確認")
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name LIKE 'S_%'
        ORDER BY name
    """)
    s_tables = cursor.fetchall()
    
    print("速報系テーブル一覧:")
    for table in s_tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"  {table[0]}: {count:,} 件")
    
    # 3. 不足しているテーブルの作成
    print("\n3. 不足しているテーブルの作成")
    
    # NL_SE_RACE_UMAテーブルの作成
    create_nl_se_race_uma = """
    CREATE TABLE IF NOT EXISTS NL_SE_RACE_UMA (
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
    """
    
    try:
        cursor.execute(create_nl_se_race_uma)
        print("  [OK] NL_SE_RACE_UMAテーブルを作成しました")
    except Exception as e:
        print(f"  [ERROR] NL_SE_RACE_UMAテーブル作成エラー: {e}")
    
    # 4. データの移行
    print("\n4. データの移行")
    try:
        # N_UMA_RACEからNL_SE_RACE_UMAにデータを移行
        cursor.execute("""
            INSERT OR REPLACE INTO NL_SE_RACE_UMA 
            SELECT 
                Year,
                MonthDay,
                JyoCD,
                RaceNum,
                Wakuban,
                Umaban,
                KettoNum,
                Bamei,
                KisyuRyakusyo,
                ChokyosiRyakusyo,
                BaTaijyu,
                Odds,
                Ninki,
                Honsyokin,
                Fukasyokin,
                NyusenJyuni,
                KakuteiJyuni,
                Time,
                ChakusaCD
            FROM N_UMA_RACE
            WHERE Year >= '2024'
        """)
        
        moved_count = cursor.rowcount
        print(f"  [OK] {moved_count:,} 件のデータを移行しました")
        
    except Exception as e:
        print(f"  [ERROR] データ移行エラー: {e}")
    
    # 5. インデックスの作成
    print("\n5. インデックスの作成")
    try:
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_nl_se_race_uma_date 
            ON NL_SE_RACE_UMA (Year, MonthDay)
        """)
        print("  [OK] 日付インデックスを作成しました")
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_nl_se_race_uma_race 
            ON NL_SE_RACE_UMA (Year, MonthDay, JyoCD, RaceNum)
        """)
        print("  [OK] レースインデックスを作成しました")
        
    except Exception as e:
        print(f"  [ERROR] インデックス作成エラー: {e}")
    
    # 6. データの確認
    print("\n6. データの確認")
    cursor.execute("SELECT COUNT(*) FROM NL_SE_RACE_UMA")
    nl_count = cursor.fetchone()[0]
    print(f"NL_SE_RACE_UMA: {nl_count:,} 件")
    
    cursor.execute("SELECT COUNT(*) FROM N_UMA_RACE WHERE Year >= '2024'")
    n_count = cursor.fetchone()[0]
    print(f"N_UMA_RACE (2024年以降): {n_count:,} 件")
    
    # 7. 最新データの確認
    print("\n7. 最新データの確認")
    cursor.execute("""
        SELECT MAX(Year || MonthDay) FROM NL_SE_RACE_UMA
    """)
    latest_date = cursor.fetchone()[0]
    print(f"最新データ日: {latest_date}")
    
    conn.commit()
    conn.close()
    
    print("\n=== 修正完了 ===")
    print("JVMonitorのデータベースエラーが修正されました。")
    print("NL_SE_RACE_UMAテーブルが作成され、データが移行されました。")

if __name__ == "__main__":
    fix_jvmonitor_database()


