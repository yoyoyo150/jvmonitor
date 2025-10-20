#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
馬カードシステム
2つのデータベースを活用した馬管理システム
"""
import sqlite3
import pandas as pd
import sys
from pathlib import Path

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

class HorseCardSystem:
    """馬カードシステムクラス"""
    
    def __init__(self):
        """初期化"""
        self.ecore_db_path = "ecore.db"
        self.excel_db_path = "trainer_prediction_system/excel_data.db"
        self.ecore_conn = None
        self.excel_conn = None
    
    def connect_databases(self):
        """データベース接続"""
        try:
            self.ecore_conn = sqlite3.connect(self.ecore_db_path)
            self.excel_conn = sqlite3.connect(self.excel_db_path)
            print("✅ データベース接続成功")
            return True
        except Exception as e:
            print(f"❌ データベース接続エラー: {e}")
            return False
    
    def disconnect_databases(self):
        """データベース切断"""
        if self.ecore_conn:
            self.ecore_conn.close()
        if self.excel_conn:
            self.excel_conn.close()
        print("✅ データベース切断完了")
    
    def get_horse_basic_info(self, ketto_num):
        """馬の基本情報取得（ecore.db）"""
        query = """
        SELECT 
            KettoNum,
            Bamei,
            BirthDate,
            SexCD,
            HinsyuCD,
            KeiroCD,
            TozaiCD,
            ChokyosiCode,
            ChokyosiRyakusyo,
            Syotai,
            BreederCode,
            BreederName,
            SanchiName,
            BanusiCode,
            BanusiName
        FROM N_UMA 
        WHERE KettoNum = ?
        """
        df = pd.read_sql_query(query, self.ecore_conn, params=[ketto_num])
        return df.iloc[0] if not df.empty else None
    
    def get_horse_pedigree(self, ketto_num):
        """血統情報取得（ecore.db）"""
        query = """
        SELECT 
            KettoNum,
            Ketto3InfoHansyokuNum1 as FatherKettoNum,
            Ketto3InfoHansyokuNum2 as MotherKettoNum,
            Ketto3InfoBamei1 as GrandfatherFather,
            Ketto3InfoBamei2 as GrandmotherFather,
            Ketto3InfoBamei3 as GrandfatherMother,
            Ketto3InfoBamei4 as GrandmotherMother
        FROM N_UMA 
        WHERE KettoNum = ?
        """
        df = pd.read_sql_query(query, self.ecore_conn, params=[ketto_num])
        return df.iloc[0] if not df.empty else None
    
    def get_horse_race_results(self, ketto_num, limit=10):
        """レース結果取得（ecore.db）"""
        query = """
        SELECT 
            KettoNum,
            Year || MonthDay as RaceDate,
            JyoCD,
            RaceNum,
            Umaban,
            Bamei,
            SexCD,
            HinsyuCD,
            KeiroCD,
            Barei,
            ChokyosiCode,
            ChokyosiRyakusyo,
            KisyuCode,
            KisyuRyakusyo,
            KakuteiJyuni,
            DochakuKubun,
            DochakuTosu,
            Time,
            Odds,
            Ninki,
            Honsyokin,
            Fukasyokin
        FROM N_UMA_RACE 
        WHERE KettoNum = ?
        ORDER BY RaceDate DESC
        LIMIT ?
        """
        df = pd.read_sql_query(query, self.ecore_conn, params=[ketto_num, limit])
        return df
    
    def get_horse_custom_variables(self, horse_name, limit=10):
        """独自変数取得（excel_data.db）"""
        query = """
        SELECT 
            SourceDate,
            HorseNameS,
            NormalizedHorseName,
            Ba_R_Raw,
            RaceName,
            Umaban,
            Mark1, Mark2, Mark3, Mark4, Mark5, Mark6, Mark7, Mark8,
            Prev_Mark1, Prev_Mark2, Prev_Mark3, Prev_Mark4, 
            Prev_Mark5, Prev_Mark6, Prev_Mark7, Prev_Mark8,
            ZI_Index, ZM_Value,
            Index_Rank1, Index_Rank2, Index_Rank3, Index_Rank4,
            Index_Diff1, Index_Diff2, Index_Diff4,
            Original_Val, Accel_Val,
            Prev_Kyakushitsu, Prev_Ninki,
            Prev_Chaku_Juni, Prev_Chaku_Sa,
            Prev_Tsuka1, Prev_Tsuka2, Prev_Tsuka3, Prev_Tsuka4,
            Prev_3F_Juni, Prev_Tosu,
            Prev_Race_Mark, Prev_Race_Mark2, Prev_Race_Mark3,
            Father_Type_Name, Damsire_Type_Name,
            Total_Horses, Work1, Work2,
            Prev_Track_Name, Same_Track_Flag,
            Prev_Kinryo, Prev_Bataiju, Prev_Bataiju_Zogen,
            Age_At_Race, Interval, Kyumei_Senme,
            Kinryo_Sa, Kyori_Sa, Prev_Shiba_Da, Prev_Kyori_M,
            Career_Total, Career_Latest, Class_C,
            Prev_Umaban, Prev_Shiba_Da_1, Current_Shiba_Da,
            Prev_Baba_Jotai, Prev_Class,
            T_Mark_Diff, Matchup_Mining_Val, Matchup_Mining_Rank,
            Kokyusen_Flag, B_Flag, Syozoku,
            Check_Trainer_Type, Check_Jockey_Type, Syozoku_1,
            Trainer_Name, Fukusho_Odds_Lower, Fukusho_Odds_Upper,
            Tan_Odds, Wakuban, Course_Group_Count, Course_Group_Name1,
            Ninki_Rank, Norikae_Flag, Prev_Race_ID_New,
            SourceFile, ImportedAt
        FROM excel_marks 
        WHERE HorseNameS = ?
        ORDER BY SourceDate DESC
        LIMIT ?
        """
        df = pd.read_sql_query(query, self.excel_conn, params=[horse_name, limit])
        return df
    
    def generate_horse_card(self, ketto_num):
        """馬カード生成"""
        print(f"=== 馬カード生成: {ketto_num} ===")
        
        # 1. 基本情報取得
        basic_info = self.get_horse_basic_info(ketto_num)
        if basic_info is None:
            print(f"❌ 血統番号 {ketto_num} の馬が見つかりません")
            return None
        
        print(f"馬名: {basic_info['Bamei']}")
        print(f"生年月日: {basic_info['BirthDate']}")
        print(f"性別: {basic_info['SexCD']}")
        print(f"品種: {basic_info['HinsyuCD']}")
        print(f"毛色: {basic_info['KeiroCD']}")
        print(f"東西: {basic_info['TozaiCD']}")
        print(f"調教師: {basic_info['ChokyosiRyakusyo']}")
        print(f"所属: {basic_info['Syotai']}")
        print(f"生産者: {basic_info['BreederName']}")
        print(f"産地: {basic_info['SanchiName']}")
        print(f"馬主: {basic_info['BanusiName']}")
        
        # 2. 血統情報取得
        pedigree = self.get_horse_pedigree(ketto_num)
        if pedigree is not None:
            print(f"\n--- 血統情報 ---")
            print(f"父: {pedigree['FatherKettoNum']} - {pedigree['GrandfatherFather']}")
            print(f"母: {pedigree['MotherKettoNum']} - {pedigree['GrandfatherMother']}")
            print(f"祖父（父方）: {pedigree['GrandfatherFather']}")
            print(f"祖母（父方）: {pedigree['GrandmotherFather']}")
            print(f"祖父（母方）: {pedigree['GrandfatherMother']}")
            print(f"祖母（母方）: {pedigree['GrandmotherMother']}")
        
        # 3. レース結果取得
        race_results = self.get_horse_race_results(ketto_num, 5)
        if not race_results.empty:
            print(f"\n--- 最近のレース結果（最新5件） ---")
            for _, race in race_results.iterrows():
                print(f"{race['RaceDate']} {race['JyoCD']}{race['RaceNum']}R "
                      f"着順:{race['KakuteiJyuni']} 騎手:{race['KisyuRyakusyo']} "
                      f"オッズ:{race['Odds']} 人気:{race['Ninki']}")
        
        # 4. 独自変数取得
        custom_vars = self.get_horse_custom_variables(basic_info['Bamei'], 3)
        if not custom_vars.empty:
            print(f"\n--- 独自変数（最新3件） ---")
            for _, custom in custom_vars.iterrows():
                print(f"{custom['SourceDate']} {custom['JyoCD']}{custom['RaceNum']}R "
                      f"Mark5:{custom['Mark5']} Mark6:{custom['Mark6']} "
                      f"ZI_Index:{custom['ZI_Index']} ZM_Value:{custom['ZM_Value']}")
        
        return {
            'basic_info': basic_info,
            'pedigree': pedigree,
            'race_results': race_results,
            'custom_variables': custom_vars
        }
    
    def search_horse_by_name(self, horse_name):
        """馬名で検索"""
        query = """
        SELECT DISTINCT KettoNum, Bamei
        FROM N_UMA 
        WHERE Bamei LIKE ?
        ORDER BY Bamei
        LIMIT 10
        """
        df = pd.read_sql_query(query, self.ecore_conn, params=[f'%{horse_name}%'])
        return df
    
    def search_horse_by_trainer(self, trainer_name):
        """調教師で検索"""
        query = """
        SELECT DISTINCT KettoNum, Bamei, ChokyosiRyakusyo
        FROM N_UMA 
        WHERE ChokyosiRyakusyo LIKE ?
        ORDER BY Bamei
        LIMIT 10
        """
        df = pd.read_sql_query(query, self.ecore_conn, params=[f'%{trainer_name}%'])
        return df

def main():
    """メイン関数"""
    print("=== 馬カードシステム開始 ===")
    
    horse_system = HorseCardSystem()
    
    if not horse_system.connect_databases():
        return
    
    try:
        # サンプル馬の検索
        print("\n--- サンプル馬の検索 ---")
        sample_horses = horse_system.search_horse_by_name("スマート")
        if not sample_horses.empty:
            print("検索結果:")
            print(sample_horses.to_string(index=False))
            
            # 最初の馬の馬カード生成
            first_horse = sample_horses.iloc[0]
            horse_card = horse_system.generate_horse_card(first_horse['KettoNum'])
            
            if horse_card:
                print("\n✅ 馬カード生成完了")
        else:
            print("❌ 検索結果が見つかりませんでした")
    
    finally:
        horse_system.disconnect_databases()

if __name__ == "__main__":
    main()
