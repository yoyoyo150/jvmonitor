#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
レース日付の確認スクリプト
前日予想かどうかを判定
"""

import sqlite3
import pandas as pd

def main():
    # データベース接続
    conn = sqlite3.connect('ecore.db')
    
    # 10/11, 10/12, 10/13のレースデータを確認
    dates = ['20251011', '20251012', '20251013']
    
    print("=== レース日付確認 ===")
    print("前日予想かどうかを判定します")
    print()
    
    for date in dates:
        print(f'--- {date} ---')
        
        # レース情報
        query = '''
        SELECT Year, MonthDay, JyoCD, Kaiji, Nichiji, RaceNum, Hondai, 
               MakeDate
        FROM N_RACE 
        WHERE Year = ? AND MonthDay = ?
        LIMIT 3
        '''
        
        df = pd.read_sql_query(query, conn, params=[date[:4], date[4:]])
        if not df.empty:
            print('レース情報:')
            for _, row in df.iterrows():
                race_info = f"{row['Year']}/{row['MonthDay']} {row['JyoCD']}{row['Kaiji']}{row['Nichiji']}R {row['Hondai']}"
                print(f'  {race_info}')
                print(f'    MakeDate: {row["MakeDate"]}')
                
                # 前日予想判定
                make_date = str(row['MakeDate'])
                race_date = f"{row['Year']}{row['MonthDay']}"
                
                if make_date and race_date:
                    if make_date < race_date:
                        print(f'    → 前日予想 (予想日: {make_date}, 開催日: {race_date})')
                    elif make_date == race_date:
                        print(f'    → 当日予想 (予想日: {make_date}, 開催日: {race_date})')
                    else:
                        print(f'    → 後日予想 (予想日: {make_date}, 開催日: {race_date})')
        else:
            print('レースデータなし')
        print()
    
    # 出走馬データも確認
    print("=== 出走馬データ確認 ===")
    for date in dates:
        print(f'--- {date} ---')
        
        query = '''
        SELECT COUNT(*) as count
        FROM N_UMA_RACE 
        WHERE Year = ? AND MonthDay = ?
        '''
        
        cursor = conn.cursor()
        cursor.execute(query, [date[:4], date[4:]])
        count = cursor.fetchone()[0]
        print(f'出走馬数: {count}')
        
        if count > 0:
            # サンプルデータ
            query = '''
            SELECT Umaban, KettoNum, Bamei, KakuteiJyuni, Honsyokin, Fukasyokin
            FROM N_UMA_RACE 
            WHERE Year = ? AND MonthDay = ?
            LIMIT 3
            '''
            
            df = pd.read_sql_query(query, conn, params=[date[:4], date[4:]])
            print('出走馬サンプル:')
            for _, row in df.iterrows():
                uma_info = f"{row['Umaban']}番 {row['Bamei']} (確定順位: {row['KakuteiJyuni']})"
                print(f'  {uma_info}')
                if row['Honsyokin'] and str(row['Honsyokin']).isdigit():
                    print(f'    単勝払戻: {int(row["Honsyokin"])/100:.0f}円')
                if row['Fukasyokin'] and str(row['Fukasyokin']).isdigit():
                    print(f'    複勝払戻: {int(row["Fukasyokin"])/100:.0f}円')
        print()
    
    conn.close()
    print("=== 確認完了 ===")

if __name__ == '__main__':
    main()
