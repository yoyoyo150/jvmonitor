#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
シンプルなエクセルデータインポートスクリプト
"""
import sys
import os
import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def main():
    """メイン関数"""
    try:
        print("=== エクセルデータインポート開始 ===")
        
        # プロジェクトルートに移動
        current_dir = Path.cwd()
        project_root = current_dir
        while not (project_root / "yDate").exists() and project_root.parent != project_root:
            project_root = project_root.parent
        
        if not (project_root / "yDate").exists():
            print("❌ プロジェクトルートが見つかりません")
            return 1
        
        os.chdir(project_root)
        print(f"プロジェクトルート: {project_root}")
        
        # データベース接続
        db_path = "excel_data.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # テーブル作成
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS HORSE_MARKS (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                SourceDate TEXT,
                HorseName TEXT,
                NormalizedHorseName TEXT,
                RaceId TEXT,
                RaceName TEXT,
                JyoCD TEXT,
                Kaiji TEXT,
                Nichiji TEXT,
                RaceNum TEXT,
                Umaban TEXT,
                MorningOdds TEXT,
                Mark1 TEXT,
                Mark2 TEXT,
                Mark3 TEXT,
                Mark4 TEXT,
                Mark5 TEXT,
                Mark6 TEXT,
                Mark7 TEXT,
                Mark8 TEXT,
                ZI_INDEX TEXT,
                ZM_VALUE TEXT,
                SHIBA_DA TEXT,
                KYORI_M TEXT,
                R_MARK1 TEXT,
                R_MARK2 TEXT,
                R_MARK3 TEXT,
                Algo_Score TEXT,
                Original_Score TEXT,
                Acceleration_Score TEXT,
                Previous_Rank TEXT,
                Previous_Popularity TEXT,
                Previous_Odds TEXT,
                Previous_Track_Type TEXT,
                Previous_Distance TEXT,
                Previous_Class TEXT,
                Previous_Weight TEXT,
                Weight_Change TEXT,
                Jockey_Win_Rate TEXT,
                Trainer_Win_Rate TEXT,
                Course_Group TEXT,
                Blood_Type TEXT,
                SourceFile TEXT,
                ImportedAt DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 既存テーブルに新しい列を追加（エラーを無視）
        new_columns = [
            'Algo_Score', 'Original_Score', 'Acceleration_Score', 'Previous_Rank',
            'Previous_Popularity', 'Previous_Odds', 'Previous_Track_Type', 'Previous_Distance',
            'Previous_Class', 'Previous_Weight', 'Weight_Change', 'Jockey_Win_Rate',
            'Trainer_Win_Rate', 'Course_Group', 'Blood_Type'
        ]
        
        for col in new_columns:
            try:
                cursor.execute(f"ALTER TABLE HORSE_MARKS ADD COLUMN {col} TEXT")
            except sqlite3.OperationalError:
                # 列が既に存在する場合は無視
                pass
        
        # yDateディレクトリの最新ファイルを処理
        yDate_dir = Path("yDate")
        excel_files = list(yDate_dir.glob("*.xlsx")) + list(yDate_dir.glob("*.csv"))
        excel_files.sort()
        
        # 最新5ファイルのみ処理
        latest_files = excel_files[-5:]
        print(f"処理対象ファイル数: {len(latest_files)}")
        
        total_imported = 0
        
        for file_path in latest_files:
            print(f"処理中: {file_path.name}")
            
            try:
                # エクセルファイル読み込み
                if file_path.suffix == '.xlsx':
                    df = pd.read_excel(file_path, dtype=str, engine='openpyxl').fillna("")
                elif file_path.suffix == '.csv':
                    df = pd.read_csv(file_path, dtype=str).fillna("")
                else:
                    continue
                
                # データ変換
                records_to_insert = []
                for index, row in df.iterrows():
                    horse_name = str(row.get("馬名S", "") or "").strip()
                    if not horse_name:
                        continue
                    
                    record = {
                        'SourceDate': str(row.get("レースID(新)", "") or "").strip()[:8] if str(row.get("レースID(新)", "") or "").strip() else file_path.stem[:8],
                        'HorseName': horse_name,
                        'NormalizedHorseName': horse_name,
                        'RaceId': str(row.get("レースID(新)", "") or "").strip(),
                        'RaceName': str(row.get("レース名", "") or "").strip(),
                        'JyoCD': str(row.get("場", "") or "").strip(),
                        'Kaiji': "",
                        'Nichiji': "",
                        'RaceNum': str(row.get("R", "") or "").strip(),
                        'Umaban': str(row.get("馬番", "") or "").strip(),
                        'MorningOdds': str(row.get("朝オッズ", "") or "").strip(),
                        'Mark1': str(row.get("馬印1", "") or "").strip(),
                        'Mark2': str(row.get("馬印2", "") or "").strip(),
                        'Mark3': str(row.get("馬印3", "") or "").strip(),
                        'Mark4': str(row.get("馬印4", "") or "").strip(),
                        'Mark5': str(row.get("馬印5", "") or "").strip(),
                        'Mark6': str(row.get("馬印6", "") or "").strip(),
                        'Mark7': str(row.get("馬印7", "") or "").strip(),
                        'Mark8': str(row.get("馬印8", "") or "").strip(),
                        'ZI_INDEX': str(row.get("ZI指数", "") or "").strip(),
                        'ZM_VALUE': str(row.get("ZM", "") or "").strip(),
                        'SHIBA_DA': str(row.get("芝ダ", "") or "").strip(),
                        'KYORI_M': str(row.get("距離", "") or "").strip(),
                        'R_MARK1': str(row.get("R印1", "") or "").strip(),
                        'R_MARK2': str(row.get("R印2", "") or "").strip(),
                        'R_MARK3': str(row.get("R印3", "") or "").strip(),
                        # 追加の重要な列
                        'Algo_Score': str(row.get("アルゴ", "") or "").strip(),
                        'Original_Score': str(row.get("オリジナル", "") or "").strip(),
                        'Acceleration_Score': str(row.get("加速", "") or "").strip(),
                        'Previous_Rank': str(row.get("前順位", "") or "").strip(),
                        'Previous_Popularity': str(row.get("前人気", "") or "").strip(),
                        'Previous_Odds': str(row.get("前オッズ", "") or "").strip(),
                        'Previous_Track_Type': str(row.get("前芝ダ", "") or "").strip(),
                        'Previous_Distance': str(row.get("前距離", "") or "").strip(),
                        'Previous_Class': str(row.get("前クラス", "") or "").strip(),
                        'Previous_Weight': str(row.get("前斤量", "") or "").strip(),
                        'Weight_Change': str(row.get("増減", "") or "").strip(),
                        'Jockey_Win_Rate': str(row.get("騎手勝率", "") or "").strip(),
                        'Trainer_Win_Rate': str(row.get("調教師勝率", "") or "").strip(),
                        'Course_Group': str(row.get("コース群", "") or "").strip(),
                        'Blood_Type': str(row.get("血統タイプ", "") or "").strip(),
                        'SourceFile': file_path.name,
                        'ImportedAt': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    records_to_insert.append(record)
                
                # データベースに挿入
                if records_to_insert:
                    column_names = list(records_to_insert[0].keys())
                    placeholders = ", ".join(f":{name}" for name in column_names)
                    
                    sql = f"""
                        INSERT OR REPLACE INTO HORSE_MARKS ({', '.join(column_names)})
                        VALUES ({placeholders})
                    """
                    
                    cursor.executemany(sql, records_to_insert)
                    conn.commit()
                    
                    print(f"  ✅ {len(records_to_insert)}件インポート完了")
                    total_imported += len(records_to_insert)
                
            except Exception as e:
                print(f"  ❌ エラー: {e}")
                continue
        
        conn.close()
        
        print(f"✅ 総インポート件数: {total_imported:,}")
        print("=== エクセルデータインポート完了 ===")
        
        return 0
        
    except Exception as e:
        print(f"エラー: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
