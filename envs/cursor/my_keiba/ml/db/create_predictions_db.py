#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
予測データベース作成・更新スクリプト
RankGrade列の追加とテーブル構造の管理
"""

import argparse
import sqlite3
import os
import sys

def create_predictions_db(db_path):
    """予測データベースの作成・更新"""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Predictionsテーブルの作成（RankGrade列を含む）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Year TEXT,
            MonthDay TEXT,
            JyoCD TEXT,
            RaceNum TEXT,
            Umaban TEXT,
            Scenario TEXT,
            WinScore REAL,
            PlaceScore REAL,
            Odds REAL,
            InvestFlag INTEGER,
            M5Value REAL,
            TrainerScore REAL,
            FeaturesHash TEXT,
            ModelVersion TEXT DEFAULT 'v1.0',
            RankGrade TEXT,
            CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 既存テーブルにRankGrade列を追加（存在しない場合）
    try:
        cursor.execute("ALTER TABLE Predictions ADD COLUMN RankGrade TEXT")
        print(f"[INFO] RankGrade列を追加しました")
    except sqlite3.OperationalError:
        # 列が既に存在する場合
        print(f"[INFO] RankGrade列は既に存在します")
    
    # インデックスの作成
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_predictions_date_scenario 
        ON Predictions(Year, MonthDay, Scenario)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_predictions_race 
        ON Predictions(Year, MonthDay, JyoCD, RaceNum, Umaban)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_predictions_rank 
        ON Predictions(RankGrade, Scenario)
    """)
    
    conn.commit()
    conn.close()
    
    print(f"[OK] データベース構造を更新しました: {db_path}")

def main():
    parser = argparse.ArgumentParser(description='予測データベース作成・更新')
    parser.add_argument('--db', default='predictions.db', help='データベースファイルパス')
    
    args = parser.parse_args()
    
    # データベースディレクトリの作成
    db_dir = os.path.dirname(args.db)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    create_predictions_db(args.db)

if __name__ == '__main__':
    main()

