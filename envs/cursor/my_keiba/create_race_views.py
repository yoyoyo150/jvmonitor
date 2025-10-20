# -*- coding: utf-8 -*-
import sqlite3
import sys
import io

# UTF-8エンコーディング設定
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def create_race_views():
    """出馬表表示用のビューを作成"""
    conn = sqlite3.connect('ecore.db')
    cursor = conn.cursor()
    
    print("=== 出馬表表示用ビューの作成 ===\n")
    
    # 1. レース基本情報ビュー
    print("1. レース基本情報ビュー (v_race_basic) を作成中...")
    cursor.execute("""
    CREATE VIEW IF NOT EXISTS v_race_basic AS
    SELECT 
        Year,
        MonthDay,
        JyoCD,
        RaceNum,
        Hondai,
        Fukudai,
        Kyori,
        HassoTime,
        TorokuTosu,
        SyussoTosu,
        TenkoCD,
        SibaBabaCD,
        DirtBabaCD,
        Honsyokin1,
        Honsyokin2,
        Honsyokin3,
        Honsyokin4,
        Honsyokin5,
        CASE JyoCD
            WHEN '01' THEN '札幌'
            WHEN '02' THEN '函館'
            WHEN '03' THEN '福島'
            WHEN '04' THEN '新潟'
            WHEN '05' THEN '東京'
            WHEN '06' THEN '中山'
            WHEN '07' THEN '中京'
            WHEN '08' THEN '京都'
            WHEN '09' THEN '阪神'
            WHEN '10' THEN '小倉'
            WHEN '50' THEN '地方競馬'
            ELSE '場' || JyoCD
        END as JyoName,
        Year || MonthDay as RaceDate,
        Year || MonthDay || JyoCD || RaceNum as RaceKey
    FROM N_RACE
    """)
    print("   [OK] レース基本情報ビューを作成しました")
    
    # 2. 出馬表ビュー
    print("2. 出馬表ビュー (v_race_horses) を作成中...")
    cursor.execute("""
    CREATE VIEW IF NOT EXISTS v_race_horses AS
    SELECT 
        u.Year,
        u.MonthDay,
        u.JyoCD,
        u.RaceNum,
        u.Wakuban,
        u.Umaban,
        u.KettoNum,
        u.Bamei,
        u.SexCD,
        u.HinsyuCD,
        u.KeiroCD,
        u.Barei,
        u.ChokyosiRyakusyo,
        u.ChokyosiCode,
        u.BanusiName,
        u.BanusiCode,
        u.Futan,
        u.KisyuRyakusyo,
        u.KisyuCode,
        u.BaTaijyu,
        u.ZogenFugo,
        u.ZogenSa,
        u.Odds,
        u.Ninki,
        u.Honsyokin,
        u.Fukasyokin,
        u.NyusenJyuni,
        u.KakuteiJyuni,
        u.Time,
        u.ChakusaCD,
        u.ChakusaCDP,
        u.ChakusaCDPP,
        u.Jyuni1c,
        u.Jyuni2c,
        u.Jyuni3c,
        u.Jyuni4c,
        u.Year || u.MonthDay || u.JyoCD || u.RaceNum as RaceKey,
        u.Year || u.MonthDay as RaceDate
    FROM N_UMA_RACE u
    """)
    print("   [OK] 出馬表ビューを作成しました")
    
    # 3. 統合出馬表ビュー
    print("3. 統合出馬表ビュー (v_race_complete) を作成中...")
    cursor.execute("""
    CREATE VIEW IF NOT EXISTS v_race_complete AS
    SELECT 
        r.Year,
        r.MonthDay,
        r.JyoCD,
        r.RaceNum,
        r.Hondai,
        r.Fukudai,
        r.Kyori,
        r.HassoTime,
        r.TorokuTosu,
        r.SyussoTosu,
        r.TenkoCD,
        r.SibaBabaCD,
        r.DirtBabaCD,
        r.JyoName,
        r.RaceDate,
        r.RaceKey,
        u.Wakuban,
        u.Umaban,
        u.KettoNum,
        u.Bamei,
        u.SexCD,
        u.HinsyuCD,
        u.KeiroCD,
        u.Barei,
        u.ChokyosiRyakusyo,
        u.ChokyosiCode,
        u.BanusiName,
        u.BanusiCode,
        u.Futan,
        u.KisyuRyakusyo,
        u.KisyuCode,
        u.BaTaijyu,
        u.ZogenFugo,
        u.ZogenSa,
        u.Odds,
        u.Ninki,
        u.Honsyokin,
        u.Fukasyokin,
        u.NyusenJyuni,
        u.KakuteiJyuni,
        u.Time,
        u.ChakusaCD,
        u.ChakusaCDP,
        u.ChakusaCDPP,
        u.Jyuni1c,
        u.Jyuni2c,
        u.Jyuni3c,
        u.Jyuni4c
    FROM v_race_basic r
    LEFT JOIN v_race_horses u ON r.RaceKey = u.RaceKey
    """)
    print("   [OK] 統合出馬表ビューを作成しました")
    
    # 4. 騎手情報ビュー
    print("4. 騎手情報ビュー (v_jockey_info) を作成中...")
    cursor.execute("""
    CREATE VIEW IF NOT EXISTS v_jockey_info AS
    SELECT 
        KisyuCode,
        KisyuRyakusyo,
        KisyuName,
        BirthDate,
        DelKubun,
        RegDate,
        DelDate
    FROM N_KISYU
    """)
    print("   [OK] 騎手情報ビューを作成しました")
    
    # 5. 調教師情報ビュー
    print("5. 調教師情報ビュー (v_trainer_info) を作成中...")
    cursor.execute("""
    CREATE VIEW IF NOT EXISTS v_trainer_info AS
    SELECT 
        ChokyosiCode,
        ChokyosiRyakusyo,
        ChokyosiName,
        BirthDate,
        DelKubun,
        RegDate,
        DelDate
    FROM N_CHOKYO
    """)
    print("   [OK] 調教師情報ビューを作成しました")
    
    # 6. 馬情報ビュー
    print("6. 馬情報ビュー (v_horse_info) を作成中...")
    cursor.execute("""
    CREATE VIEW IF NOT EXISTS v_horse_info AS
    SELECT 
        KettoNum,
        Bamei,
        BameiKana,
        BameiEng,
        BirthDate,
        SexCD,
        HinsyuCD,
        KeiroCD,
        UmaKigoCD,
        ChokyosiCode,
        ChokyosiRyakusyo,
        BanusiCode,
        BanusiName,
        BreederCode,
        BreederName,
        SanchiName
    FROM N_UMA
    """)
    print("   [OK] 馬情報ビューを作成しました")
    
    # 7. 統計情報ビュー
    print("7. 統計情報ビュー (v_race_stats) を作成中...")
    cursor.execute("""
    CREATE VIEW IF NOT EXISTS v_race_stats AS
    SELECT 
        Year,
        MonthDay,
        JyoCD,
        JyoName,
        COUNT(DISTINCT RaceNum) as RaceCount,
        COUNT(*) as HorseCount,
        AVG(CAST(Kyori AS INTEGER)) as AvgDistance,
        MIN(HassoTime) as FirstRaceTime,
        MAX(HassoTime) as LastRaceTime
    FROM v_race_complete
    WHERE Kyori != '' AND Kyori != '0000'
    GROUP BY Year, MonthDay, JyoCD, JyoName
    """)
    print("   [OK] 統計情報ビューを作成しました")
    
    # ビューの確認
    print("\n=== 作成されたビューの確認 ===")
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='view' AND name LIKE 'v_%'
        ORDER BY name
    """)
    views = cursor.fetchall()
    
    for view in views:
        print(f"  [OK] {view[0]}")
    
    # サンプルデータの確認
    print("\n=== サンプルデータの確認 ===")
    cursor.execute("SELECT COUNT(*) FROM v_race_basic")
    race_count = cursor.fetchone()[0]
    print(f"レース基本情報: {race_count:,} 件")
    
    cursor.execute("SELECT COUNT(*) FROM v_race_horses")
    horse_count = cursor.fetchone()[0]
    print(f"出馬情報: {horse_count:,} 件")
    
    cursor.execute("SELECT COUNT(*) FROM v_race_complete")
    complete_count = cursor.fetchone()[0]
    print(f"統合出馬表: {complete_count:,} 件")
    
    conn.commit()
    conn.close()
    
    print("\n=== ビュー作成完了 ===")
    print("出馬表表示システムで利用可能なビューが作成されました。")

if __name__ == "__main__":
    create_race_views()
