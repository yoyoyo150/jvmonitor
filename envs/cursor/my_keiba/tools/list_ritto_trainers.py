#!/usr/bin/env python3
"""
栗東の調教師一覧表示スクリプト
データベースの登録状況を確認する
"""

import sqlite3
import pandas as pd
import sys
from pathlib import Path

def list_ritto_trainers(db_path: Path) -> None:
    """栗東の調教師一覧を表示"""
    print("=== 栗東の調教師一覧 ===")
    
    conn = sqlite3.connect(db_path)
    try:
        # 栗東の調教師を抽出（TRAINER_NAME列を使用）
        sql = """
        SELECT 
            TRAINER_NAME,
            COUNT(*) as race_count,
            COUNT(DISTINCT SourceDate) as race_days,
            MIN(SourceDate) as first_race,
            MAX(SourceDate) as last_race
        FROM HORSE_MARKS 
        WHERE TRAINER_NAME IS NOT NULL 
        AND TRAINER_NAME != ''
        GROUP BY TRAINER_NAME
        ORDER BY race_count DESC
        """
        
        df = pd.read_sql_query(sql, conn)
        
        if df.empty:
            print("栗東の調教師データが見つかりません。")
            return
            
        print(f"調教師数: {len(df)}")
        print("\n--- 調教師一覧 ---")
        print(df.to_string(index=False, formatters={
            'race_count': '{:>6}'.format,
            'race_days': '{:>6}'.format,
            'first_race': '{:>8}'.format,
            'last_race': '{:>8}'.format
        }))
        
        # 統計情報
        print(f"\n--- 統計情報 ---")
        print(f"総調教師数: {len(df)}")
        print(f"平均レース数: {df['race_count'].mean():.1f}")
        print(f"最多レース数: {df['race_count'].max()}")
        print(f"最少レース数: {df['race_count'].min()}")
        
        # 上位10名
        print(f"\n--- レース数上位10名 ---")
        top10 = df.head(10)
        print(top10[['TRAINER_NAME', 'race_count', 'race_days']].to_string(index=False, formatters={
            'race_count': '{:>6}'.format,
            'race_days': '{:>6}'.format
        }))
        
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
    
    list_ritto_trainers(db_path)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())





