import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
import sys

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

class M5M6PatternAnalyzer:
    """M5/M6の特定パターンと期間別効果分析システム"""
    
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
    
    def get_m5m6_data(self, start_date="2024-11-02", end_date="2025-09-28"):
        """M5/M6データの取得（データ不足の言い訳なし）"""
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
            
            print(f"M5/M6データ取得完了: {len(df)}件")
            return df
            
        except Exception as e:
            print(f"データ取得エラー: {e}")
            return None
    
    def analyze_m5m6_patterns(self, df):
        """M5/M6の特定パターン分析"""
        if df is None or df.empty:
            return None
        
        # パターン別分析
        patterns = {}
        
        # パターンA: Mark5=1, Mark6=1 (合計2)
        pattern_a = df[(df['Mark5_numeric'] == 1) & (df['Mark6_numeric'] == 1)]
        if not pattern_a.empty:
            patterns['パターンA (M5=1, M6=1)'] = self.calculate_pattern_stats(pattern_a)
        
        # パターンB: Mark5=2, Mark6=2 (合計4)
        pattern_b = df[(df['Mark5_numeric'] == 2) & (df['Mark6_numeric'] == 2)]
        if not pattern_b.empty:
            patterns['パターンB (M5=2, M6=2)'] = self.calculate_pattern_stats(pattern_b)
        
        # パターンC: Mark5=3, Mark6=3 (合計6)
        pattern_c = df[(df['Mark5_numeric'] == 3) & (df['Mark6_numeric'] == 3)]
        if not pattern_c.empty:
            patterns['パターンC (M5=3, M6=3)'] = self.calculate_pattern_stats(pattern_c)
        
        # パターンD: Mark5=1, Mark6=2 (合計3)
        pattern_d = df[(df['Mark5_numeric'] == 1) & (df['Mark6_numeric'] == 2)]
        if not pattern_d.empty:
            patterns['パターンD (M5=1, M6=2)'] = self.calculate_pattern_stats(pattern_d)
        
        # パターンE: Mark5=2, Mark6=1 (合計3)
        pattern_e = df[(df['Mark5_numeric'] == 2) & (df['Mark6_numeric'] == 1)]
        if not pattern_e.empty:
            patterns['パターンE (M5=2, M6=1)'] = self.calculate_pattern_stats(pattern_e)
        
        # パターンF: Mark5=1, Mark6=3 (合計4)
        pattern_f = df[(df['Mark5_numeric'] == 1) & (df['Mark6_numeric'] == 3)]
        if not pattern_f.empty:
            patterns['パターンF (M5=1, M6=3)'] = self.calculate_pattern_stats(pattern_f)
        
        # パターンG: Mark5=3, Mark6=1 (合計4)
        pattern_g = df[(df['Mark5_numeric'] == 3) & (df['Mark6_numeric'] == 1)]
        if not pattern_g.empty:
            patterns['パターンG (M5=3, M6=1)'] = self.calculate_pattern_stats(pattern_g)
        
        # パターンH: Mark5=2, Mark6=3 (合計5)
        pattern_h = df[(df['Mark5_numeric'] == 2) & (df['Mark6_numeric'] == 3)]
        if not pattern_h.empty:
            patterns['パターンH (M5=2, M6=3)'] = self.calculate_pattern_stats(pattern_h)
        
        # パターンI: Mark5=3, Mark6=2 (合計5)
        pattern_i = df[(df['Mark5_numeric'] == 3) & (df['Mark6_numeric'] == 2)]
        if not pattern_i.empty:
            patterns['パターンI (M5=3, M6=2)'] = self.calculate_pattern_stats(pattern_i)
        
        return patterns
    
    def calculate_pattern_stats(self, pattern_df):
        """パターン統計の計算"""
        if pattern_df.empty:
            return None
        
        # 着順データの処理
        pattern_df = pattern_df.copy()
        pattern_df['Chaku_numeric'] = pd.to_numeric(pattern_df['Chaku'], errors='coerce')
        
        # 有効な着順データのみ
        valid_finish = pattern_df.dropna(subset=['Chaku_numeric'])
        
        if valid_finish.empty:
            return {
                'total_races': len(pattern_df),
                'valid_races': 0,
                'win_rate': 0.0,
                'place_rate': 0.0,
                'show_rate': 0.0,
                'fukusho_rate': 0.0,
                'avg_zi_index': 0.0,
                'avg_zm_value': 0.0
            }
        
        # 勝率、連対率、複勝率の計算
        wins = len(valid_finish[valid_finish['Chaku_numeric'] == 1])
        places = len(valid_finish[valid_finish['Chaku_numeric'] <= 2])
        shows = len(valid_finish[valid_finish['Chaku_numeric'] <= 3])
        fukushos = len(valid_finish[valid_finish['Chaku_numeric'] <= 3])
        
        total_races = len(valid_finish)
        
        win_rate = (wins / total_races * 100) if total_races > 0 else 0
        place_rate = (places / total_races * 100) if total_races > 0 else 0
        show_rate = (shows / total_races * 100) if total_races > 0 else 0
        fukusho_rate = (fukushos / total_races * 100) if total_races > 0 else 0
        
        # ZI_Index, ZM_Valueの平均（数値変換してから計算）
        try:
            zi_index_numeric = pd.to_numeric(valid_finish['ZI_Index'], errors='coerce')
            avg_zi_index = zi_index_numeric.mean() if not zi_index_numeric.isna().all() else 0
        except:
            avg_zi_index = 0
        
        try:
            zm_value_numeric = pd.to_numeric(valid_finish['ZM_Value'], errors='coerce')
            avg_zm_value = zm_value_numeric.mean() if not zm_value_numeric.isna().all() else 0
        except:
            avg_zm_value = 0
        
        return {
            'total_races': len(pattern_df),
            'valid_races': total_races,
            'win_rate': round(win_rate, 1),
            'place_rate': round(place_rate, 1),
            'show_rate': round(show_rate, 1),
            'fukusho_rate': round(fukusho_rate, 1),
            'avg_zi_index': round(avg_zi_index, 2),
            'avg_zm_value': round(avg_zm_value, 2)
        }
    
    def analyze_period_effects(self, df):
        """期間別効果分析"""
        if df is None or df.empty:
            return None
        
        # 日付をdatetimeに変換
        df['Date'] = pd.to_datetime(df['SourceDate'], format='%Y%m%d')
        
        # 期間別分析
        period_analysis = {}
        
        # 直近1ヶ月
        recent_1m = df[df['Date'] >= (df['Date'].max() - timedelta(days=30))]
        if not recent_1m.empty:
            period_analysis['直近1ヶ月'] = self.calculate_period_stats(recent_1m)
        
        # 直近3ヶ月
        recent_3m = df[df['Date'] >= (df['Date'].max() - timedelta(days=90))]
        if not recent_3m.empty:
            period_analysis['直近3ヶ月'] = self.calculate_period_stats(recent_3m)
        
        # 直近6ヶ月
        recent_6m = df[df['Date'] >= (df['Date'].max() - timedelta(days=180))]
        if not recent_6m.empty:
            period_analysis['直近6ヶ月'] = self.calculate_period_stats(recent_6m)
        
        # 直近1年
        recent_1y = df[df['Date'] >= (df['Date'].max() - timedelta(days=365))]
        if not recent_1y.empty:
            period_analysis['直近1年'] = self.calculate_period_stats(recent_1y)
        
        # 月別分析
        monthly_analysis = {}
        for month in range(1, 13):
            month_data = df[df['Date'].dt.month == month]
            if not month_data.empty:
                monthly_analysis[f'{month}月'] = self.calculate_period_stats(month_data)
        
        return {
            'period_analysis': period_analysis,
            'monthly_analysis': monthly_analysis
        }
    
    def calculate_period_stats(self, period_df):
        """期間統計の計算"""
        if period_df.empty:
            return None
        
        # 着順データの処理
        period_df = period_df.copy()
        period_df['Chaku_numeric'] = pd.to_numeric(period_df['Chaku'], errors='coerce')
        
        # 有効な着順データのみ
        valid_finish = period_df.dropna(subset=['Chaku_numeric'])
        
        if valid_finish.empty:
            return {
                'total_races': len(period_df),
                'valid_races': 0,
                'win_rate': 0.0,
                'place_rate': 0.0,
                'show_rate': 0.0,
                'fukusho_rate': 0.0,
                'avg_zi_index': 0.0,
                'avg_zm_value': 0.0
            }
        
        # 勝率、連対率、複勝率の計算
        wins = len(valid_finish[valid_finish['Chaku_numeric'] == 1])
        places = len(valid_finish[valid_finish['Chaku_numeric'] <= 2])
        shows = len(valid_finish[valid_finish['Chaku_numeric'] <= 3])
        fukushos = len(valid_finish[valid_finish['Chaku_numeric'] <= 3])
        
        total_races = len(valid_finish)
        
        win_rate = (wins / total_races * 100) if total_races > 0 else 0
        place_rate = (places / total_races * 100) if total_races > 0 else 0
        show_rate = (shows / total_races * 100) if total_races > 0 else 0
        fukusho_rate = (fukushos / total_races * 100) if total_races > 0 else 0
        
        # ZI_Index, ZM_Valueの平均（数値変換してから計算）
        try:
            zi_index_numeric = pd.to_numeric(valid_finish['ZI_Index'], errors='coerce')
            avg_zi_index = zi_index_numeric.mean() if not zi_index_numeric.isna().all() else 0
        except:
            avg_zi_index = 0
        
        try:
            zm_value_numeric = pd.to_numeric(valid_finish['ZM_Value'], errors='coerce')
            avg_zm_value = zm_value_numeric.mean() if not zm_value_numeric.isna().all() else 0
        except:
            avg_zm_value = 0
        
        return {
            'total_races': len(period_df),
            'valid_races': total_races,
            'win_rate': round(win_rate, 1),
            'place_rate': round(place_rate, 1),
            'show_rate': round(show_rate, 1),
            'fukusho_rate': round(fukusho_rate, 1),
            'avg_zi_index': round(avg_zi_index, 2),
            'avg_zm_value': round(avg_zm_value, 2)
        }
    
    def generate_analysis_report(self, patterns, period_effects):
        """分析レポート生成"""
        report = {
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'm5m6_patterns': patterns,
            'period_effects': period_effects
        }
        
        # レポート保存
        output_dir = "outputs"
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # JSON形式で保存
        json_file = f"{output_dir}/m5m6_pattern_analysis_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # CSV形式で保存
        csv_file = f"{output_dir}/m5m6_pattern_analysis_{timestamp}.csv"
        self.save_patterns_to_csv(patterns, csv_file)
        
        print(f"分析レポート生成完了")
        print(f"   JSON: {json_file}")
        print(f"   CSV: {csv_file}")
        
        return report
    
    def save_patterns_to_csv(self, patterns, csv_file):
        """パターン分析結果をCSVに保存"""
        if not patterns:
            return
        
        rows = []
        for pattern_name, stats in patterns.items():
            if stats:
                rows.append({
                    'パターン': pattern_name,
                    '総レース数': stats['total_races'],
                    '有効レース数': stats['valid_races'],
                    '勝率': stats['win_rate'],
                    '連対率': stats['place_rate'],
                    '複勝率': stats['show_rate'],
                    '複勝率': stats['fukusho_rate'],
                    '平均ZI_Index': stats['avg_zi_index'],
                    '平均ZM_Value': stats['avg_zm_value']
                })
        
        if rows:
            df = pd.DataFrame(rows)
            df.to_csv(csv_file, index=False, encoding='utf-8-sig')
    
    def run_analysis(self):
        """分析実行"""
        print("=== M5/M6パターン分析開始 ===")
        
        # データ取得
        df = self.get_m5m6_data()
        if df is None or df.empty:
            print("データ取得失敗")
            return None
        
        # パターン分析
        patterns = self.analyze_m5m6_patterns(df)
        if not patterns:
            print("パターン分析失敗")
            return None
        
        # 期間別効果分析
        period_effects = self.analyze_period_effects(df)
        if not period_effects:
            print("期間別効果分析失敗")
            return None
        
        # レポート生成
        report = self.generate_analysis_report(patterns, period_effects)
        
        # 結果表示
        self.display_results(patterns, period_effects)
        
        return report
    
    def display_results(self, patterns, period_effects):
        """結果表示"""
        print("\n=== M5/M6パターン分析結果 ===")
        for pattern_name, stats in patterns.items():
            if stats:
                print(f"\n{pattern_name}:")
                print(f"  総レース数: {stats['total_races']}")
                print(f"  有効レース数: {stats['valid_races']}")
                print(f"  勝率: {stats['win_rate']}%")
                print(f"  連対率: {stats['place_rate']}%")
                print(f"  複勝率: {stats['show_rate']}%")
                print(f"  複勝率: {stats['fukusho_rate']}%")
                print(f"  平均ZI_Index: {stats['avg_zi_index']}")
                print(f"  平均ZM_Value: {stats['avg_zm_value']}")
        
        print("\n=== 期間別効果分析結果 ===")
        if period_effects and 'period_analysis' in period_effects:
            for period_name, stats in period_effects['period_analysis'].items():
                if stats:
                    print(f"\n{period_name}:")
                    print(f"  総レース数: {stats['total_races']}")
                    print(f"  有効レース数: {stats['valid_races']}")
                    print(f"  勝率: {stats['win_rate']}%")
                    print(f"  連対率: {stats['place_rate']}%")
                    print(f"  複勝率: {stats['show_rate']}%")
                    print(f"  複勝率: {stats['fukusho_rate']}%")
                    print(f"  平均ZI_Index: {stats['avg_zi_index']}")
                    print(f"  平均ZM_Value: {stats['avg_zm_value']}")

def main():
    analyzer = M5M6PatternAnalyzer()
    report = analyzer.run_analysis()
    
    if report:
        print("\n分析完了")
    else:
        print("\n分析失敗")

if __name__ == "__main__":
    main()
