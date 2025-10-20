#!/usr/bin/env python3
"""ExcelまたはParquetから馬印を検索するユーティリティ"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SQLite の HORSE_MARKS テーブルから馬印を検索する")
    parser.add_argument("--db", default="ecore.db", help="SQLite データベースのパス (デフォルト: ecore.db)")
    parser.add_argument("--horse-name", help="馬名 (部分一致)")
    parser.add_argument("--source-date", help="開催日 (YYYYMMDD)")
    parser.add_argument("--jyo-cd", help="競馬場コード (例: 01=札幌, 05=東京)")
    parser.add_argument("--race-num", help="レース番号")
    parser.add_argument("--umaban", help="馬番")
    parser.add_argument("--limit", type=int, help="取得する結果の最大件数")
    return parser.parse_args()

def main() -> int:
    args = parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    db_path = Path(args.db)
    if not db_path.exists():
        print(f"エラー: データベースファイルが見つかりません: {db_path}", file=sys.stderr)
        return 1

    conn = sqlite3.connect(db_path)
    try:
        query_parts = []
        params = []

        if args.horse_name:
            query_parts.append("NormalizedHorseName LIKE ?")
            params.append(f"%{''.join(args.horse_name.split())}%")

        if args.source_date:
            query_parts.append("SourceDate = ?")
            params.append(args.source_date)
            
        if args.jyo_cd:
            query_parts.append("JyoCD = ?")
            params.append(args.jyo_cd)

        if args.race_num:
            query_parts.append("RaceNum = ?")
            params.append(args.race_num)

        if args.umaban:
            query_parts.append("Umaban = ?")
            params.append(args.umaban)

        if not query_parts:
            where_clause = "1=1"
        else:
            where_clause = " AND ".join(query_parts)
        
        # 全ての列を取得するが、表示順序を調整
        select_columns = [
            "SourceDate", "HorseName", "TrainerName", "RaceId", "RaceName", 
            "JyoCD", "Kaiji", "Nichiji", "RaceNum", "Umaban", 
            "MorningOdds", "Mark1", "Mark2", "Mark3", "Mark4", 
            "Mark5", "Mark6", "Mark7", "Mark8", "SourceFile", "ImportedAt",
            "ZI_INDEX", "ZM_VALUE", "SHIBA_DA", "KYORI_M", "R_MARK1", "R_MARK2", "R_MARK3",
            "RACE_CLASS_C", "CHAKU", "SEX", "AGE", "JOCKEY", "KINRYO", "PREV_KYAKUSHITSU",
            "PREV_MARK1", "PREV_MARK2", "PREV_MARK3", "PREV_MARK4", "PREV_MARK5", "PREV_MARK6", "PREV_MARK7", "PREV_MARK8",
            "PREV_NINKI", "INDEX_RANK1", "ACCEL_VAL", "INDEX_RANK2", "INDEX_DIFF2", "ORIGINAL_VAL",
            "INDEX_RANK3", "INDEX_RANK4", "PREV_CHAKU_JUNI", "PREV_CHAKU_SA", "TANSHO_ODDS", "FUKUSHO_ODDS",
            "INDEX_DIFF4", "INDEX_DIFF1", "PREV_TSUKA1", "PREV_TSUKA2", "PREV_TSUKA3", "PREV_TSUKA4",
            "PREV_3F_JUNI", "PREV_TOSU", "PREV_RACE_MARK", "PREV_RACE_MARK2", "PREV_RACE_MARK3",
            "FATHER_TYPE_NAME", "TOTAL_HORSES", "WORK1", "WORK2", "PREV_TRACK_NAME", "SAME_TRACK_FLAG",
            "PREV_KINRYO", "PREV_BATAIJU", "PREV_BATAIJU_ZOGEN", "AGE_AT_RACE", "INTERVAL", "KYUMEI_SENME",
            "KINRYO_SA", "KYORI_SA", "PREV_SHIBA_DA", "PREV_KYORI_M", "CAREER_TOTAL", "CAREER_LATEST",
            "CLASS_C", "PREV_UMABAN", "CURRENT_SHIBA_DA", "PREV_BABA_JOTAI", "PREV_CLASS", "DAMSIRE_TYPE_NAME",
            "T_MARK_DIFF", "MATCHUP_MINING_VAL", "MATCHUP_MINING_RANK", "KOKYUSEN_FLAG", "B_COL_FLAG", "SYOZOKU",
            "CHECK_TRAINER_TYPE", "CHECK_JOCKEY_TYPE", "TRAINER_NAME", "FUKUSHO_ODDS_LOWER", "FUKUSHO_ODDS_UPPER",
            "TAN_ODDS", "WAKUBAN", "COURSE_GROUP_COUNT", "COURSE_GROUP_NAME1", "NINKI_RANK", "NORIKAE_FLAG", "PREV_RACE_ID",
            "ZI_RANK", # 新しく追加したZI指数の順位
        ]
        
        sql = f"SELECT {', '.join(select_columns)} FROM HORSE_MARKS WHERE {where_clause} ORDER BY SourceDate DESC, ImportedAt DESC"
        if args.limit:
            sql += " LIMIT ?"
            params.append(args.limit)
        
        cursor = conn.execute(sql, params)
        results = cursor.fetchall()

        if not results:
            print("該当する馬印データは見つかりませんでした。")
            return 0
        
        # ヘッダー表示
        print("\n--- 検索結果 ---")
        header = "| " + " | ".join(select_columns) + " |"
        print(header)
        print("|-" + "-|-".join(["-" * len(col) for col in select_columns]) + "-|")

        # 結果表示
        for row in results:
            formatted_row = []
            for i, col_val in enumerate(row):
                # 出力を見やすくするため、各列の最大幅に合わせて調整
                formatted_row.append(str(col_val))
            print("| " + " | ".join(formatted_row) + " |")
        
        print(f"\n合計 {len(results)} 件のデータが見つかりました。")
    return 0

    except sqlite3.Error as e:
        print(f"データベースエラー: {e}", file=sys.stderr)
        return 1
    finally:
        conn.close()

if __name__ == "__main__":
    raise SystemExit(main())
