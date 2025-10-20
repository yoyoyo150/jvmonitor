import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
import json
import os
import sys

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

class TargetFrontierValidator:
    """TARGET frontierデータとの整合性検証システム"""
    
    def __init__(self, excel_db_path="trainer_prediction_system/excel_data.db"):
        self.excel_db_path = excel_db_path
        self.conn = None
        self.connect()
    
    def connect(self):
        """データベース接続"""
        try:
            self.conn = sqlite3.connect(self.excel_db_path)
            print("データベース接続成功")
        except Exception as e:
            print(f"データベース接続エラー: {e}")
            return False
        return True
    
    def get_trainer_data_for_validation(self, start_date="2024-11-02", end_date="2025-09-28"):
        """検証用調教師データの取得"""
        try:
            query = """
            SELECT 
                SourceDate,
                HorseNameS,
                Trainer_Name,
                Mark5,
                Mark6,
                Chaku,
                ZI_Index,
                ZM_Value,
                Ba_R_Raw,
                RaceName
            FROM excel_marks
            WHERE SourceDate >= ? AND SourceDate <= ?
            AND Mark5 IS NOT NULL 
            AND Mark6 IS NOT NULL
            AND Mark5 != '?'
            AND Mark6 != '?'
            AND Trainer_Name IS NOT NULL
            AND Trainer_Name != ''
            """
            
            df = pd.read_sql_query(query, self.conn, params=[start_date.replace('-', ''), end_date.replace('-', '')])
            
            # Mark5, Mark6を数値に変換
            df['Mark5_numeric'] = pd.to_numeric(df['Mark5'], errors='coerce')
            df['Mark6_numeric'] = pd.to_numeric(df['Mark6'], errors='coerce')
            
            # Mark5+Mark6の合計を計算
            df['Mark5_Mark6_sum'] = df['Mark5_numeric'] + df['Mark6_numeric']
            
            # 条件適用（2以上6以下）
            df = df[
                (df['Mark5_Mark6_sum'] >= 2) & 
                (df['Mark5_Mark6_sum'] <= 6)
            ]
            
            print(f"検証用データ取得完了: {len(df)}件")
            return df
            
        except Exception as e:
            print(f"データ取得エラー: {e}")
            return None
    
    def calculate_trainer_stats(self, df, trainer_name):
        """特定調教師の統計計算"""
        if df is None or df.empty:
            return None
        
        # 調教師でフィルタ
        trainer_data = df[df['Trainer_Name'] == trainer_name].copy()
        
        if trainer_data.empty:
            return None
        
        # 着順データの処理
        trainer_data['Chaku_numeric'] = pd.to_numeric(trainer_data['Chaku'], errors='coerce')
        
        # 有効な着順データのみ
        valid_finish = trainer_data.dropna(subset=['Chaku_numeric'])
        
        if valid_finish.empty:
            return {
                'trainer_name': trainer_name,
                'total_races': len(trainer_data),
                'valid_races': 0,
                'wins': 0,
                'places': 0,
                'shows': 0,
                'win_rate': 0.0,
                'place_rate': 0.0,
                'show_rate': 0.0,
                'fukusho_rate': 0.0
            }
        
        # 着別度数の計算
        wins = len(valid_finish[valid_finish['Chaku_numeric'] == 1])
        places = len(valid_finish[valid_finish['Chaku_numeric'] == 2])
        shows = len(valid_finish[valid_finish['Chaku_numeric'] == 3])
        fukushos = len(valid_finish[valid_finish['Chaku_numeric'] <= 3])
        
        total_races = len(trainer_data)
        valid_races = len(valid_finish)
        
        # 勝率、連対率、複勝率の計算
        win_rate = (wins / valid_races * 100) if valid_races > 0 else 0
        place_rate = ((wins + places) / valid_races * 100) if valid_races > 0 else 0
        show_rate = ((wins + places + shows) / valid_races * 100) if valid_races > 0 else 0
        fukusho_rate = (fukushos / valid_races * 100) if valid_races > 0 else 0
        
        return {
            'trainer_name': trainer_name,
            'total_races': total_races,
            'valid_races': valid_races,
            'wins': wins,
            'places': places,
            'shows': shows,
            'fukushos': fukushos,
            'win_rate': round(win_rate, 1),
            'place_rate': round(place_rate, 1),
            'show_rate': round(show_rate, 1),
            'fukusho_rate': round(fukusho_rate, 1)
        }
    
    def validate_against_target_frontier(self, df):
        """TARGET frontierデータとの整合性検証"""
        
        # 検証対象の調教師（お客様のデータから）
        target_trainers = [
            "中内田充",
            "斉藤崇史",
            "庄野靖志",
            "堀宣行"
        ]
        
        validation_results = {}
        
        for trainer in target_trainers:
            print(f"\n=== {trainer} の検証 ===")
            
            # 統計計算
            stats = self.calculate_trainer_stats(df, trainer)
            
            if stats:
                print(f"総レース数: {stats['total_races']}")
                print(f"有効レース数: {stats['valid_races']}")
                print(f"着別度数: {stats['wins']}-{stats['places']}-{stats['shows']}-{stats['fukushos']}/{stats['valid_races']}")
                print(f"勝率: {stats['win_rate']}%")
                print(f"連対率: {stats['place_rate']}%")
                print(f"複勝率: {stats['show_rate']}%")
                print(f"複勝率: {stats['fukusho_rate']}%")
                
                validation_results[trainer] = stats
            else:
                print(f"{trainer} のデータが見つかりません")
                validation_results[trainer] = None
        
        return validation_results
    
    def compare_with_target_frontier_data(self, validation_results):
        """TARGET frontierデータとの比較"""
        
        # TARGET frontierの基準データ
        target_data = {
            "中内田充": {
                "着別度数": "18-14-12-41/85",
                "勝率": 21.2,
                "連対率": 37.6,
                "複勝率": 51.8
            },
            "斉藤崇史": {
                "着別度数": "19-8-6-36/69",
                "勝率": 27.5,
                "連対率": 39.1,
                "複勝率": 47.8
            },
            "庄野靖志": {
                "着別度数": "6-1-2-8/17",
                "勝率": 35.3,
                "連対率": 41.2,
                "複勝率": 52.9
            },
            "堀宣行": {
                "着別度数": "7-5-3-13/28",
                "勝率": 25.0,
                "連対率": 42.9,
                "複勝率": 53.6
            }
        }
        
        comparison_results = {}
        
        for trainer, stats in validation_results.items():
            if stats and trainer in target_data:
                target = target_data[trainer]
                
                # 着別度数の比較
                actual_format = f"{stats['wins']}-{stats['places']}-{stats['shows']}-{stats['fukushos']}/{stats['valid_races']}"
                target_format = target["着別度数"]
                
                # 勝率の比較
                win_rate_diff = abs(stats['win_rate'] - target["勝率"])
                
                # 連対率の比較
                place_rate_diff = abs(stats['place_rate'] - target["連対率"])
                
                # 複勝率の比較
                show_rate_diff = abs(stats['show_rate'] - target["複勝率"])
                
                comparison_results[trainer] = {
                    "actual": stats,
                    "target": target,
                    "着別度数_一致": actual_format == target_format,
                    "着別度数_実際": actual_format,
                    "着別度数_目標": target_format,
                    "勝率_差": round(win_rate_diff, 1),
                    "連対率_差": round(place_rate_diff, 1),
                    "複勝率_差": round(show_rate_diff, 1),
                    "総合評価": "良好" if win_rate_diff <= 3 and place_rate_diff <= 3 and show_rate_diff <= 3 else "要改善"
                }
                
                print(f"\n=== {trainer} の比較結果 ===")
                print(f"着別度数: {actual_format} (目標: {target_format})")
                print(f"勝率: {stats['win_rate']}% (目標: {target['勝率']}%, 差: {win_rate_diff:.1f}%)")
                print(f"連対率: {stats['place_rate']}% (目標: {target['連対率']}%, 差: {place_rate_diff:.1f}%)")
                print(f"複勝率: {stats['show_rate']}% (目標: {target['複勝率']}%, 差: {show_rate_diff:.1f}%)")
                print(f"総合評価: {'良好' if win_rate_diff <= 3 and place_rate_diff <= 3 and show_rate_diff <= 3 else '要改善'}")
        
        return comparison_results
    
    def generate_validation_report(self, validation_results, comparison_results):
        """検証レポート生成"""
        report = {
            'validation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'validation_results': validation_results,
            'comparison_results': comparison_results
        }
        
        # レポート保存
        output_dir = "outputs"
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # JSON形式で保存
        json_file = f"{output_dir}/target_frontier_validation_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n検証レポート生成完了: {json_file}")
        
        return report
    
    def run_validation(self):
        """検証実行"""
        print("=== TARGET frontierデータとの整合性検証開始 ===")
        
        # データ取得
        df = self.get_trainer_data_for_validation()
        if df is None or df.empty:
            print("データ取得失敗")
            return None
        
        # 整合性検証
        validation_results = self.validate_against_target_frontier(df)
        
        # TARGET frontierデータとの比較
        comparison_results = self.compare_with_target_frontier_data(validation_results)
        
        # レポート生成
        report = self.generate_validation_report(validation_results, comparison_results)
        
        return report

def main():
    validator = TargetFrontierValidator()
    report = validator.run_validation()
    
    if report:
        print("\n検証完了")
    else:
        print("\n検証失敗")

if __name__ == "__main__":
    main()
