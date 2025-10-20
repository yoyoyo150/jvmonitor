#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
調教師予想システム
統一されたクオリティ管理とJVMonitor連携
"""
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from database_manager import DatabaseManager

class TrainerPredictionSystem:
    """調教師予想システム"""
    
    def __init__(self, config_path="config/trainer_prediction_config.json"):
        """初期化"""
        self.config_path = config_path
        
        # config_pathをPathオブジェクトに変換し、絶対パスまたは実行ファイルからの相対パスで解決
        # run_analysis.py が trainer_prediction_system ディレクトリ直下にあるため、
        # config_path は trainer_prediction_system/config/trainer_prediction_config.json を指す
        base_dir = Path(__file__).parent.parent # trainer_prediction_system ディレクトリ
        resolved_config_path = (base_dir / self.config_path).resolve()
        
        self.db_manager = DatabaseManager(str(resolved_config_path))
        self.config = self.db_manager.config
        
    def analyze_trainer_performance(self, target_dates=None):
        """調教師成績分析"""
        print("=== 調教師成績分析開始 ===")
        
        try:
            with self.db_manager as db:
                # データ取得
                df = db.get_trainer_data()
                if df is None:
                    print("データ取得に失敗しました")
                    return None
                
                # データ品質検証
                is_valid, message = db.validate_data_quality(df)
                print(f"データ品質: {message}")
                
                if not is_valid:
                    print("データ品質が不十分です")
                    return None
                
                # 調教師統計計算
                trainer_stats = db.get_trainer_statistics(df)
                if trainer_stats is None:
                    print("調教師統計計算に失敗しました")
                    return None
                
                # 結果保存
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                csv_path = db.save_results(trainer_stats, f"trainer_analysis_{timestamp}.csv")
                json_path = db.save_results(trainer_stats, f"trainer_analysis_{timestamp}.json", format='json')
                
                print(f"分析結果保存: {csv_path}")
                print(f"JSON結果保存: {json_path}")
                
                return trainer_stats
                
        except Exception as e:
            print(f"調教師成績分析エラー: {e}")
            return None
    
    def generate_candidates(self, trainer_stats, min_place_rate=0.25):
        """予想候補生成"""
        print("=== 予想候補生成開始 ===")
        
        try:
            if trainer_stats is None or trainer_stats.empty:
                print("調教師統計データがありません")
                return None
            
            # 高成績調教師の選定
            high_performance_trainers = trainer_stats[
                (trainer_stats['PlaceRate'] >= min_place_rate) &
                (trainer_stats['TotalRaces'] >= self.config['analysis_config']['trainer_criteria']['min_races'])
            ].copy()
            
            # スコア計算
            high_performance_trainers['Score'] = (
                high_performance_trainers['WinCount'] * self.config['prediction_config']['scoring_system']['win_score'] +
                high_performance_trainers['PlaceCount'] * self.config['prediction_config']['scoring_system']['place_score'] +
                high_performance_trainers['ShowCount'] * self.config['prediction_config']['scoring_system']['show_score'] +
                high_performance_trainers['PlaceRate'] * 10  # 着順率ボーナス
            )
            
            # ソート
            high_performance_trainers = high_performance_trainers.sort_values('Score', ascending=False)
            
            print(f"高成績調教師: {len(high_performance_trainers)}名")
            print("上位10名:")
            for _, row in high_performance_trainers.head(10).iterrows():
                print(f"  {row['TrainerName']}: {row['Result']} (着順率: {row['PlaceRate']:.2f}, スコア: {row['Score']:.2f})")
            
            # 結果保存
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_path = self.db_manager.save_results(high_performance_trainers, f"candidates_{timestamp}.csv")
            
            print(f"候補生成結果保存: {csv_path}")
            return high_performance_trainers
            
        except Exception as e:
            print(f"予想候補生成エラー: {e}")
            return None
    
    def validate_jvmonitor_alignment(self, trainer_stats):
        """JVMonitor連携検証"""
        print("=== JVMonitor連携検証開始 ===")
        
        try:
            jvmonitor_config = self.config.get('jvmonitor_alignment', {})
            if not jvmonitor_config.get('enabled', False):
                print("JVMonitor連携が無効です")
                return True
            
            expected_count = jvmonitor_config.get('expected_trainer_count', 37)
            tolerance = jvmonitor_config.get('tolerance', 2)
            
            actual_count = len(trainer_stats) if trainer_stats is not None else 0
            
            print(f"期待される調教師数: {expected_count}")
            print(f"実際の調教師数: {actual_count}")
            print(f"許容範囲: ±{tolerance}")
            
            if abs(actual_count - expected_count) <= tolerance:
                print("✅ JVMonitor連携検証: 成功")
                return True
            else:
                print(f"❌ JVMonitor連携検証: 失敗 (差: {abs(actual_count - expected_count)})")
                return False
                
        except Exception as e:
            print(f"JVMonitor連携検証エラー: {e}")
            return False
    
    def generate_quality_report(self, trainer_stats, candidates):
        """品質レポート生成"""
        print("=== 品質レポート生成開始 ===")
        
        try:
            report = {
                "generation_time": datetime.now().isoformat(),
                "system_version": self.config['system_info']['version'],
                "data_quality": {
                    "trainer_count": len(trainer_stats) if trainer_stats is not None else 0,
                    "candidate_count": len(candidates) if candidates is not None else 0,
                    "data_source": self.config['database_config']['primary_table']
                },
                "analysis_results": {
                    "total_trainers": len(trainer_stats) if trainer_stats is not None else 0,
                    "high_performance_trainers": len(candidates) if candidates is not None else 0,
                    "average_place_rate": trainer_stats['PlaceRate'].mean() if trainer_stats is not None and not trainer_stats.empty else 0.0
                },
                "jvmonitor_alignment": {
                    "expected_count": self.config.get('jvmonitor_alignment', {}).get('expected_trainer_count', 37),
                    "actual_count": len(trainer_stats) if trainer_stats is not None else 0,
                    "alignment_status": "OK" if self.validate_jvmonitor_alignment(trainer_stats) else "NG"
                }
            }
            
            # レポート保存
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = Path(self.config['output_config']['output_directory']) / f"quality_report_{timestamp}.json"
            report_path.parent.mkdir(exist_ok=True)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            print(f"品質レポート保存: {report_path}")
            return report
            
        except Exception as e:
            print(f"品質レポート生成エラー: {e}")
            return None
    
    def run_full_analysis(self, target_dates=None, min_place_rate=0.25):
        """完全分析実行"""
        print("=== 調教師予想システム完全分析開始 ===")
        
        try:
            # 1. 調教師成績分析
            trainer_stats = self.analyze_trainer_performance(target_dates)
            if trainer_stats is None:
                print("調教師成績分析に失敗しました")
                return None
            
            # 2. 予想候補生成
            candidates = self.generate_candidates(trainer_stats, min_place_rate)
            if candidates is None:
                print("予想候補生成に失敗しました")
                return None
            
            # 3. JVMonitor連携検証
            jvmonitor_ok = self.validate_jvmonitor_alignment(trainer_stats)
            
            # 4. 品質レポート生成
            quality_report = self.generate_quality_report(trainer_stats, candidates)
            
            print("=== 完全分析完了 ===")
            return {
                'trainer_stats': trainer_stats,
                'candidates': candidates,
                'jvmonitor_alignment': jvmonitor_ok,
                'quality_report': quality_report
            }
            
        except Exception as e:
            print(f"完全分析エラー: {e}")
            return None

if __name__ == "__main__":
    # テスト実行
    system = TrainerPredictionSystem()
    results = system.run_full_analysis(target_dates=['20250927', '20250928'])
    
    if results:
        print("分析完了")
        print(f"調教師数: {len(results['trainer_stats'])}")
        print(f"候補数: {len(results['candidates'])}")
        print(f"JVMonitor連携: {'OK' if results['jvmonitor_alignment'] else 'NG'}")
    else:
        print("分析失敗")
