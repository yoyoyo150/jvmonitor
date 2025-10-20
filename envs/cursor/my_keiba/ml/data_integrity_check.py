#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
データ整合性検証システム
予想生成前に実際のレースデータの存在を確認
"""
import sqlite3

def validate_race_exists(year, monthday, jyo_cd, race_num):
    """指定されたレースが実際に存在するかチェック"""
    conn = sqlite3.connect('ecore.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COUNT(*) FROM N_RACE 
        WHERE Year = ? AND MonthDay = ? AND JyoCD = ? AND RaceNum = ?
    """, [year, monthday, jyo_cd, race_num])
    
    count = cursor.fetchone()[0]
    conn.close()
    
    return count > 0

def validate_horse_entries(year, monthday, jyo_cd, race_num):
    """指定されたレースの出走馬データが存在するかチェック"""
    conn = sqlite3.connect('ecore.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COUNT(*) FROM N_UMA_RACE 
        WHERE Year = ? AND MonthDay = ? AND JyoCD = ? AND RaceNum = ?
    """, [year, monthday, jyo_cd, race_num])
    
    count = cursor.fetchone()[0]
    conn.close()
    
    return count

def get_valid_races_for_date(year, monthday):
    """指定日の実際に存在するレース一覧を取得"""
    conn = sqlite3.connect('ecore.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT JyoCD, RaceNum, Hondai, Kyori
        FROM N_RACE 
        WHERE Year = ? AND MonthDay = ?
        ORDER BY JyoCD, RaceNum
    """, [year, monthday])
    
    races = cursor.fetchall()
    conn.close()
    
    return races

def validate_prediction_data_integrity():
    """予想データの整合性を全体チェック"""
    print("=== 予想データ整合性チェック ===")
    
    # predictions.dbの全データをチェック
    pred_conn = sqlite3.connect('predictions.db')
    pred_cursor = pred_conn.cursor()
    
    pred_cursor.execute("""
        SELECT DISTINCT Year, MonthDay, JyoCD, RaceNum
        FROM Predictions
        ORDER BY Year, MonthDay, JyoCD, RaceNum
    """)
    
    predictions = pred_cursor.fetchall()
    pred_conn.close()
    
    invalid_count = 0
    valid_count = 0
    
    for pred in predictions:
        year, monthday, jyo_cd, race_num = pred
        
        if validate_race_exists(year, monthday, jyo_cd, race_num):
            valid_count += 1
        else:
            invalid_count += 1
            print(f"[ERROR] 存在しないレース: {year}/{monthday} 場{jyo_cd} {race_num}R")
    
    print(f"[OK] 有効な予想: {valid_count}件")
    print(f"[ERROR] 無効な予想: {invalid_count}件")
    
    return invalid_count == 0

if __name__ == "__main__":
    # 整合性チェック実行
    is_valid = validate_prediction_data_integrity()
    
    if is_valid:
        print("[OK] 全ての予想データが実際のレースと整合しています")
    else:
        print("[ERROR] 予想データに整合性の問題があります")
