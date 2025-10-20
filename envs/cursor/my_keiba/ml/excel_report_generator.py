#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
開催日データに基づくエクセルレポート自動生成
ロジック1評価結果をExcelレポートとして出力
"""
import sqlite3
import pandas as pd
import os
from datetime import datetime
from typing import Dict, List
import argparse

import sys
import os
sys.path.append(os.path.dirname(__file__))
from logic1_ranking_system import Logic1RankingSystem

class ExcelReportGenerator:
    """エクセルレポート生成クラス"""
    
    def __init__(self, ecore_db_path: str, excel_db_path: str):
        self.ecore_db_path = ecore_db_path
        self.excel_db_path = excel_db_path
        self.logic1 = Logic1RankingSystem(ecore_db_path, excel_db_path)
        
        # JyoCD マッピング
        self.jyo_names = {
            '01': '札幌', '02': '函館', '03': '福島', '04': '新潟', '05': '東京',
            '06': '中山', '07': '中京', '08': '京都', '09': '阪神', '10': '小倉',
            '30': '門別', '31': '盛岡', '32': '水沢', '33': '浦和', '34': '船橋',
            '35': '大井', '36': '川崎', '37': '金沢', '38': '笠松', '39': '名古屋',
            '40': '園田', '41': '姫路', '42': '高知', '43': '佐賀'
        }
    
    def generate_daily_report(self, year: str, monthday: str, output_path: str = None) -> str:
        """指定日の全レース評価レポートを生成"""
        
        if not output_path:
            output_path = f"reports/logic1_report_{year}{monthday}.xlsx"
        
        # ディレクトリ作成
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # レース一覧を取得
        races = self._get_races_for_date(year, monthday)
        
        if not races:
            print(f"[WARN] {year}/{monthday} のレースデータが見つかりません")
            return ""
        
        # 各シート用のデータを準備
        all_evaluations = []
        investment_targets = []
        venue_summary = {}
        rank_distribution = {'S': 0, 'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0}
        
        print(f"=== {year}/{monthday} ロジック1評価レポート生成中 ===")
        
        for race in races:
            jyo_cd, race_num, race_name, distance, track_cd = race
            jyo_name = self.jyo_names.get(jyo_cd, f"場{jyo_cd}")
            
            # レース内全馬評価
            horse_evaluations = self.logic1.evaluate_race_horses(year, monthday, jyo_cd, str(race_num))
            
            # データ整理
            for evaluation in horse_evaluations:
                # 全評価データ
                all_evaluations.append({
                    '日付': f"{year}/{monthday}",
                    '開催場': jyo_name,
                    'レース': f"{race_num}R",
                    'レース名': race_name or f"{race_num}R",
                    '距離': f"{distance}m" if distance else "",
                    'トラック': track_cd or "",
                    '馬番': evaluation['umaban'],
                    '馬名': evaluation['horse_name'],
                    'ランク': evaluation['rank'],
                    '投資対象': "★" if evaluation['is_investment_target'] else "",
                    'エクセルデータ': "○" if evaluation['details'].get('excel_data_available') else "×",
                    '過去レース数': evaluation['details'].get('performance_races', 0)
                })
                
                # 投資対象データ
                if evaluation['is_investment_target']:
                    investment_targets.append({
                        '日付': f"{year}/{monthday}",
                        '開催場': jyo_name,
                        'レース': f"{race_num}R",
                        'レース名': race_name or f"{race_num}R",
                        '馬番': evaluation['umaban'],
                        '馬名': evaluation['horse_name'],
                        'ランク': evaluation['rank'],
                        '推奨投資額': 100 if evaluation['rank'] == 'S' else 100,  # 固定額
                        '備考': f"ロジック1-{evaluation['rank']}ランク"
                    })
                
                # ランク分布
                rank_distribution[evaluation['rank']] += 1
            
            # 会場別サマリー
            if jyo_name not in venue_summary:
                venue_summary[jyo_name] = {
                    'レース数': 0,
                    '総出走頭数': 0,
                    '投資対象数': 0,
                    'S': 0, 'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0
                }
            
            venue_summary[jyo_name]['レース数'] += 1
            venue_summary[jyo_name]['総出走頭数'] += len(horse_evaluations)
            venue_summary[jyo_name]['投資対象数'] += sum(1 for e in horse_evaluations if e['is_investment_target'])
            
            for evaluation in horse_evaluations:
                venue_summary[jyo_name][evaluation['rank']] += 1
        
        # Excelファイル生成
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            
            # 1. 全評価結果シート
            if all_evaluations:
                df_all = pd.DataFrame(all_evaluations)
                df_all.to_excel(writer, sheet_name='全評価結果', index=False)
            
            # 2. 投資対象シート
            if investment_targets:
                df_invest = pd.DataFrame(investment_targets)
                df_invest.to_excel(writer, sheet_name='投資対象', index=False)
            
            # 3. 会場別サマリーシート
            if venue_summary:
                venue_data = []
                for venue, data in venue_summary.items():
                    venue_data.append({
                        '開催場': venue,
                        'レース数': data['レース数'],
                        '総出走頭数': data['総出走頭数'],
                        '投資対象数': data['投資対象数'],
                        '投資対象率': f"{data['投資対象数']/data['総出走頭数']*100:.1f}%" if data['総出走頭数'] > 0 else "0%",
                        'Sランク': data['S'],
                        'Aランク': data['A'],
                        'Bランク': data['B'],
                        'Cランク': data['C'],
                        'Dランク': data['D'],
                        'Eランク': data['E']
                    })
                
                df_venue = pd.DataFrame(venue_data)
                df_venue.to_excel(writer, sheet_name='会場別サマリー', index=False)
            
            # 4. 全体サマリーシート
            summary_data = [
                {'項目': '評価日', '値': f"{year}/{monthday}"},
                {'項目': '開催場数', '値': len(venue_summary)},
                {'項目': '総レース数', '値': len(races)},
                {'項目': '総出走頭数', '値': len(all_evaluations)},
                {'項目': '投資対象数', '値': len(investment_targets)},
                {'項目': '投資対象率', '値': f"{len(investment_targets)/len(all_evaluations)*100:.1f}%" if all_evaluations else "0%"},
                {'項目': '', '値': ''},
                {'項目': 'ランク分布', '値': ''},
                {'項目': 'Sランク', '値': rank_distribution['S']},
                {'項目': 'Aランク', '値': rank_distribution['A']},
                {'項目': 'Bランク', '値': rank_distribution['B']},
                {'項目': 'Cランク', '値': rank_distribution['C']},
                {'項目': 'Dランク', '値': rank_distribution['D']},
                {'項目': 'Eランク', '値': rank_distribution['E']},
                {'項目': '', '値': ''},
                {'項目': 'ロジック', '値': 'ロジック1 (初回版)'},
                {'項目': '生成日時', '値': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            ]
            
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name='全体サマリー', index=False)
        
        print(f"✅ レポート生成完了: {output_path}")
        print(f"   総出走頭数: {len(all_evaluations)}頭")
        print(f"   投資対象数: {len(investment_targets)}頭")
        print(f"   投資対象率: {len(investment_targets)/len(all_evaluations)*100:.1f}%" if all_evaluations else "0%")
        
        return output_path
    
    def _get_races_for_date(self, year: str, monthday: str) -> List[tuple]:
        """指定日のレース一覧を取得"""
        try:
            conn = sqlite3.connect(self.ecore_db_path)
            cursor = conn.cursor()
            
            query = """
                SELECT JyoCD, RaceNum, Hondai, Kyori, TrackCD
                FROM N_RACE 
                WHERE Year = ? AND MonthDay = ?
                ORDER BY JyoCD, RaceNum
            """
            
            cursor.execute(query, (year, monthday))
            races = cursor.fetchall()
            conn.close()
            
            return races
            
        except Exception as e:
            print(f"Error getting races: {e}")
            return []
    
    def generate_period_report(self, date_from: str, date_to: str, output_path: str = None) -> str:
        """期間レポートを生成"""
        
        if not output_path:
            output_path = f"reports/logic1_period_report_{date_from.replace('-', '')}_{date_to.replace('-', '')}.xlsx"
        
        # 期間内の全日付を取得
        dates = self._get_dates_in_period(date_from, date_to)
        
        if not dates:
            print(f"[WARN] {date_from} ～ {date_to} の期間にレースデータが見つかりません")
            return ""
        
        print(f"=== {date_from} ～ {date_to} 期間レポート生成中 ===")
        
        all_data = []
        daily_summaries = []
        
        for year, monthday in dates:
            print(f"  処理中: {year}/{monthday}")
            
            # 日別レポートデータを取得
            races = self._get_races_for_date(year, monthday)
            
            daily_investment_count = 0
            daily_total_count = 0
            daily_rank_dist = {'S': 0, 'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0}
            
            for race in races:
                jyo_cd, race_num, race_name, distance, track_cd = race
                jyo_name = self.jyo_names.get(jyo_cd, f"場{jyo_cd}")
                
                horse_evaluations = self.logic1.evaluate_race_horses(year, monthday, jyo_cd, str(race_num))
                
                for evaluation in horse_evaluations:
                    all_data.append({
                        '日付': f"{year}/{monthday}",
                        '開催場': jyo_name,
                        'レース': f"{race_num}R",
                        '馬番': evaluation['umaban'],
                        '馬名': evaluation['horse_name'],
                        'ランク': evaluation['rank'],
                        '投資対象': "★" if evaluation['is_investment_target'] else ""
                    })
                    
                    daily_total_count += 1
                    daily_rank_dist[evaluation['rank']] += 1
                    
                    if evaluation['is_investment_target']:
                        daily_investment_count += 1
            
            # 日別サマリー
            daily_summaries.append({
                '日付': f"{year}/{monthday}",
                '総出走頭数': daily_total_count,
                '投資対象数': daily_investment_count,
                '投資対象率': f"{daily_investment_count/daily_total_count*100:.1f}%" if daily_total_count > 0 else "0%",
                'Sランク': daily_rank_dist['S'],
                'Aランク': daily_rank_dist['A'],
                'Bランク': daily_rank_dist['B'],
                'Cランク': daily_rank_dist['C'],
                'Dランク': daily_rank_dist['D'],
                'Eランク': daily_rank_dist['E']
            })
        
        # Excelファイル生成
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            
            # 全データシート
            if all_data:
                df_all = pd.DataFrame(all_data)
                df_all.to_excel(writer, sheet_name='期間全データ', index=False)
            
            # 日別サマリーシート
            if daily_summaries:
                df_daily = pd.DataFrame(daily_summaries)
                df_daily.to_excel(writer, sheet_name='日別サマリー', index=False)
            
            # 期間サマリーシート
            total_horses = len(all_data)
            total_investments = sum(1 for d in all_data if d['投資対象'] == "★")
            
            period_summary = [
                {'項目': '期間', '値': f"{date_from} ～ {date_to}"},
                {'項目': '対象日数', '値': len(dates)},
                {'項目': '総出走頭数', '値': total_horses},
                {'項目': '総投資対象数', '値': total_investments},
                {'項目': '平均投資対象率', '値': f"{total_investments/total_horses*100:.1f}%" if total_horses > 0 else "0%"},
                {'項目': 'ロジック', '値': 'ロジック1 (初回版)'},
                {'項目': '生成日時', '値': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            ]
            
            df_period = pd.DataFrame(period_summary)
            df_period.to_excel(writer, sheet_name='期間サマリー', index=False)
        
        print(f"✅ 期間レポート生成完了: {output_path}")
        print(f"   対象日数: {len(dates)}日")
        print(f"   総出走頭数: {total_horses}頭")
        print(f"   総投資対象数: {total_investments}頭")
        
        return output_path
    
    def _get_dates_in_period(self, date_from: str, date_to: str) -> List[tuple]:
        """期間内の日付一覧を取得"""
        try:
            conn = sqlite3.connect(self.ecore_db_path)
            cursor = conn.cursor()
            
            # 日付を変換
            from_date = date_from.replace('-', '')
            to_date = date_to.replace('-', '')
            
            query = """
                SELECT DISTINCT Year, MonthDay
                FROM N_RACE 
                WHERE Year || MonthDay BETWEEN ? AND ?
                ORDER BY Year, MonthDay
            """
            
            cursor.execute(query, (from_date, to_date))
            dates = cursor.fetchall()
            conn.close()
            
            return dates
            
        except Exception as e:
            print(f"Error getting dates in period: {e}")
            return []

def main():
    """メイン実行"""
    parser = argparse.ArgumentParser(description='ロジック1エクセルレポート生成')
    parser.add_argument('--date', help='単日レポート日付 (YYYY-MM-DD)')
    parser.add_argument('--date-from', help='期間レポート開始日 (YYYY-MM-DD)')
    parser.add_argument('--date-to', help='期間レポート終了日 (YYYY-MM-DD)')
    parser.add_argument('--output', help='出力ファイルパス')
    
    args = parser.parse_args()
    
    # パスの設定
    base_dir = os.path.dirname(os.path.dirname(__file__))
    ecore_db = os.path.join(base_dir, 'ecore.db')
    excel_db = os.path.join(base_dir, 'excel_data.db')
    
    # レポート生成器の初期化
    generator = ExcelReportGenerator(ecore_db, excel_db)
    
    if args.date:
        # 単日レポート
        date_parts = args.date.split('-')
        year = date_parts[0]
        monthday = date_parts[1] + date_parts[2]
        
        output_path = generator.generate_daily_report(year, monthday, args.output)
        
    elif args.date_from and args.date_to:
        # 期間レポート
        output_path = generator.generate_period_report(args.date_from, args.date_to, args.output)
        
    else:
        print("--date または --date-from と --date-to を指定してください")
        return
    
    if output_path:
        print(f"\n📊 レポートファイル: {output_path}")

if __name__ == "__main__":
    main()
