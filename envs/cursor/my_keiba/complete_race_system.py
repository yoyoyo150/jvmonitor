# -*- coding: utf-8 -*-
import sqlite3
import sys
import io
import os
from datetime import datetime

# UTF-8エンコーディング設定
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class CompleteRaceSystem:
    def __init__(self, db_path='ecore.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        
    def get_venue_name(self, jyo_cd):
        """開催場名を取得"""
        venues = {
            '01': '札幌', '02': '函館', '03': '福島', '04': '新潟', '05': '東京',
            '06': '中山', '07': '中京', '08': '京都', '09': '阪神', '10': '小倉',
            '50': '地方競馬'
        }
        return venues.get(jyo_cd, f'場{jyo_cd}')
    
    def get_recent_races(self, year=None, limit=50):
        """最近のレースを取得"""
        query = """
        SELECT 
            Year,
            MonthDay,
            JyoCD,
            RaceNum,
            Hondai,
            Kyori,
            HassoTime,
            TorokuTosu,
            SyussoTosu
        FROM N_RACE
        WHERE 1=1
        """
        params = []
        
        if year:
            query += " AND Year = ?"
            params.append(year)
        else:
            query += " AND Year >= '2024'"
        
        query += " ORDER BY Year DESC, MonthDay DESC, JyoCD, RaceNum"
        query += f" LIMIT {limit}"
        
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()
    
    def get_historical_races(self, year, limit=100):
        """過去のレースを取得"""
        query = """
        SELECT 
            Year,
            MonthDay,
            JyoCD,
            RaceNum,
            Hondai,
            Kyori,
            HassoTime,
            TorokuTosu,
            SyussoTosu
        FROM N_RACE
        WHERE Year = ?
        ORDER BY MonthDay DESC, JyoCD, RaceNum
        LIMIT ?
        """
        
        cursor = self.conn.cursor()
        cursor.execute(query, (year, limit))
        return cursor.fetchall()
    
    def get_race_horses(self, year, monthday, jyo_cd, race_num):
        """特定レースの出馬表を取得"""
        query = """
        SELECT 
            Wakuban,
            Umaban,
            Bamei,
            KisyuRyakusyo,
            ChokyosiRyakusyo,
            BaTaijyu,
            Odds,
            Ninki,
            Honsyokin,
            Fukasyokin,
            NyusenJyuni,
            KakuteiJyuni,
            Time
        FROM N_UMA_RACE
        WHERE Year = ? AND MonthDay = ? AND JyoCD = ? AND RaceNum = ?
        ORDER BY Umaban
        """
        
        cursor = self.conn.cursor()
        cursor.execute(query, (year, monthday, jyo_cd, race_num))
        return cursor.fetchall()
    
    def display_recent_races(self):
        """2024年以降のレースを並べる形式で表示"""
        print("=== 2024年以降のレース一覧（並べる形式） ===")
        
        for year in ['2025', '2024']:
            races = self.get_recent_races(year=year, limit=200)
            if not races:
                continue
                
            print(f"\n【{year}年】")
            print("=" * 60)
            
            # 月別にグループ化
            monthly_races = {}
            for race in races:
                year, monthday, jyo_cd, race_num, hondai, kyori, hasso_time, toroku, syusso = race
                month = monthday[:2]
                if month not in monthly_races:
                    monthly_races[month] = []
                monthly_races[month].append(race)
            
            # 月別に表示
            for month in sorted(monthly_races.keys(), reverse=True):
                month_races = monthly_races[month]
                print(f"\n{year}年{month}月 ({len(month_races)}レース)")
                print("-" * 40)
                
                for race in month_races[:15]:  # 月あたり最大15レース表示
                    year, monthday, jyo_cd, race_num, hondai, kyori, hasso_time, toroku, syusso = race
                    venue_name = self.get_venue_name(jyo_cd)
                    date_str = f"{monthday[:2]}月{monthday[2:]}日"
                    print(f"  {date_str} {venue_name} {race_num}R: {hondai} ({kyori}m, {hasso_time})")
                    print(f"    登録:{toroku}頭 出走:{syusso}頭")
                
                if len(month_races) > 15:
                    print(f"    ... 他{len(month_races) - 15}レース")
    
    def display_historical_races(self):
        """2023年以前のレースをアコーデオン式で表示"""
        print("=== 2023年以前のレース一覧（アコーデオン式） ===")
        
        for year in ['2023', '2022', '2021', '2020', '2019', '2018', '2017']:
            races = self.get_historical_races(year, limit=50)
            if not races:
                continue
                
            print(f"\n【{year}年】 ({len(races)}レース)")
            print("=" * 50)
            
            # 月別にグループ化
            monthly_races = {}
            for race in races:
                year, monthday, jyo_cd, race_num, hondai, kyori, hasso_time, toroku, syusso = race
                month = monthday[:2]
                if month not in monthly_races:
                    monthly_races[month] = []
                monthly_races[month].append(race)
            
            # 月別にアコーデオン式で表示
            for month in sorted(monthly_races.keys(), reverse=True):
                month_races = monthly_races[month]
                month_name = f"{year}年{month}月"
                print(f"\n▼ {month_name} ({len(month_races)}レース)")
                
                # 最初の3レースのみ表示
                for i, race in enumerate(month_races[:3]):
                    year, monthday, jyo_cd, race_num, hondai, kyori, hasso_time, toroku, syusso = race
                    venue_name = self.get_venue_name(jyo_cd)
                    date_str = f"{monthday[:2]}月{monthday[2:]}日"
                    print(f"  {date_str} {venue_name} {race_num}R: {hondai} ({kyori}m, {hasso_time})")
                    print(f"    登録:{toroku}頭 出走:{syusso}頭")
                
                if len(month_races) > 3:
                    print(f"  ... 他{len(month_races) - 3}レース")
                    print(f"  [Enter] キーで{month_name}の全レースを表示")
                    
                    # ユーザー入力待ち
                    try:
                        input()
                        print(f"\n{month_name}の全レース:")
                        print("-" * 30)
                        
                        for race in month_races:
                            year, monthday, jyo_cd, race_num, hondai, kyori, hasso_time, toroku, syusso = race
                            venue_name = self.get_venue_name(jyo_cd)
                            date_str = f"{monthday[:2]}月{monthday[2:]}日"
                            print(f"  {date_str} {venue_name} {race_num}R: {hondai} ({kyori}m, {hasso_time})")
                            print(f"    登録:{toroku}頭 出走:{syusso}頭")
                    except EOFError:
                        print("入力が中断されました。")
                        break
    
    def display_race_detail(self, year, monthday, jyo_cd, race_num):
        """特定レースの詳細を表示"""
        cursor = self.conn.cursor()
        
        # レース基本情報
        race_query = """
        SELECT Hondai, Fukudai, Kyori, HassoTime, TorokuTosu, SyussoTosu, TenkoCD, SibaBabaCD
        FROM N_RACE
        WHERE Year = ? AND MonthDay = ? AND JyoCD = ? AND RaceNum = ?
        """
        
        cursor.execute(race_query, (year, monthday, jyo_cd, race_num))
        race_info = cursor.fetchone()
        
        if not race_info:
            print("レース情報が見つかりません。")
            return
        
        hondai, fukudai, kyori, hasso_time, toroku, syusso, tenko, siba_baba = race_info
        venue_name = self.get_venue_name(jyo_cd)
        date_str = f"{year}年{monthday[:2]}月{monthday[2:]}日"
        
        print(f"=== レース詳細 ===")
        print(f"開催日: {date_str}")
        print(f"開催場: {venue_name}")
        print(f"レース: {race_num}R")
        print(f"レース名: {hondai}")
        if fukudai:
            print(f"副題: {fukudai}")
        print(f"距離: {kyori}m")
        print(f"発走時刻: {hasso_time}")
        print(f"登録頭数: {toroku}頭")
        print(f"出走頭数: {syusso}頭")
        print(f"天候: {tenko}")
        print(f"芝馬場: {siba_baba}")
        
        # 出馬表
        horses = self.get_race_horses(year, monthday, jyo_cd, race_num)
        
        print(f"\n=== 出馬表 ===")
        for horse in horses:
            waku, uma, bamei, kisyu, chokyosi, taijyu, odds, ninki, honsyokin, fukasyokin, nyusen, kakutei, time = horse
            print(f"{waku}-{uma}: {bamei}")
            print(f"  騎手: {kisyu} / 調教師: {chokyosi}")
            print(f"  馬体重: {taijyu}kg")
            print(f"  オッズ: {odds} / 人気: {ninki}")
            print(f"  本賞金: {honsyokin}円 / 副賞金: {fukasyokin}円")
            if nyusen:
                print(f"  入線順: {nyusen}位")
            if kakutei:
                print(f"  確定順: {kakutei}位")
            if time:
                print(f"  タイム: {time}")
            print()
    
    def show_system_status(self):
        """システムの状況を表示"""
        cursor = self.conn.cursor()
        
        print("=== システム状況 ===")
        
        # データベース統計
        cursor.execute("SELECT COUNT(*) FROM N_RACE")
        race_count = cursor.fetchone()[0]
        print(f"総レース数: {race_count:,} 件")
        
        cursor.execute("SELECT COUNT(*) FROM N_UMA_RACE")
        uma_count = cursor.fetchone()[0]
        print(f"総出馬数: {uma_count:,} 件")
        
        # 最新データ
        cursor.execute("SELECT MAX(Year || MonthDay) FROM N_RACE")
        latest_race = cursor.fetchone()[0]
        print(f"最新レース日: {latest_race}")
        
        # 年別統計
        cursor.execute("""
            SELECT Year, COUNT(*) as count 
            FROM N_RACE 
            WHERE Year >= '2020'
            GROUP BY Year 
            ORDER BY Year DESC
        """)
        yearly_stats = cursor.fetchall()
        
        print("\n年別レース数:")
        for year, count in yearly_stats:
            print(f"  {year}年: {count:,} レース")
        
        # JVMonitorエラー修正状況
        cursor.execute("SELECT COUNT(*) FROM NL_SE_RACE_UMA")
        nl_count = cursor.fetchone()[0]
        print(f"\nJVMonitor修正状況:")
        print(f"  NL_SE_RACE_UMA: {nl_count:,} 件")
        
        if nl_count > 0:
            print("  [OK] JVMonitorエラーは修正済み")
        else:
            print("  [WARNING] JVMonitorエラーが残っています")
    
    def main_menu(self):
        """メインメニュー"""
        while True:
            print("\n" + "="*60)
            print("🏇 競馬出馬表表示システム v2.0")
            print("="*60)
            print("1. 2024年以降のレース（並べる形式）")
            print("2. 2023年以前のレース（アコーデオン式）")
            print("3. 特定レースの詳細表示")
            print("4. システム状況確認")
            print("5. 終了")
            print("="*60)
            
            try:
                choice = input("選択 (1-5): ").strip()
                
                if choice == '1':
                    self.display_recent_races()
                
                elif choice == '2':
                    self.display_historical_races()
                
                elif choice == '3':
                    print("\nレース詳細を表示するレースを選択してください:")
                    year = input("年を入力 (例: 2024): ").strip()
                    
                    if not year:
                        print("年が入力されていません。")
                        continue
                    
                    races = self.get_historical_races(year, limit=20)
                    if not races:
                        print("該当するレースが見つかりません。")
                        continue
                    
                    print(f"\n{year}年のレース一覧:")
                    for i, race in enumerate(races[:10], 1):
                        year, monthday, jyo_cd, race_num, hondai, kyori, hasso_time, toroku, syusso = race
                        venue_name = self.get_venue_name(jyo_cd)
                        date_str = f"{year}年{monthday[:2]}月{monthday[2:]}日"
                        print(f"{i}. {date_str} {venue_name} {race_num}R: {hondai}")
                    
                    try:
                        race_choice = int(input("レース番号を入力: ")) - 1
                        if 0 <= race_choice < len(races):
                            selected_race = races[race_choice]
                            year, monthday, jyo_cd, race_num = selected_race[0], selected_race[1], selected_race[2], selected_race[3]
                            self.display_race_detail(year, monthday, jyo_cd, race_num)
                        else:
                            print("無効な選択です。")
                    except ValueError:
                        print("数値を入力してください。")
                
                elif choice == '4':
                    self.show_system_status()
                
                elif choice == '5':
                    print("システムを終了します。")
                    break
                
                else:
                    print("無効な選択です。1-5の数字を入力してください。")
                    
            except KeyboardInterrupt:
                print("\n\nシステムを終了します。")
                break
            except Exception as e:
                print(f"エラーが発生しました: {e}")
    
    def close(self):
        """データベース接続を閉じる"""
        self.conn.close()

def main():
    """メイン実行"""
    print("競馬出馬表表示システムを起動中...")
    
    # データベースファイルの確認
    if not os.path.exists('ecore.db'):
        print("エラー: ecore.db が見つかりません。")
        print("データベースファイルが正しい場所にあることを確認してください。")
        return
    
    try:
        system = CompleteRaceSystem()
        system.main_menu()
        system.close()
    except Exception as e:
        print(f"システムエラー: {e}")
        print("データベース接続に問題がある可能性があります。")

if __name__ == "__main__":
    main()


