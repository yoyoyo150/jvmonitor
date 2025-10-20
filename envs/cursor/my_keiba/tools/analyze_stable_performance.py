import sqlite3
import pandas as pd
import sys
from pathlib import Path

def analyze_stable_performance(db_path: Path):
    print(f"厩舎分析を開始します: {db_path}")
    conn = None
    try:
        conn = sqlite3.connect(db_path)

        # DEBUG: HORSE_MARKSテーブルの列を確認
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(HORSE_MARKS);")
        print("--- HORSE_MARKS Columns ---")
        for col_info in cursor.fetchall():
            print(f"  {col_info[1]} ({col_info[2]})")

        cursor.execute("PRAGMA table_info(N_UMA_RACE);")
        print("--- N_UMA_RACE Columns ---")
        for col_info in cursor.fetchall():
            print(f"  {col_info[1]} ({col_info[2]})")
        print("--------------------------")

        # SQL: 調教師名は COALESCE(HM.TrainerName, HM.TRAINER_NAME) を使用
        # 馬名は正規化（空白・全角空白除去）して結合
        sql_query = """
        SELECT
            COALESCE(HM.TrainerName, HM.TRAINER_NAME) AS TrainerName,
            HM.Mark5,
            HM.Mark6,
            CASE
                WHEN NUL.KakuteiJyuni GLOB '[0-9]*' THEN CAST(NUL.KakuteiJyuni AS INTEGER)
                ELSE NULL
            END AS FinishOrder
        FROM HORSE_MARKS AS HM
        INNER JOIN N_UMA_RACE AS NUL
            ON HM.SourceDate = (NUL.Year || NUL.MonthDay)
            AND HM.NormalizedHorseName = REPLACE(REPLACE(NUL.Bamei, ' ', ''), '　', '')
        WHERE
            COALESCE(HM.TrainerName, HM.TRAINER_NAME) IS NOT NULL AND COALESCE(HM.TrainerName, HM.TRAINER_NAME) != '' AND
            HM.Mark5 IS NOT NULL AND HM.Mark5 != '' AND
            HM.Mark6 IS NOT NULL AND HM.Mark6 != '' AND
            FinishOrder IS NOT NULL;
        """

        df = pd.read_sql_query(sql_query, conn)
        print(f"DEBUG: Initial DataFrame shape: {df.shape}")
        if not df.empty:
            print(f"DEBUG: Initial DataFrame head:\n{df.head()}")

        if df.empty:
            print("分析対象のデータが見つかりませんでした。(SQLクエリ後)")
            return

        # Mark5とMark6を数値に変換 (変換できない値はNaNにする)
        df['Mark5_Num'] = pd.to_numeric(df['Mark5'], errors='coerce')
        df['Mark6_Num'] = pd.to_numeric(df['Mark6'], errors='coerce')
        print(f"DEBUG: After to_numeric, DataFrame shape: {df.shape}")
        if not df.empty:
            print(f"DEBUG: After to_numeric, DataFrame head:\n{df.head()}")

        # NaNを除外
        df.dropna(subset=['Mark5_Num', 'Mark6_Num', 'FinishOrder', 'TrainerName'], inplace=True)
        print(f"DEBUG: After dropna, DataFrame shape: {df.shape}")
        if not df.empty:
            print(f"DEBUG: After dropna, DataFrame head:\n{df.head()}")

        if df.empty:
            print("数値変換後、分析対象のデータが見つかりませんでした。(dropna後)")
            return

        # 複勝判定 (1着, 2着, 3着を成功とする)
        df['IsPlace'] = df['FinishOrder'] <= 3
        print(f"DEBUG: After IsPlace, DataFrame shape: {df.shape}")
        if not df.empty:
            print(f"DEBUG: After IsPlace, DataFrame head:\n{df.head()}")

        # 厩舎ごとに集計
        grouped = df.groupby('TrainerName').agg(
            AvgMark5=('Mark5_Num', 'mean'),
            AvgMark6=('Mark6_Num', 'mean'),
            PlaceWins=('IsPlace', 'sum'),
            TotalRaces=('TrainerName', 'count')
        ).reset_index()

        # ベイズ収縮（ベータ事前分布 α0, β0）
        # 初期値: 事前複勝率 30% 程度（α0=3, β0=7）
        alpha0, beta0 = 3.0, 7.0
        grouped['PlaceRate_raw'] = (grouped['PlaceWins'] / grouped['TotalRaces']) * 100.0
        grouped['PlaceRate_shrunk'] = ((grouped['PlaceWins'] + alpha0) / (grouped['TotalRaces'] + alpha0 + beta0)) * 100.0

        # 最低出走数の閾値
        min_races = 5
        grouped = grouped[grouped['TotalRaces'] >= min_races]
        print(f"DEBUG: After min_races filter, grouped shape: {grouped.shape}")
        if not grouped.empty:
            print(f"DEBUG: After min_races filter, head:\n{grouped.head()}")
        
        # 並び替え: Mark5/6が低いほど良く、収縮後複勝率が高いほど良い
        grouped = grouped.sort_values(
            by=['AvgMark5', 'AvgMark6', 'PlaceRate_shrunk'],
            ascending=[True, True, False]
        )

        # 上位を表示
        print("\n--- 厩舎分析結果 (Mark5/Mark6低 + 収縮後複勝率高) 上位30 ---")
        cols = ['TrainerName', 'TotalRaces', 'AvgMark5', 'AvgMark6', 'PlaceWins', 'PlaceRate_raw', 'PlaceRate_shrunk']
        print(grouped[cols].head(30).to_string(index=False, formatters={
            'AvgMark5': '{:.2f}'.format,
            'AvgMark6': '{:.2f}'.format,
            'PlaceRate_raw': '{:.2f}'.format,
            'PlaceRate_shrunk': '{:.2f}'.format,
        }))

    except sqlite3.Error as e:
        print(f"データベースエラー: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"分析中にエラーが発生しました: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if conn:
            conn.close()

def main() -> int:
    db_path = Path("ecore.db") # Assuming ecore.db is in the current directory
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    analyze_stable_performance(db_path)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
