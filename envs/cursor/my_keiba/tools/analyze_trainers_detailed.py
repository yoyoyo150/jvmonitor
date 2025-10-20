#!/usr/bin/env python3
"""
調教師詳細分析スクリプト
JVMonitorのような詳細な調教師分析を表示
"""

import sqlite3
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

def analyze_trainers_detailed(db_path: Path, target_dates: list[str] = None) -> None:
    """調教師の詳細分析を実行"""
    print("=== 調教師詳細分析 ===")
    
    conn = sqlite3.connect(db_path)
    try:
        # 対象期間の指定
        if target_dates:
            date_filter = f"AND HM.SourceDate IN ({','.join(['?' for _ in target_dates])})"
            params = target_dates
        else:
            date_filter = ""
            params = []
        
        # 調教師の詳細分析クエリ（馬名正規化処理を追加）
        sql = f"""
        SELECT 
            HM.TRAINER_NAME as TrainerName,
            COUNT(*) as TotalRaces,
            COUNT(DISTINCT HM.SourceDate) as RaceDays,
            COUNT(CASE WHEN NUL.KakuteiJyuni = '1' THEN 1 END) as Wins,
            COUNT(CASE WHEN NUL.KakuteiJyuni IN ('1', '2') THEN 1 END) as Places,
            COUNT(CASE WHEN NUL.KakuteiJyuni IN ('1', '2', '3') THEN 1 END) as Shows,
            COUNT(CASE WHEN NUL.KakuteiJyuni IN ('1', '2', '3') THEN 1 END) * 100.0 / COUNT(*) as ShowRate,
            COUNT(CASE WHEN NUL.KakuteiJyuni IN ('1', '2') THEN 1 END) * 100.0 / COUNT(*) as PlaceRate,
            COUNT(CASE WHEN NUL.KakuteiJyuni = '1' THEN 1 END) * 100.0 / COUNT(*) as WinRate,
            AVG(CASE WHEN NUL.KakuteiJyuni GLOB '[0-9]*' THEN CAST(NUL.KakuteiJyuni AS INTEGER) END) as AvgFinish,
            SUM(CASE WHEN NUL.KakuteiJyuni = '1' THEN 1 ELSE 0 END) as WinCount,
            SUM(CASE WHEN NUL.KakuteiJyuni IN ('1', '2') THEN 1 ELSE 0 END) as PlaceCount,
            SUM(CASE WHEN NUL.KakuteiJyuni IN ('1', '2', '3') THEN 1 ELSE 0 END) as ShowCount,
            AVG(CAST(HM.Mark5 AS REAL)) as AvgMark5,
            AVG(CAST(HM.Mark6 AS REAL)) as AvgMark6,
            MIN(HM.SourceDate) as FirstRace,
            MAX(HM.SourceDate) as LastRace
        FROM HORSE_MARKS AS HM
        LEFT JOIN N_UMA_RACE AS NUL
            ON HM.SourceDate = (NUL.Year || NUL.MonthDay)
            AND REPLACE(REPLACE(REPLACE(HM.HorseName, ' ', ''), '　', ''), '・', '') = 
                REPLACE(REPLACE(REPLACE(NUL.Bamei, ' ', ''), '　', ''), '・', '')
        WHERE HM.TRAINER_NAME IS NOT NULL 
        AND HM.TRAINER_NAME != ''
        {date_filter}
        GROUP BY HM.TRAINER_NAME
        HAVING COUNT(*) >= 5
        ORDER BY ShowRate DESC, TotalRaces DESC
        """
        
        df = pd.read_sql_query(sql, conn, params=params)
        
        if df.empty:
            print("調教師データが見つかりません。")
            return
            
        print(f"分析対象調教師数: {len(df)}")
        print(f"分析期間: {df['FirstRace'].min()} ～ {df['LastRace'].max()}")
        
        # 結果を整形して表示
        print("\n" + "="*120)
        print("調教師詳細分析結果")
        print("="*120)
        
        # ヘッダー
        header = f"{'順位':>3} {'調教師':<12} {'レース数':>6} {'複勝率':>6} {'連対率':>6} {'勝率':>6} {'平均着順':>6} {'Mark5':>6} {'Mark6':>6} {'初回':>8} {'最終':>8}"
        print(header)
        print("-" * 120)
        
        # データ行
        for i, (_, row) in enumerate(df.head(50).iterrows(), 1):
            trainer_name = row['TrainerName'][:10] if len(row['TrainerName']) > 10 else row['TrainerName']
            line = f"{i:>3} {trainer_name:<12} {row['TotalRaces']:>6} {row['ShowRate']:>5.1f}% {row['PlaceRate']:>5.1f}% {row['WinRate']:>5.1f}% {row['AvgFinish']:>6.1f} {row['AvgMark5']:>6.1f} {row['AvgMark6']:>6.1f} {row['FirstRace']:>8} {row['LastRace']:>8}"
            print(line)
        
        # 統計情報
        print("\n" + "="*60)
        print("統計情報")
        print("="*60)
        print(f"総調教師数: {len(df)}")
        print(f"平均レース数: {df['TotalRaces'].mean():.1f}")
        print(f"平均複勝率: {df['ShowRate'].mean():.1f}%")
        print(f"平均連対率: {df['PlaceRate'].mean():.1f}%")
        print(f"平均勝率: {df['WinRate'].mean():.1f}%")
        
        # 上位10名の詳細
        print("\n" + "="*80)
        print("上位10名詳細")
        print("="*80)
        top10 = df.head(10)
        for i, (_, row) in enumerate(top10.iterrows(), 1):
            print(f"\n{i}. {row['TrainerName']}")
            print(f"   レース数: {row['TotalRaces']} (開催日数: {row['RaceDays']})")
            print(f"   複勝率: {row['ShowRate']:.1f}% ({row['ShowCount']}/{row['TotalRaces']})")
            print(f"   連対率: {row['PlaceRate']:.1f}% ({row['PlaceCount']}/{row['TotalRaces']})")
            print(f"   勝率: {row['WinRate']:.1f}% ({row['WinCount']}/{row['TotalRaces']})")
            print(f"   平均着順: {row['AvgFinish']:.1f}")
            print(f"   平均Mark5: {row['AvgMark5']:.1f}, 平均Mark6: {row['AvgMark6']:.1f}")
        
        # CSV出力
        output_file = Path('outputs') / 'trainer_analysis.csv'
        output_file.parent.mkdir(exist_ok=True)
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n詳細データをCSV出力: {output_file}")
        
    except sqlite3.Error as e:
        print(f"データベースエラー: {e}", file=sys.stderr)
    finally:
        conn.close()

def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    
    db_path = Path("ecore.db")
    if not db_path.exists():
        print(f"エラー: DBが見つかりません: {db_path}", file=sys.stderr)
        return 1
    
    # 9/13～27の期間で分析
    target_dates = [
        "20250913", "20250914", "20250915", "20250916", "20250917", 
        "20250918", "20250919", "20250920", "20250921", "20250922", 
        "20250923", "20250924", "20250925", "20250926", "20250927"
    ]
    
    analyze_trainers_detailed(db_path, target_dates)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
