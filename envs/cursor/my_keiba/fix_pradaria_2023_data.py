# -*- coding: utf-8 -*-
import sqlite3
import sys
import io

# UTF-8エンコーディング設定
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def check_pradaria_2023_actual_data():
    """プラダリアの2023年データを詳細確認"""
    conn = sqlite3.connect('ecore.db')
    cursor = conn.cursor()
    
    print("=== プラダリアの2023年データ詳細確認 ===\n")
    
    # 1. プラダリアの2023年全出走確認
    print("1. プラダリアの2023年全出走確認")
    cursor.execute("""
        SELECT 
            Year,
            MonthDay,
            JyoCD,
            RaceNum,
            NyusenJyuni,
            KakuteiJyuni,
            KisyuRyakusyo,
            Honsyokin,
            Time,
            Odds,
            Ninki
        FROM N_UMA_RACE
        WHERE Bamei = 'プラダリア' AND Year = '2023'
        ORDER BY MonthDay DESC
    """)
    pradaria_2023 = cursor.fetchall()
    
    print(f"プラダリアの2023年出馬数: {len(pradaria_2023)} 件")
    
    if pradaria_2023:
        print("\nプラダリアの2023年成績:")
        for race in pradaria_2023:
            year, monthday, jyo_cd, race_num, nyusen, kakutei, kisyu, honsyokin, time, odds, ninki = race
            date_str = f"{monthday[:2]}月{monthday[2:]}日"
            print(f"  {date_str} 場{jyo_cd} {race_num}R ({kakutei or nyusen}位)")
            print(f"    騎手: {kisyu}, 賞金: {honsyokin}円, タイム: {time}")
            print(f"    オッズ: {odds}, 人気: {ninki}")
    else:
        print("プラダリアの2023年データが見つかりません")
        print("データベースに問題があります")
    
    # 2. 2023年10月9日の京都大賞典データ確認
    print("\n2. 2023年10月9日の京都大賞典データ確認")
    cursor.execute("""
        SELECT 
            Year,
            MonthDay,
            JyoCD,
            RaceNum,
            Bamei,
            NyusenJyuni,
            KakuteiJyuni,
            KisyuRyakusyo,
            Honsyokin,
            Time
        FROM N_UMA_RACE
        WHERE Year = '2023' AND MonthDay = '1009' AND JyoCD = '08'
        ORDER BY Umaban
    """)
    kyoto_daisho = cursor.fetchall()
    
    print(f"2023年10月9日 京都大賞典の出馬数: {len(kyoto_daisho)} 件")
    
    if kyoto_daisho:
        print("京都大賞典の出馬表:")
        for race in kyoto_daisho:
            year, monthday, jyo_cd, race_num, bamei, nyusen, kakutei, kisyu, honsyokin, time = race
            print(f"  {bamei} ({kakutei or nyusen}位) - {kisyu} - {time}")
    else:
        print("2023年10月9日 京都大賞典のデータが見つかりません")
    
    # 3. データベースの整合性確認
    print("\n3. データベースの整合性確認")
    cursor.execute("""
        SELECT 
            Year,
            COUNT(*) as race_count
        FROM N_RACE
        WHERE Year = '2023'
        GROUP BY Year
    """)
    race_2023 = cursor.fetchone()
    
    cursor.execute("""
        SELECT 
            Year,
            COUNT(*) as uma_count
        FROM N_UMA_RACE
        WHERE Year = '2023'
        GROUP BY Year
    """)
    uma_2023 = cursor.fetchone()
    
    print(f"2023年のレース数: {race_2023[1] if race_2023 else 0:,} 件")
    print(f"2023年の出馬数: {uma_2023[1] if uma_2023 else 0:,} 件")
    
    # 4. プラダリアの全成績確認
    print("\n4. プラダリアの全成績確認")
    cursor.execute("""
        SELECT 
            Year,
            COUNT(*) as race_count
        FROM N_UMA_RACE
        WHERE Bamei = 'プラダリア'
        GROUP BY Year
        ORDER BY Year DESC
    """)
    pradaria_all = cursor.fetchall()
    
    print("プラダリアの年別出馬数:")
    for year, race_count in pradaria_all:
        print(f"  {year}年: {race_count} 出馬")
    
    conn.close()

def fix_database_issues():
    """データベースの問題を修正"""
    print("\n=== データベース問題の修正 ===\n")
    
    conn = sqlite3.connect('ecore.db')
    cursor = conn.cursor()
    
    try:
        # 1. インデックスの再構築
        print("1. インデックスの再構築")
        cursor.execute("REINDEX")
        print("[OK] インデックスを再構築しました")
        
        # 2. データベースの最適化
        print("\n2. データベースの最適化")
        cursor.execute("VACUUM")
        print("[OK] データベースを最適化しました")
        
        # 3. 統計情報の更新
        print("\n3. 統計情報の更新")
        cursor.execute("ANALYZE")
        print("[OK] 統計情報を更新しました")
        
        # 4. プラダリアの2023年データを再確認
        print("\n4. プラダリアの2023年データを再確認")
        cursor.execute("""
            SELECT COUNT(*) FROM N_UMA_RACE
            WHERE Bamei = 'プラダリア' AND Year = '2023'
        """)
        pradaria_2023_count = cursor.fetchone()[0]
        print(f"修正後のプラダリア2023年出馬数: {pradaria_2023_count} 件")
        
        if pradaria_2023_count > 0:
            print("[OK] プラダリアの2023年データが確認できました")
        else:
            print("[WARNING] プラダリアの2023年データがまだ見つかりません")
            print("EveryDB2.3でデータを再ダウンロードする必要があります")
        
        conn.commit()
        
    except Exception as e:
        print(f"[ERROR] データベース修正エラー: {e}")
        conn.rollback()
    finally:
        conn.close()

def create_data_recovery_script():
    """データ復旧用スクリプトの作成"""
    print("\n=== データ復旧用スクリプトの作成 ===\n")
    
    script_content = '''@echo off
echo プラダリア2023年データ復旧スクリプト
echo =====================================

echo.
echo 1. データベースの整合性を確認中...
python check_pradaria_2023_data.py

echo.
echo 2. EveryDB2.3でデータを再ダウンロードしてください:
echo    - 蓄積系 > 時系列
echo    - 開始日: 2023/01/01
echo    - 終了日: 2023/12/31
echo    - データ種別: N_RACE, N_UMA_RACE, N_UMA

echo.
echo 3. 完了後、このスクリプトを再実行してください。
pause
'''
    
    with open('recover_pradaria_2023.bat', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("[OK] recover_pradaria_2023.bat を作成しました")

if __name__ == "__main__":
    check_pradaria_2023_actual_data()
    fix_database_issues()
    create_data_recovery_script()


