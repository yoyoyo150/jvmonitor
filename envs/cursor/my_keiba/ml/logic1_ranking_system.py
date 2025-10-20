#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ロジック1: S~Eランク分け評価システム
JVMonitor統合用の馬評価ロジック
"""
import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class Logic1RankingSystem:
    """ロジック1による馬のランク評価システム"""
    
    def __init__(self, ecore_db_path: str, excel_db_path: str):
        self.ecore_db_path = ecore_db_path
        self.excel_db_path = excel_db_path
        self.rank_rules = self._load_rank_rules()
    
    def _load_rank_rules(self) -> Dict:
        """ランクルールの読み込み"""
        config_path = os.path.join(os.path.dirname(__file__), 'config', 'logic1_rank_rules.json')
        
        # デフォルトルールを作成（ファイルが存在しない場合）
        default_rules = {
            "logic1_rules": {
                "S": {
                    "description": "最高評価（投資対象）",
                    "conditions": {
                        "win_score_min": 0.7,
                        "m5_value_max": 3.0,
                        "trainer_win_rate_min": 0.15,
                        "jockey_win_rate_min": 0.10,
                        "recent_form_min": 3,
                        "excel_algo_score_min": 80
                    }
                },
                "A": {
                    "description": "高評価（投資対象）",
                    "conditions": {
                        "win_score_min": 0.5,
                        "m5_value_max": 5.0,
                        "trainer_win_rate_min": 0.10,
                        "jockey_win_rate_min": 0.08,
                        "recent_form_min": 2,
                        "excel_algo_score_min": 70
                    }
                },
                "B": {
                    "description": "中評価（要検討）",
                    "conditions": {
                        "win_score_min": 0.3,
                        "m5_value_max": 7.0,
                        "trainer_win_rate_min": 0.08,
                        "jockey_win_rate_min": 0.06,
                        "recent_form_min": 1,
                        "excel_algo_score_min": 60
                    }
                },
                "C": {
                    "description": "普通評価",
                    "conditions": {
                        "win_score_min": 0.2,
                        "m5_value_max": 10.0,
                        "trainer_win_rate_min": 0.05,
                        "jockey_win_rate_min": 0.04,
                        "recent_form_min": 0,
                        "excel_algo_score_min": 50
                    }
                },
                "D": {
                    "description": "低評価",
                    "conditions": {
                        "win_score_min": 0.1,
                        "m5_value_max": 15.0,
                        "trainer_win_rate_min": 0.03,
                        "jockey_win_rate_min": 0.02,
                        "recent_form_min": 0,
                        "excel_algo_score_min": 30
                    }
                },
                "E": {
                    "description": "最低評価",
                    "conditions": {}
                }
            },
            "invest_grades": ["S", "A"],
            "version": "1.0",
            "created_date": datetime.now().isoformat()
        }
        
        if not os.path.exists(config_path):
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_rules, f, ensure_ascii=False, indent=2)
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def evaluate_horse(self, year: str, monthday: str, jyo_cd: str, race_num: str, umaban: str) -> Tuple[str, Dict]:
        """指定された馬の評価を実行"""
        
        # 基本データの取得
        horse_data = self._get_horse_basic_data(year, monthday, jyo_cd, race_num, umaban)
        if not horse_data:
            return 'E', {'error': 'Horse data not found'}
        
        # エクセルデータの取得
        excel_data = self._get_excel_data(year, monthday, horse_data['horse_name'])
        
        # 過去成績データの取得
        performance_data = self._get_performance_data(horse_data['ketto_num'])
        
        # 評価スコアの計算
        evaluation_scores = self._calculate_evaluation_scores(horse_data, excel_data, performance_data)
        
        # ランク判定
        rank = self._determine_rank(evaluation_scores)
        
        return rank, {
            'horse_name': horse_data['horse_name'],
            'evaluation_scores': evaluation_scores,
            'excel_data_available': excel_data is not None,
            'performance_races': len(performance_data) if performance_data else 0
        }
    
    def _get_horse_basic_data(self, year: str, monthday: str, jyo_cd: str, race_num: str, umaban: str) -> Optional[Dict]:
        """馬の基本データを取得"""
        try:
            conn = sqlite3.connect(self.ecore_db_path)
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    UR.KettoNum,
                    UR.Bamei,
                    UR.KisyuRyakusyo,
                    UR.ChokyosiRyakusyo,
                    UR.Odds,
                    UR.Ninki,
                    R.Kyori,
                    R.TrackCD,
                    R.GradeCD
                FROM N_UMA_RACE UR
                JOIN N_RACE R ON UR.Year = R.Year 
                    AND UR.MonthDay = R.MonthDay 
                    AND UR.JyoCD = R.JyoCD 
                    AND UR.RaceNum = R.RaceNum
                WHERE UR.Year = ? AND UR.MonthDay = ? 
                    AND UR.JyoCD = ? AND UR.RaceNum = ? AND UR.Umaban = ?
            """
            
            cursor.execute(query, (year, monthday, jyo_cd, race_num, umaban))
            result = cursor.fetchone()
            
            if result:
                return {
                    'ketto_num': result[0],
                    'horse_name': result[1],
                    'jockey': result[2],
                    'trainer': result[3],
                    'odds': float(result[4]) if result[4] else 999.0,
                    'popularity': int(result[5]) if result[5] else 99,
                    'distance': int(result[6]) if result[6] else 0,
                    'track_cd': result[7],
                    'grade_cd': result[8]
                }
            
            conn.close()
            return None
            
        except Exception as e:
            print(f"Error getting horse basic data: {e}")
            return None
    
    def _get_excel_data(self, year: str, monthday: str, horse_name: str) -> Optional[Dict]:
        """エクセルデータを取得"""
        try:
            conn = sqlite3.connect(self.excel_db_path)
            cursor = conn.cursor()
            
            # テーブル名を構築
            table_name = f"EXCEL_DATA_{year}{monthday}"
            
            # テーブルの存在確認
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            if not cursor.fetchone():
                conn.close()
                return None
            
            # データ取得（実際に存在するカラム名を使用）
            query = f"""
                SELECT 
                    馬印1, 馬印2, 馬印3, 馬印4, 馬印5,
                    オリジナル, ZM, ZI指数, 加速, 前人気,
                    騎手, 前着順, 前着差, 単勝
                FROM {table_name}
                WHERE 馬名S = ?
            """
            
            cursor.execute(query, (horse_name,))
            result = cursor.fetchone()
            
            if result:
                return {
                    'mark1': result[0], 'mark2': result[1], 'mark3': result[2], 
                    'mark4': result[3], 'mark5': result[4],
                    'algo_score': float(result[5]) if result[5] and str(result[5]).replace('.', '').replace('-', '').isdigit() else 0.0,  # オリジナル点数
                    'zm_value': float(result[6]) if result[6] and str(result[6]).replace('.', '').isdigit() else 100.0,
                    'zi_value': float(result[7]) if result[7] and str(result[7]).replace('.', '').isdigit() else 0.0,
                    'm5_value': float(result[8]) if result[8] and str(result[8]).replace('.', '').replace('-', '').isdigit() else 10.0,  # 加速点数
                    'trainer_win_rate': 0.1,  # デフォルト値（エクセルにない場合）
                    'jockey_win_rate': 0.05,  # デフォルト値（エクセルにない場合）
                    'prev_rank': int(result[11]) if result[11] and str(result[11]).isdigit() else 99,  # 前着順
                    'prev_popularity': int(result[9]) if result[9] and str(result[9]).isdigit() else 99,  # 前人気
                    'prev_odds': float(result[13]) if result[13] and str(result[13]).replace('.', '').isdigit() else 999.0  # 単勝オッズ
                }
            
            conn.close()
            return None
            
        except Exception as e:
            print(f"Error getting excel data: {e}")
            return None
    
    def _get_performance_data(self, ketto_num: str) -> List[Dict]:
        """過去成績データを取得"""
        try:
            conn = sqlite3.connect(self.ecore_db_path)
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    Year, MonthDay, JyoCD, RaceNum, KakuteiJyuni, Ninki, Odds,
                    Honsyokin, Time
                FROM N_UMA_RACE 
                WHERE KettoNum = ? AND KakuteiJyuni IS NOT NULL
                ORDER BY Year DESC, MonthDay DESC
                LIMIT 10
            """
            
            cursor.execute(query, (ketto_num,))
            results = cursor.fetchall()
            
            performance_list = []
            for result in results:
                performance_list.append({
                    'year': result[0],
                    'monthday': result[1],
                    'jyo_cd': result[2],
                    'race_num': result[3],
                    'rank': int(result[4]) if result[4] else 99,
                    'popularity': int(result[5]) if result[5] else 99,
                    'odds': float(result[6]) if result[6] else 999.0,
                    'prize': int(result[7]) if result[7] else 0,
                    'time': result[8]
                })
            
            conn.close()
            return performance_list
            
        except Exception as e:
            print(f"Error getting performance data: {e}")
            return []
    
    def _calculate_evaluation_scores(self, horse_data: Dict, excel_data: Optional[Dict], performance_data: List[Dict]) -> Dict:
        """評価スコアを計算"""
        scores = {
            'win_score': 0.0,
            'm5_value': 10.0,
            'trainer_win_rate': 0.0,
            'jockey_win_rate': 0.0,
            'recent_form': 0,
            'excel_algo_score': 0.0
        }
        
        # エクセルデータからのスコア
        if excel_data:
            scores['m5_value'] = excel_data['m5_value']  # 加速点数（低いほど良い）
            scores['trainer_win_rate'] = excel_data['trainer_win_rate']  # デフォルト値使用
            scores['jockey_win_rate'] = excel_data['jockey_win_rate']  # デフォルト値使用
            scores['excel_algo_score'] = excel_data['algo_score']  # オリジナル点数
            scores['zi_value'] = excel_data['zi_value']  # ZI指数（高いほど良い）
            scores['zm_value'] = excel_data['zm_value']  # ZM値
            
            # 馬印2（アルゴスピード指数順位）による補正
            mark2 = excel_data.get('mark2', '')
            if mark2 and str(mark2).isdigit():
                mark2_rank = int(mark2)
                if mark2_rank <= 3:  # 上位3位以内
                    scores['excel_algo_score'] += 10  # ボーナス
                elif mark2_rank <= 6:  # 6位以内
                    scores['excel_algo_score'] += 5
        
        # 過去成績からの勝率計算
        if performance_data:
            wins = sum(1 for p in performance_data if p['rank'] == 1)
            total_races = len(performance_data)
            scores['win_score'] = wins / total_races if total_races > 0 else 0.0
            
            # 最近の調子（直近3走での3着以内率）
            recent_3 = performance_data[:3]
            if recent_3:
                good_results = sum(1 for p in recent_3 if p['rank'] <= 3)
                scores['recent_form'] = good_results
        
        # 人気とオッズからの補正
        if horse_data['popularity'] <= 3:
            scores['win_score'] += 0.1  # 人気馬にボーナス
        
        if horse_data['odds'] <= 3.0:
            scores['win_score'] += 0.1  # 低オッズ馬にボーナス
        
        return scores
    
    def _determine_rank(self, scores: Dict) -> str:
        """スコアに基づいてランクを決定"""
        rules = self.rank_rules['logic1_rules']
        
        # S→A→B→C→D→Eの順で判定
        for rank in ['S', 'A', 'B', 'C', 'D']:
            if rank not in rules:
                continue
            
            conditions = rules[rank]['conditions']
            meets_all_conditions = True
            
            for condition, threshold in conditions.items():
                if condition.endswith('_min'):
                    score_key = condition.replace('_min', '')
                    if scores.get(score_key, 0) < threshold:
                        meets_all_conditions = False
                        break
                elif condition.endswith('_max'):
                    score_key = condition.replace('_max', '')
                    if scores.get(score_key, 999) > threshold:
                        meets_all_conditions = False
                        break
            
            if meets_all_conditions:
                return rank
        
        return 'E'  # どの条件も満たさない場合
    
    def evaluate_race_horses(self, year: str, monthday: str, jyo_cd: str, race_num: str) -> List[Dict]:
        """レース内の全馬を評価"""
        try:
            conn = sqlite3.connect(self.ecore_db_path)
            cursor = conn.cursor()
            
            # レース内の全馬を取得
            query = """
                SELECT Umaban, Bamei 
                FROM N_UMA_RACE 
                WHERE Year = ? AND MonthDay = ? AND JyoCD = ? AND RaceNum = ?
                ORDER BY Umaban
            """
            
            cursor.execute(query, (year, monthday, jyo_cd, race_num))
            horses = cursor.fetchall()
            conn.close()
            
            results = []
            for umaban, bamei in horses:
                rank, details = self.evaluate_horse(year, monthday, jyo_cd, race_num, str(umaban))
                
                results.append({
                    'umaban': umaban,
                    'horse_name': bamei,
                    'rank': rank,
                    'is_investment_target': rank in self.rank_rules.get('invest_grades', ['S', 'A']),
                    'details': details
                })
            
            return results
            
        except Exception as e:
            print(f"Error evaluating race horses: {e}")
            return []

def main():
    """テスト実行"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ロジック1馬評価システム')
    parser.add_argument('--date', required=True, help='評価日 (YYYY-MM-DD)')
    parser.add_argument('--jyo', help='場コード (例: 05)')
    parser.add_argument('--race', help='レース番号 (例: 11)')
    
    args = parser.parse_args()
    
    # パスの設定
    base_dir = os.path.dirname(os.path.dirname(__file__))
    ecore_db = os.path.join(base_dir, 'ecore.db')
    excel_db = os.path.join(base_dir, 'excel_data.db')
    
    # 日付の変換
    date_parts = args.date.split('-')
    year = date_parts[0]
    monthday = date_parts[1] + date_parts[2]
    
    # 評価システムの初期化
    logic1 = Logic1RankingSystem(ecore_db, excel_db)
    
    print(f"=== ロジック1評価システム ({args.date}) ===")
    
    if args.jyo and args.race:
        # 指定レースの評価
        results = logic1.evaluate_race_horses(year, monthday, args.jyo, args.race)
        
        print(f"\n{year}/{monthday} 場{args.jyo} {args.race}R 評価結果:")
        print("馬番 | ランク | 馬名 | 投資対象")
        print("-" * 40)
        
        for result in results:
            invest_mark = "★" if result['is_investment_target'] else " "
            print(f"{int(result['umaban']):2d}番 | {result['rank']:4s} | {result['horse_name']:12s} | {invest_mark}")
    
    else:
        # 指定日の全レース評価
        conn = sqlite3.connect(ecore_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT JyoCD, RaceNum 
            FROM N_RACE 
            WHERE Year = ? AND MonthDay = ?
            ORDER BY JyoCD, RaceNum
        """, (year, monthday))
        
        races = cursor.fetchall()
        conn.close()
        
        total_investment_targets = 0
        
        for jyo_cd, race_num in races:
            results = logic1.evaluate_race_horses(year, monthday, jyo_cd, str(race_num))
            investment_targets = [r for r in results if r['is_investment_target']]
            
            if investment_targets:
                print(f"\n場{jyo_cd} {race_num}R - 投資対象: {len(investment_targets)}頭")
                for target in investment_targets:
                    print(f"  {int(target['umaban']):2d}番 {target['rank']} {target['horse_name']}")
                
                total_investment_targets += len(investment_targets)
        
        print(f"\n=== 総投資対象数: {total_investment_targets}頭 ===")

if __name__ == "__main__":
    main()
