import sqlite3
import pandas as pd
from datetime import datetime

def verify_prediction_dates():
    """10/11, 10/12, 10/13の予想作成可能性を検証"""
    
    target_dates = ['20251011', '20251012', '20251013']
    
    print("=== 予想作成可能性検証 ===")
    print(f"対象日付: {', '.join(target_dates)}")
    print()
    
    # ecore.dbの確認
    conn = sqlite3.connect('ecore.db')
    cursor = conn.cursor()
    
    print("【1. レースデータ確認】")
    for date in target_dates:
        print(f"\n--- {date} ---")
        
        # N_RACEテーブルでレース情報確認
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM N_RACE 
                WHERE MakeDate = ? AND Year = ? AND MonthDay = ?
            """, (date, date[:4], date[4:]))
            race_count = cursor.fetchone()[0]
            print(f"レース数: {race_count}")
            
            if race_count > 0:
                # レース詳細情報
                cursor.execute("""
                    SELECT Year, MonthDay, JyoCD, Kaiji, Nichiji, RaceNum, 
                           RaceName, GradeCD, Distance, TrackCD, CourseCD
                    FROM N_RACE 
                    WHERE MakeDate = ? AND Year = ? AND MonthDay = ?
                    ORDER BY JyoCD, Kaiji, Nichiji, RaceNum
                """, (date, date[:4], date[4:]))
                
                races = cursor.fetchall()
                for race in races[:5]:  # 最初の5レースのみ表示
                    print(f"  {race[0]}/{race[1]} {race[2]}{race[3]}{race[4]}R {race[6]} ({race[7]}) {race[8]}m")
                
                if len(races) > 5:
                    print(f"  ... 他{len(races)-5}レース")
                    
        except Exception as e:
            print(f"レースデータ取得エラー: {e}")
    
    print("\n【2. 出走馬データ確認】")
    for date in target_dates:
        print(f"\n--- {date} ---")
        
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM N_UMA_RACE 
                WHERE MakeDate = ? AND Year = ? AND MonthDay = ?
            """, (date, date[:4], date[4:]))
            uma_count = cursor.fetchone()[0]
            print(f"出走馬数: {uma_count}")
            
            if uma_count > 0:
                # 出走馬のサンプル
                cursor.execute("""
                    SELECT UmaCD, UmaName, JyoCD, Kaiji, Nichiji, RaceNum, Umaban
                    FROM N_UMA_RACE 
                    WHERE MakeDate = ? AND Year = ? AND MonthDay = ?
                    ORDER BY JyoCD, Kaiji, Nichiji, RaceNum, Umaban
                    LIMIT 10
                """, (date, date[:4], date[4:]))
                
                umas = cursor.fetchall()
                for uma in umas:
                    print(f"  {uma[1]} ({uma[6]}番)")
                    
        except Exception as e:
            print(f"出走馬データ取得エラー: {e}")
    
    print("\n【3. 馬印データ確認】")
    conn.close()
    conn = sqlite3.connect('excel_data.db')
    cursor = conn.cursor()
    
    for date in target_dates:
        print(f"\n--- {date} ---")
        
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM HORSE_MARKS 
                WHERE SourceDate = ?
            """, (date,))
            mark_count = cursor.fetchone()[0]
            print(f"馬印データ数: {mark_count}")
            
            if mark_count > 0:
                # 馬印のサンプル
                cursor.execute("""
                    SELECT HorseName, Mark1, Mark2, Mark3, Mark4, Mark5
                    FROM HORSE_MARKS 
                    WHERE SourceDate = ?
                    LIMIT 5
                """, (date,))
                
                marks = cursor.fetchall()
                for mark in marks:
                    print(f"  {mark[0]}: {mark[1]}, {mark[2]}, {mark[3]}, {mark[4]}, {mark[5]}")
                    
        except Exception as e:
            print(f"馬印データ取得エラー: {e}")
    
    conn.close()
    
    print("\n【4. 予想作成可能性判定】")
    print("必要なデータ:")
    print("- レース情報: レース名、距離、コース、グレード")
    print("- 出走馬情報: 馬名、騎手、調教師、負担重量")
    print("- 馬印データ: 各馬の評価マーク")
    print("- 過去成績: 過去のレース結果")
    print("- 調教データ: 最新の調教情報")

if __name__ == "__main__":
    verify_prediction_dates()








