#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
M5による第一段階振り分けシステム
芝：1-2位、ダート：1位が絶対条件
"""
import sqlite3
import os
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class M5PrimaryFilter:
    """M5評価による第一段階フィルター"""
    
    def __init__(self, ecore_db_path: str, excel_db_path: str):
        self.ecore_db_path = ecore_db_path
        self.excel_db_path = excel_db_path
        self.log_file = os.path.join(os.path.dirname(__file__), 'logs', 'm5_filter_log.json')
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
    
    def filter_race_by_m5(self, year: str, monthday: str, jyo_cd: str, race_num: str) -> Dict:
        """レース内でM5による第一段階フィルタリング"""
        
        result = {
            'race_info': f"{year}/{monthday} 場{jyo_cd} {race_num}R",
            'track_type': None,
            'total_horses': 0,
            'qualified_horses': [],
            'disqualified_horses': [],
            'filter_applied': False,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # レース情報取得（芝・ダート判定）
            track_type = self._get_track_type(year, monthday, jyo_cd, race_num)
            result['track_type'] = track_type
            
            if not track_type:
                result['error'] = 'レース情報が取得できません'
                return result
            
            # 出走馬とM5データ取得
            horses_m5_data = self._get_horses_m5_data(year, monthday, jyo_cd, race_num)
            result['total_horses'] = len(horses_m5_data)
            
            if not horses_m5_data:
                result['error'] = 'M5データが取得できません'
                return result
            
            # M5順位でソート（加速点数が低いほど良い）
            horses_m5_data.sort(key=lambda x: x['m5_value'] if x['m5_value'] is not None else 999)
            
            # フィルタリング条件適用
            if track_type == '芝':
                # 芝：1-2位が条件
                qualified_positions = [1, 2]
                condition_text = "芝レース：M5評価1-2位"
            else:
                # ダート：1位のみが条件
                qualified_positions = [1]
                condition_text = "ダートレース：M5評価1位のみ"
            
            # 条件に合致する馬を抽出
            for i, horse in enumerate(horses_m5_data):
                position = i + 1
                horse_info = {
                    'umaban': horse['umaban'],
                    'horse_name': horse['horse_name'],
                    'm5_value': horse['m5_value'],
                    'm5_position': position,
                    'excel_data_available': horse['excel_data_available']
                }
                
                if position in qualified_positions:
                    result['qualified_horses'].append(horse_info)
                else:
                    result['disqualified_horses'].append(horse_info)
            
            result['filter_applied'] = True
            result['condition'] = condition_text
            result['qualified_count'] = len(result['qualified_horses'])
            
            # ログ記録
            self._log_filter_result(result)
            
            return result
            
        except Exception as e:
            result['error'] = str(e)
            return result
    
    def _get_track_type(self, year: str, monthday: str, jyo_cd: str, race_num: str) -> Optional[str]:
        """レースの芝・ダート判定"""
        try:
            conn = sqlite3.connect(self.ecore_db_path)
            cursor = conn.cursor()
            
            query = """
                SELECT TrackCD FROM N_RACE 
                WHERE Year = ? AND MonthDay = ? AND JyoCD = ? AND RaceNum = ?
            """
            
            cursor.execute(query, (year, monthday, jyo_cd, race_num))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                track_cd = result[0]
                # TrackCD: 1x=芝, 2x=ダート, 3x=障害
                if track_cd and str(track_cd).startswith('1'):
                    return '芝'
                elif track_cd and str(track_cd).startswith('2'):
                    return 'ダート'
                elif track_cd and str(track_cd).startswith('3'):
                    return '障害'
            
            return None
            
        except Exception as e:
            print(f"Error getting track type: {e}")
            return None
    
    def _get_horses_m5_data(self, year: str, monthday: str, jyo_cd: str, race_num: str) -> List[Dict]:
        """レース内全馬のM5データ取得"""
        horses_data = []
        
        try:
            # ecore.dbから出走馬一覧取得
            ecore_conn = sqlite3.connect(self.ecore_db_path)
            ecore_cursor = ecore_conn.cursor()
            
            query = """
                SELECT Umaban, Bamei FROM N_UMA_RACE 
                WHERE Year = ? AND MonthDay = ? AND JyoCD = ? AND RaceNum = ?
                ORDER BY Umaban
            """
            
            ecore_cursor.execute(query, (year, monthday, jyo_cd, race_num))
            horses = ecore_cursor.fetchall()
            ecore_conn.close()
            
            # excel_data.dbからM5データ取得
            excel_conn = sqlite3.connect(self.excel_db_path)
            excel_cursor = excel_conn.cursor()
            
            table_name = f"EXCEL_DATA_{year}{monthday}"
            
            # テーブル存在確認
            excel_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            if not excel_cursor.fetchone():
                excel_conn.close()
                # エクセルデータがない場合はecore.dbのデータのみ返す
                return [{'umaban': h[0], 'horse_name': h[1], 'm5_value': None, 'excel_data_available': False} for h in horses]
            
            for umaban, horse_name in horses:
                # M5データ（加速点数）を取得
                query = f"""
                    SELECT 加速 FROM {table_name} WHERE 馬名S = ?
                """
                
                excel_cursor.execute(query, (horse_name,))
                m5_result = excel_cursor.fetchone()
                
                m5_value = None
                if m5_result and m5_result[0] is not None:
                    try:
                        # 数値変換（文字列の場合もある）
                        m5_str = str(m5_result[0]).replace('-', '').replace('.', '')
                        if m5_str.isdigit():
                            m5_value = float(m5_result[0])
                    except:
                        pass
                
                horses_data.append({
                    'umaban': umaban,
                    'horse_name': horse_name,
                    'm5_value': m5_value,
                    'excel_data_available': m5_result is not None
                })
            
            excel_conn.close()
            return horses_data
            
        except Exception as e:
            print(f"Error getting horses M5 data: {e}")
            return []
    
    def _log_filter_result(self, result: Dict):
        """フィルター結果をログに記録"""
        try:
            # 既存ログ読み込み
            logs = []
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            
            # 新しいログ追加
            logs.append(result)
            
            # 最新100件のみ保持
            if len(logs) > 100:
                logs = logs[-100:]
            
            # ログ保存
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Error logging filter result: {e}")
    
    def filter_daily_races(self, year: str, monthday: str) -> Dict:
        """指定日の全レースにM5フィルター適用"""
        
        daily_result = {
            'date': f"{year}/{monthday}",
            'total_races': 0,
            'turf_races': 0,
            'dirt_races': 0,
            'total_qualified': 0,
            'races': [],
            'summary': {},
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # 指定日のレース一覧取得
            conn = sqlite3.connect(self.ecore_db_path)
            cursor = conn.cursor()
            
            query = """
                SELECT DISTINCT JyoCD, RaceNum FROM N_RACE 
                WHERE Year = ? AND MonthDay = ?
                ORDER BY JyoCD, RaceNum
            """
            
            cursor.execute(query, (year, monthday))
            races = cursor.fetchall()
            conn.close()
            
            daily_result['total_races'] = len(races)
            
            # 各レースにフィルター適用
            for jyo_cd, race_num in races:
                race_result = self.filter_race_by_m5(year, monthday, jyo_cd, str(race_num))
                daily_result['races'].append(race_result)
                
                if race_result.get('filter_applied'):
                    daily_result['total_qualified'] += race_result.get('qualified_count', 0)
                    
                    if race_result.get('track_type') == '芝':
                        daily_result['turf_races'] += 1
                    elif race_result.get('track_type') == 'ダート':
                        daily_result['dirt_races'] += 1
            
            # サマリー作成
            daily_result['summary'] = {
                '芝レース数': daily_result['turf_races'],
                'ダートレース数': daily_result['dirt_races'],
                '総投資対象数': daily_result['total_qualified'],
                '平均投資対象率': f"{daily_result['total_qualified'] / (daily_result['turf_races'] * 2 + daily_result['dirt_races'] * 1) * 100:.1f}%" if (daily_result['turf_races'] + daily_result['dirt_races']) > 0 else "0%"
            }
            
            return daily_result
            
        except Exception as e:
            daily_result['error'] = str(e)
            return daily_result

def main():
    """テスト実行"""
    import argparse
    
    parser = argparse.ArgumentParser(description='M5第一段階フィルター')
    parser.add_argument('--date', required=True, help='対象日 (YYYY-MM-DD)')
    parser.add_argument('--jyo', help='場コード')
    parser.add_argument('--race', help='レース番号')
    
    args = parser.parse_args()
    
    # パス設定
    base_dir = os.path.dirname(os.path.dirname(__file__))
    ecore_db = os.path.join(base_dir, 'ecore.db')
    excel_db = os.path.join(base_dir, 'excel_data.db')
    
    # 日付変換
    date_parts = args.date.split('-')
    year = date_parts[0]
    monthday = date_parts[1] + date_parts[2]
    
    # フィルター初期化
    m5_filter = M5PrimaryFilter(ecore_db, excel_db)
    
    print(f"=== M5第一段階フィルター ({args.date}) ===")
    print("条件: 芝レース=M5評価1-2位、ダートレース=M5評価1位のみ")
    
    if args.jyo and args.race:
        # 単一レース
        result = m5_filter.filter_race_by_m5(year, monthday, args.jyo, args.race)
        
        print(f"\\n{result['race_info']} ({result.get('track_type', '不明')})")
        
        if result.get('filter_applied'):
            print(f"条件: {result.get('condition')}")
            print(f"総出走: {result['total_horses']}頭")
            print(f"投資対象: {result['qualified_count']}頭")
            
            print("\\n✅ 投資対象馬:")
            for horse in result['qualified_horses']:
                print(f"  {int(horse['umaban']):2d}番 {horse['horse_name']:12s} M5={horse['m5_value']} (順位:{horse['m5_position']})")
        else:
            print(f"❌ エラー: {result.get('error', '不明')}")
    
    else:
        # 全レース
        daily_result = m5_filter.filter_daily_races(year, monthday)
        
        print(f"\\n📊 {daily_result['date']} 全レース結果:")
        print(f"総レース数: {daily_result['total_races']}")
        print(f"芝レース: {daily_result['turf_races']}R")
        print(f"ダートレース: {daily_result['dirt_races']}R")
        print(f"総投資対象: {daily_result['total_qualified']}頭")
        
        print("\\n🎯 投資対象一覧:")
        for race in daily_result['races']:
            if race.get('qualified_count', 0) > 0:
                print(f"\\n{race['race_info']} ({race.get('track_type')})")
                for horse in race['qualified_horses']:
                    print(f"  {int(horse['umaban']):2d}番 {horse['horse_name']:12s} M5={horse['m5_value']}")

if __name__ == "__main__":
    main()
