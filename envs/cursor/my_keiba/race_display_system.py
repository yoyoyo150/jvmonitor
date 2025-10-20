# -*- coding: utf-8 -*-
import sqlite3
import pandas as pd
from datetime import datetime
import streamlit as st
import sys
import io

# UTF-8エンコーディング設定
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class RaceDisplaySystem:
    def __init__(self, db_path='ecore.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
    
    def get_race_list(self, year=None, month=None, jyo_cd=None, limit=50):
        """レース一覧を取得"""
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
            SyussoTosu,
            TenkoCD,
            SibaBabaCD,
            DirtBabaCD
        FROM N_RACE
        WHERE 1=1
        """
        params = []
        
        if year:
            query += " AND Year = ?"
            params.append(year)
        
        if month:
            query += " AND SUBSTR(MonthDay, 1, 2) = ?"
            params.append(month.zfill(2))
        
        if jyo_cd:
            query += " AND JyoCD = ?"
            params.append(jyo_cd)
        
        query += " ORDER BY Year DESC, MonthDay DESC, JyoCD, RaceNum"
        query += f" LIMIT {limit}"
        
        return pd.read_sql_query(query, self.conn, params=params)
    
    def get_race_details(self, year, monthday, jyo_cd, race_num):
        """特定レースの詳細情報を取得"""
        query = """
        SELECT 
            r.Year,
            r.MonthDay,
            r.JyoCD,
            r.RaceNum,
            r.Hondai,
            r.Fukudai,
            r.Kyori,
            r.HassoTime,
            r.TorokuTosu,
            r.SyussoTosu,
            r.TenkoCD,
            r.SibaBabaCD,
            r.DirtBabaCD,
            r.Honsyokin1,
            r.Honsyokin2,
            r.Honsyokin3,
            r.Honsyokin4,
            r.Honsyokin5
        FROM N_RACE r
        WHERE r.Year = ? AND r.MonthDay = ? AND r.JyoCD = ? AND r.RaceNum = ?
        """
        
        race_info = pd.read_sql_query(query, self.conn, params=[year, monthday, jyo_cd, race_num])
        return race_info.iloc[0] if not race_info.empty else None
    
    def get_horse_list(self, year, monthday, jyo_cd, race_num):
        """特定レースの出馬表を取得"""
        query = """
        SELECT 
            u.Wakuban,
            u.Umaban,
            u.KettoNum,
            u.Bamei,
            u.SexCD,
            u.HinsyuCD,
            u.KeiroCD,
            u.Barei,
            u.ChokyosiRyakusyo,
            u.BanusiName,
            u.Futan,
            u.KisyuRyakusyo,
            u.BaTaijyu,
            u.ZogenFugo,
            u.ZogenSa,
            u.Odds,
            u.Ninki,
            u.Honsyokin,
            u.Fukasyokin,
            u.NyusenJyuni,
            u.KakuteiJyuni,
            u.Time,
            u.ChakusaCD
        FROM N_UMA_RACE u
        WHERE u.Year = ? AND u.MonthDay = ? AND u.JyoCD = ? AND u.RaceNum = ?
        ORDER BY u.Umaban
        """
        
        return pd.read_sql_query(query, self.conn, params=[year, monthday, jyo_cd, race_num])
    
    def get_jockey_info(self, kisyu_code):
        """騎手情報を取得"""
        query = """
        SELECT 
            KisyuCode,
            KisyuRyakusyo,
            KisyuName
        FROM N_KISYU
        WHERE KisyuCode = ?
        """
        
        return pd.read_sql_query(query, self.conn, params=[kisyu_code])
    
    def get_trainer_info(self, chokyosi_code):
        """調教師情報を取得"""
        query = """
        SELECT 
            ChokyosiCode,
            ChokyosiRyakusyo,
            ChokyosiName
        FROM N_CHOKYO
        WHERE ChokyosiCode = ?
        """
        
        return pd.read_sql_query(query, self.conn, params=[chokyosi_code])
    
    def get_venue_name(self, jyo_cd):
        """開催場名を取得"""
        venue_names = {
            '01': '札幌', '02': '函館', '03': '福島', '04': '新潟', '05': '東京',
            '06': '中山', '07': '中京', '08': '京都', '09': '阪神', '10': '小倉',
            '50': '地方競馬'
        }
        return venue_names.get(jyo_cd, f'場{jyo_cd}')
    
    def format_race_display(self, race_info, horse_list):
        """レース情報を表示用にフォーマット"""
        if race_info is None:
            return "レース情報が見つかりません。"
        
        # レース基本情報
        venue_name = self.get_venue_name(race_info['JyoCD'])
        race_date = f"{race_info['Year']}年{race_info['MonthDay'][:2]}月{race_info['MonthDay'][2:]}日"
        
        display = f"""
=== レース情報 ===
開催日: {race_date}
開催場: {venue_name}
レース番号: {race_info['RaceNum']}R
レース名: {race_info['Hondai']}
副題: {race_info['Fukudai']}
距離: {race_info['Kyori']}m
発走時刻: {race_info['HassoTime']}
登録頭数: {race_info['TorokuTosu']}頭
出走頭数: {race_info['SyussoTosu']}頭
天候: {race_info['TenkoCD']}
芝馬場: {race_info['SibaBabaCD']}
ダート馬場: {race_info['DirtBabaCD']}

=== 出馬表 ===
"""
        
        # 出馬表
        for _, horse in horse_list.iterrows():
            display += f"""
{horse['Wakuban']}-{horse['Umaban']}: {horse['Bamei']}
  騎手: {horse['KisyuRyakusyo']} / 調教師: {horse['ChokyosiRyakusyo']}
  馬主: {horse['BanusiName']}
  負担重量: {horse['Futan']}kg
  馬体重: {horse['BaTaijyu']}kg ({horse['ZogenFugo']}{horse['ZogenSa']}kg)
  オッズ: {horse['Odds']} / 人気: {horse['Ninki']}
  本賞金: {horse['Honsyokin']}円 / 副賞金: {horse['Fukasyokin']}円
"""
        
        return display
    
    def search_races(self, keyword=None, year=None, venue=None):
        """レース検索"""
        query = """
        SELECT DISTINCT
            Year,
            MonthDay,
            JyoCD,
            RaceNum,
            Hondai,
            Kyori,
            HassoTime
        FROM N_RACE
        WHERE 1=1
        """
        params = []
        
        if keyword:
            query += " AND (Hondai LIKE ? OR Fukudai LIKE ?)"
            params.extend([f'%{keyword}%', f'%{keyword}%'])
        
        if year:
            query += " AND Year = ?"
            params.append(year)
        
        if venue:
            query += " AND JyoCD = ?"
            params.append(venue)
        
        query += " ORDER BY Year DESC, MonthDay DESC, JyoCD, RaceNum"
        query += " LIMIT 100"
        
        return pd.read_sql_query(query, self.conn, params=params)
    
    def get_recent_races(self, days=7):
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
            COUNT(u.Umaban) as horse_count
        FROM N_RACE r
        LEFT JOIN N_UMA_RACE u ON r.Year = u.Year 
            AND r.MonthDay = u.MonthDay 
            AND r.JyoCD = u.JyoCD 
            AND r.RaceNum = u.RaceNum
        WHERE r.Year >= '2024'
        GROUP BY r.Year, r.MonthDay, r.JyoCD, r.RaceNum
        ORDER BY r.Year DESC, r.MonthDay DESC
        LIMIT 50
        """
        
        return pd.read_sql_query(query, self.conn)
    
    def close(self):
        """データベース接続を閉じる"""
        self.conn.close()

def main():
    """メイン実行関数"""
    st.set_page_config(page_title="競馬出馬表システム", layout="wide")
    
    st.title("🏇 競馬出馬表システム")
    
    # データベース接続
    race_system = RaceDisplaySystem()
    
    # サイドバー
    st.sidebar.title("検索条件")
    
    # 検索条件
    search_keyword = st.sidebar.text_input("レース名検索")
    search_year = st.sidebar.selectbox("年", [None, "2025", "2024", "2023", "2022", "2021"])
    search_venue = st.sidebar.selectbox("開催場", [None, "01", "02", "03", "04", "05", "06", "07", "08", "09", "10"])
    
    # 検索実行
    if st.sidebar.button("検索"):
        results = race_system.search_races(
            keyword=search_keyword,
            year=search_year,
            venue=search_venue
        )
        
        if not results.empty:
            st.subheader("検索結果")
            for _, race in results.iterrows():
                venue_name = race_system.get_venue_name(race['JyoCD'])
                st.write(f"**{race['Year']}年{race['MonthDay'][:2]}月{race['MonthDay'][2:]}日** {venue_name} {race['RaceNum']}R: {race['Hondai']} ({race['Kyori']}m, {race['HassoTime']})")
        else:
            st.warning("該当するレースが見つかりませんでした。")
    
    # 最近のレース
    st.subheader("最近のレース")
    recent_races = race_system.get_recent_races()
    
    if not recent_races.empty:
        for _, race in recent_races.head(10).iterrows():
            venue_name = race_system.get_venue_name(race['JyoCD'])
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**{race['Year']}年{race['MonthDay'][:2]}月{race['MonthDay'][2:]}日** {venue_name} {race['RaceNum']}R: {race['Hondai']}")
            
            with col2:
                st.write(f"{race['Kyori']}m")
            
            with col3:
                if st.button(f"詳細", key=f"detail_{race['Year']}_{race['MonthDay']}_{race['JyoCD']}_{race['RaceNum']}"):
                    # レース詳細を表示
                    race_info = race_system.get_race_details(
                        race['Year'], race['MonthDay'], race['JyoCD'], race['RaceNum']
                    )
                    horse_list = race_system.get_horse_list(
                        race['Year'], race['MonthDay'], race['JyoCD'], race['RaceNum']
                    )
                    
                    if race_info is not None:
                        st.subheader("レース詳細")
                        st.text(race_system.format_race_display(race_info, horse_list))
    
    race_system.close()

if __name__ == "__main__":
    main()
