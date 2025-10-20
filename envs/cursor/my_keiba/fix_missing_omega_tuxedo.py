import sqlite3
import sys
import io
import pandas as pd
import os
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

DB_PATH = 'ecore.db'
YDATE_DIR = r"C:\my_project_folder\envs\cursor\my_keiba\yDate"

def fix_missing_omega_tuxedo():
    print("=== オメガタキシードの2025年5月3日データの緊急修正 ===\n")

    # 1. 画面情報に基づいて手動でデータを挿入
    print("1. 画面情報に基づいて手動でデータを挿入")
    
    # 画面から確認できる情報
    horse_data = {
        'SourceDate': '20250503',
        'HorseName': 'オメガタキシード',
        'NormalizedHorseName': 'オメガタキシード',
        'JOCKEY': '戸崎圭太',
        'KINRYO': '58',
        'KYORI_M': '2100',
        'SHIBA_DA': 'ダ',
        'CHAKU': '3',  # 3着
        'TANSHO_ODDS': '53.2',
        'FUKUSHO_ODDS': '0',  # 画面からは不明
        'TOTAL_HORSES': '16',
        'SEX': '騙',
        'AGE': '5',
        'TRAINER_NAME': '井上智史',
        'SourceFile': '20250503_manual.xlsx',
        'ImportedAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 既存データを削除（念のため）
        cursor.execute("DELETE FROM HORSE_MARKS WHERE SourceDate = '20250503' AND HorseName = 'オメガタキシード'")
        
        # 新しいデータを挿入
        cursor.execute("""
            INSERT INTO HORSE_MARKS (
                SourceDate, HorseName, NormalizedHorseName, JOCKEY, KINRYO, KYORI_M, SHIBA_DA,
                CHAKU, TANSHO_ODDS, FUKUSHO_ODDS, TOTAL_HORSES, SEX, AGE, TRAINER_NAME,
                SourceFile, ImportedAt
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            horse_data['SourceDate'],
            horse_data['HorseName'],
            horse_data['NormalizedHorseName'],
            horse_data['JOCKEY'],
            horse_data['KINRYO'],
            horse_data['KYORI_M'],
            horse_data['SHIBA_DA'],
            horse_data['CHAKU'],
            horse_data['TANSHO_ODDS'],
            horse_data['FUKUSHO_ODDS'],
            horse_data['TOTAL_HORSES'],
            horse_data['SEX'],
            horse_data['AGE'],
            horse_data['TRAINER_NAME'],
            horse_data['SourceFile'],
            horse_data['ImportedAt']
        ))
        
        conn.commit()
        print("✅ オメガタキシードの2025年5月3日データを手動で挿入しました")
        
        # 2. 挿入されたデータを確認
        print("\n2. 挿入されたデータを確認")
        cursor.execute("""
            SELECT SourceDate, HorseName, JOCKEY, KINRYO, CHAKU, TANSHO_ODDS, ImportedAt
            FROM HORSE_MARKS 
            WHERE SourceDate = '20250503' AND HorseName = 'オメガタキシード'
        """)
        
        inserted_data = cursor.fetchone()
        if inserted_data:
            date, name, jockey, kinryo, chaku, odds, imported_at = inserted_data
            print(f"挿入されたデータ:")
            print(f"  日付: {date}")
            print(f"  馬名: {name}")
            print(f"  騎手: {jockey}")
            print(f"  斤量: {kinryo}")
            print(f"  着順: {chaku}")
            print(f"  オッズ: {odds}")
            print(f"  インポート時刻: {imported_at}")
        else:
            print("❌ データの挿入に失敗しました")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ データ挿入エラー: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

    # 3. 問題の根本原因調査
    print("\n3. 問題の根本原因調査")
    print("画面では2025年5月3日に3着で出走していることが確認されていますが、")
    print("データベースとExcelファイルに該当データが存在しません。")
    print("\n考えられる原因:")
    print("1. Excelファイルの作成時にオメガタキシードのデータが漏れている")
    print("2. データのインポート処理でエラーが発生している")
    print("3. 馬名の表記が異なる（全角・半角、スペースなど）")
    print("4. データベースの制約エラーで挿入に失敗している")

    # 4. 推奨アクション
    print("\n4. 推奨アクション")
    print("1. 手動で挿入したデータを確認")
    print("2. 他の欠落データがないか調査")
    print("3. Excelファイルの作成プロセスを確認")
    print("4. データインポート処理の改善")

if __name__ == '__main__':
    fix_missing_omega_tuxedo()

