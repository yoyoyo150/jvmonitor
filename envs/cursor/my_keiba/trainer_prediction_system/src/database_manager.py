#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
データベース管理クラス
統一されたデータベース参照とクオリティ管理
"""
import sqlite3
import pandas as pd
import json
import sys
import os
from pathlib import Path
from datetime import datetime
import logging

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

class DatabaseManager:
    """データベース管理クラス"""
    
    @staticmethod
    def normalize_horse_name(horse_name):
        """馬名を正規化（全角スペースを半角に、前後の空白除去）"""
        if isinstance(horse_name, str):
            return horse_name.replace('　', ' ').strip()
        return str(horse_name) # 文字列以外はそのまま文字列化
    
    def __init__(self, config_path="config/trainer_prediction_config.json"):
        """初期化"""
        self.config = self.load_config(config_path)
        self.db_path = self.config['database_config']['db_path'] # ecore.dbのパス
        self.excel_db_path = self.config['database_config']['excel_db_path'] # excel_data.dbのパス
        self.ecore_conn = None
        self.excel_conn = None
        self.setup_logging()
        
    def load_config(self, config_path):
        """設定ファイルの読み込み"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"設定ファイルの読み込みエラー: {e}")
            return {}
    
    def setup_logging(self):
        """ログ設定"""
        log_dir = Path(self.config.get('output_config', {}).get('log_directory', 'logs'))
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / f'trainer_prediction_{datetime.now().strftime("%Y%m%d")}.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def connect(self, db_type: str = "ecore"):
        """データベース接続"""
        try:
            if db_type == "ecore":
                self.ecore_conn = sqlite3.connect(self.db_path)
                self.logger.info(f"ecoreデータベース接続成功: {self.db_path}")
                return True
            elif db_type == "excel":
                self.excel_conn = sqlite3.connect(self.excel_db_path)
                self.logger.info(f"Excel専用データベース接続成功: {self.excel_db_path}")
                return True
            else:
                self.logger.error(f"不明なデータベースタイプ: {db_type}")
                return False
        except Exception as e:
            self.logger.error(f"{db_type}データベース接続エラー: {e}")
            return False
    
    def disconnect(self, db_type: str = "all"):
        """データベース切断"""
        if db_type == "ecore" or db_type == "all":
            if self.ecore_conn:
                self.ecore_conn.close()
                self.logger.info("ecoreデータベース切断")
        if db_type == "excel" or db_type == "all":
            if self.excel_conn:
                self.excel_conn.close()
                self.logger.info("Excel専用データベース切断")
    
    def get_trainer_data(self, target_dates=None):
        """調教師データの取得（excel_data.dbのみ使用）"""
        if not self.excel_conn:
            if not self.connect(db_type="excel"):
                return None
        
        try:
            # 設定から取得
            analysis_config = self.config['analysis_config']
            
            # 日付条件の生成
            if target_dates is None:
                # 設定ファイルのstart_dateとend_dateを使用して期間を生成
                start_date = analysis_config['date_range']['start_date']
                end_date = analysis_config['date_range']['end_date']
                
                # 日付範囲を生成
                from datetime import datetime, timedelta
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                
                target_dates = []
                current_dt = start_dt
                while current_dt <= end_dt:
                    target_dates.append(current_dt.strftime('%Y%m%d'))
                    current_dt += timedelta(days=1)
                
                # target_datesが空でないことを確認
                if not target_dates:
                    self.logger.error("生成された日付リストが空です")
                    return None
            
            date_condition_excel = " OR ".join([f"SourceDate = '{date}'" for date in target_dates])
            
            # デバッグ用ログ
            self.logger.info(f"生成された日付数: {len(target_dates)}")
            self.logger.info(f"開始日: {target_dates[0] if target_dates else 'None'}")
            self.logger.info(f"終了日: {target_dates[-1] if target_dates else 'None'}")
            self.logger.info(f"日付条件 (excel): {date_condition_excel[:100]}...")
            
            # excel_data.db (excel_marks) から全データを取得
            excel_query = f"""
            SELECT 
                SourceDate,
                HorseNameS as HorseName,
                Trainer_Name as TrainerName,
                Chaku as KakuteiJyuni,
                Mark5,
                Mark6,
                Ba_R_Raw
            FROM excel_marks
            WHERE {date_condition_excel}
            AND Trainer_Name IS NOT NULL 
            AND Trainer_Name != ''
            AND Chaku IS NOT NULL 
            AND Chaku != ''
            AND (Mark5 IS NOT NULL OR Mark6 IS NOT NULL)
            """
            
            df_excel = pd.read_sql_query(excel_query, self.excel_conn)
            self.logger.info(f"excel_data.dbからデータ取得: {len(df_excel)}件")
            
            # Mark5+Mark6の条件を適用（合計2以上6以下）
            if 'Mark5' in df_excel.columns and 'Mark6' in df_excel.columns:
                # Mark5とMark6を数値に変換（'?'はNaNに）
                df_excel['Mark5_numeric'] = pd.to_numeric(df_excel['Mark5'].replace('?', pd.NA), errors='coerce')
                df_excel['Mark6_numeric'] = pd.to_numeric(df_excel['Mark6'].replace('?', pd.NA), errors='coerce')
                
                # Mark5+Mark6の合計を計算
                df_excel['Mark5_Mark6_sum'] = df_excel['Mark5_numeric'] + df_excel['Mark6_numeric']
                
                # 条件を適用（2以上6以下）
                df_excel = df_excel[
                    (df_excel['Mark5_Mark6_sum'] >= 2) & 
                    (df_excel['Mark5_Mark6_sum'] <= 6)
                ]
                
                self.logger.info(f"Mark5+Mark6条件適用後: {len(df_excel)}件")
            
            return df_excel
            
        except Exception as e:
            self.logger.error(f"データ取得・結合エラー: {e}")
            return None
    
    def validate_data_quality(self, df):
        """データ品質の検証"""
        if df is None or df.empty:
            return False, "データが空です"
        
        # 必須カラムの確認 (excel_data.dbのDFで必要なカラム)
        required_columns = ['SourceDate', 'TrainerName', 'KakuteiJyuni', 'HorseName']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return False, f"必須カラムが不足: {missing_columns}"
        
        # 空値の確認 (最低限の必須カラム、KakuteiJyuniは空値を許容)
        critical_columns = ['SourceDate', 'TrainerName', 'HorseName']
        null_counts = df[critical_columns].isnull().sum()
        if null_counts.any():
            return False, f"必須カラムに空値が存在: {null_counts.to_dict()}"
        
        # KakuteiJyuniの空値数をログに記録
        chaku_nulls = df['KakuteiJyuni'].isnull().sum()
        if chaku_nulls > 0:
            self.logger.info(f"KakuteiJyuniの空値: {chaku_nulls}件 (着順未確定レース)")
        
        # 着順データの確認 (中止、除外、未確定を許容)
        valid_finish_orders = (
            df['KakuteiJyuni'].str.isdigit() | 
            (df['KakuteiJyuni'] == '00') |
            (df['KakuteiJyuni'] == '止') |
            (df['KakuteiJyuni'] == '消') |
            df['KakuteiJyuni'].isnull()
        )
        if not valid_finish_orders.all():
            invalid_orders = df[~valid_finish_orders]['KakuteiJyuni'].unique()
            return False, f"無効な着順データ: {invalid_orders}"
        
        # Mark5/Mark6 のデータ型チェック (文字列として存在すればOK)
        if 'Mark5' in df.columns and not (df['Mark5'].apply(lambda x: isinstance(x, str) or pd.isna(x))).all():
            return False, "Mark5カラムに文字列またはNone以外のデータが含まれています"
        if 'Mark6' in df.columns and not (df['Mark6'].apply(lambda x: isinstance(x, str) or pd.isna(x))).all():
            return False, "Mark6カラムに文字列またはNone以外のデータが含まれています"
        
        return True, "データ品質OK"
    
    def get_trainer_statistics(self, df):
        """調教師統計の計算"""
        if df is None or df.empty:
            return None
        
        try:
            # 着順データを数値に変換
            df['KakuteiJyuni_numeric'] = pd.to_numeric(df['KakuteiJyuni'], errors='coerce')
            
            # Mark5とMark6を数値に変換（'?'はNaNに）
            df['Mark5_numeric'] = pd.to_numeric(df['Mark5'].replace('?', pd.NA), errors='coerce')
            df['Mark6_numeric'] = pd.to_numeric(df['Mark6'].replace('?', pd.NA), errors='coerce')
            
            # 調教師別統計
            trainer_stats = df.groupby('TrainerName').apply(
                lambda x: pd.Series({
                    'TotalRaces': len(x),
                    'WinCount': (x['KakuteiJyuni_numeric'] == 1).sum(),
                    'PlaceCount': (x['KakuteiJyuni_numeric'] == 2).sum(),
                    'ShowCount': (x['KakuteiJyuni_numeric'] == 3).sum(),
                    'OtherCount': (x['KakuteiJyuni_numeric'] > 3).sum(),
                    'PlaceRate': ((x['KakuteiJyuni_numeric'] <= 3).sum() / len(x)) if len(x) > 0 else 0.0,
                    'AvgMark5': x['Mark5_numeric'].mean(),
                    'AvgMark6': x['Mark6_numeric'].mean()
                })
            ).reset_index()
            
            # 結果文字列の生成
            trainer_stats['Result'] = trainer_stats.apply(
                lambda row: f"{int(row['WinCount'])}-{int(row['PlaceCount'])}-{int(row['ShowCount'])}-{int(row['OtherCount'])}/{int(row['TotalRaces'])}",
                axis=1
            )
            
            self.logger.info(f"調教師統計計算完了: {len(trainer_stats)}名")
            return trainer_stats
            
        except Exception as e:
            self.logger.error(f"調教師統計計算エラー: {e}")
            return None
    
    def save_results(self, data, filename, format='csv'):
        """結果の保存"""
        try:
            output_dir = Path(self.config.get('output_config', {}).get('output_directory', 'outputs'))
            output_dir.mkdir(exist_ok=True)
            
            file_path = output_dir / filename
            
            if format == 'csv':
                data.to_csv(file_path, index=False, encoding='utf-8-sig')
            elif format == 'json':
                data.to_json(file_path, orient='records', force_ascii=False, indent=2)
            
            self.logger.info(f"結果保存完了: {file_path}")
            return str(file_path)
            
        except Exception as e:
            self.logger.error(f"結果保存エラー: {e}")
            return None
    
    def __enter__(self):
        """コンテキストマネージャー開始"""
        self.connect(db_type="ecore")
        self.connect(db_type="excel")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャー終了"""
        self.disconnect(db_type="all")

if __name__ == "__main__":
    # テスト実行
    with DatabaseManager() as db:
        df = db.get_trainer_data()
        if df is not None:
            is_valid, message = db.validate_data_quality(df)
            print(f"データ品質: {message}")
            
            if is_valid:
                trainer_stats = db.get_trainer_statistics(df)
                if trainer_stats is not None:
                    print(f"調教師統計: {len(trainer_stats)}名")
                    print(trainer_stats.head())
