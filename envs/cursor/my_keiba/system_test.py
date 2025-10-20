# -*- coding: utf-8 -*-
import sqlite3
import sys
import io
import os
from datetime import datetime

# UTF-8エンコーディング設定
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def test_database_connection():
    """データベース接続テスト"""
    print("=== データベース接続テスト ===")
    
    try:
        conn = sqlite3.connect('ecore.db')
        cursor = conn.cursor()
        
        # 基本テーブルの確認
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"[OK] データベース接続成功")
        print(f"[OK] テーブル数: {len(tables)}")
        
        # 主要テーブルのデータ確認
        cursor.execute("SELECT COUNT(*) FROM N_RACE")
        race_count = cursor.fetchone()[0]
        print(f"[OK] N_RACE: {race_count:,} 件")
        
        cursor.execute("SELECT COUNT(*) FROM N_UMA_RACE")
        uma_count = cursor.fetchone()[0]
        print(f"[OK] N_UMA_RACE: {uma_count:,} 件")
        
        # JVMonitor修正テーブルの確認
        cursor.execute("SELECT COUNT(*) FROM NL_SE_RACE_UMA")
        nl_count = cursor.fetchone()[0]
        print(f"[OK] NL_SE_RACE_UMA: {nl_count:,} 件")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] データベース接続エラー: {e}")
        return False

def test_data_retrieval():
    """データ取得テスト"""
    print("\n=== データ取得テスト ===")
    
    try:
        conn = sqlite3.connect('ecore.db')
        cursor = conn.cursor()
        
        # 最新レースの取得
        cursor.execute("""
            SELECT Year, MonthDay, JyoCD, RaceNum, Hondai, Kyori, HassoTime
            FROM N_RACE 
            WHERE Year >= '2024'
            ORDER BY Year DESC, MonthDay DESC
            LIMIT 5
        """)
        recent_races = cursor.fetchall()
        
        print(f"[OK] 最新レース取得: {len(recent_races)} 件")
        for race in recent_races:
            year, monthday, jyo_cd, race_num, hondai, kyori, hasso_time = race
            print(f"  {year}年{monthday[:2]}月{monthday[2:]}日 場{jyo_cd} {race_num}R: {hondai}")
        
        # 過去レースの取得
        cursor.execute("""
            SELECT Year, COUNT(*) as count
            FROM N_RACE 
            WHERE Year >= '2017'
            GROUP BY Year 
            ORDER BY Year DESC
        """)
        yearly_races = cursor.fetchall()
        
        print(f"[OK] 年別レース数取得: {len(yearly_races)} 年")
        for year, count in yearly_races:
            print(f"  {year}年: {count:,} レース")
        
        # 出馬データの取得
        cursor.execute("""
            SELECT COUNT(*) FROM N_UMA_RACE 
            WHERE Year >= '2024'
        """)
        recent_umas = cursor.fetchone()[0]
        print(f"[OK] 2024年以降の出馬数: {recent_umas:,} 件")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] データ取得エラー: {e}")
        return False

def test_utf8_encoding():
    """UTF-8エンコーディングテスト"""
    print("\n=== UTF-8エンコーディングテスト ===")
    
    try:
        conn = sqlite3.connect('ecore.db')
        cursor = conn.cursor()
        
        # 日本語データの取得テスト
        cursor.execute("""
            SELECT Bamei, KisyuRyakusyo, ChokyosiRyakusyo
            FROM N_UMA_RACE 
            WHERE Bamei != '' AND Bamei IS NOT NULL
            LIMIT 5
        """)
        japanese_data = cursor.fetchall()
        
        print(f"[OK] 日本語データ取得: {len(japanese_data)} 件")
        for data in japanese_data:
            bamei, kisyu, chokyosi = data
            print(f"  馬名: {bamei}, 騎手: {kisyu}, 調教師: {chokyosi}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] UTF-8エンコーディングエラー: {e}")
        return False

def test_system_performance():
    """システムパフォーマンステスト"""
    print("\n=== システムパフォーマンステスト ===")
    
    try:
        import time
        start_time = time.time()
        
        conn = sqlite3.connect('ecore.db')
        cursor = conn.cursor()
        
        # 複雑なクエリの実行時間テスト
        cursor.execute("""
            SELECT 
                r.Year,
                r.MonthDay,
                r.JyoCD,
                r.RaceNum,
                r.Hondai,
                COUNT(u.Umaban) as horse_count
            FROM N_RACE r
            LEFT JOIN N_UMA_RACE u ON r.Year = u.Year 
                AND r.MonthDay = u.MonthDay 
                AND r.JyoCD = u.JyoCD 
                AND r.RaceNum = u.RaceNum
            WHERE r.Year >= '2024'
            GROUP BY r.Year, r.MonthDay, r.JyoCD, r.RaceNum
            ORDER BY r.Year DESC, r.MonthDay DESC
            LIMIT 100
        """)
        
        results = cursor.fetchall()
        end_time = time.time()
        
        execution_time = end_time - start_time
        print(f"[OK] 複雑クエリ実行時間: {execution_time:.3f}秒")
        print(f"[OK] 結果件数: {len(results)} 件")
        
        if execution_time < 1.0:
            print("[OK] パフォーマンス: 良好")
        elif execution_time < 3.0:
            print("[WARNING] パフォーマンス: 普通")
        else:
            print("[WARNING] パフォーマンス: 遅い")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] パフォーマンステストエラー: {e}")
        return False

def test_jvmonitor_fix():
    """JVMonitor修正状況テスト"""
    print("\n=== JVMonitor修正状況テスト ===")
    
    try:
        conn = sqlite3.connect('ecore.db')
        cursor = conn.cursor()
        
        # NL_SE_RACE_UMAテーブルの存在確認
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='NL_SE_RACE_UMA'
        """)
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("[OK] NL_SE_RACE_UMAテーブルが存在します")
            
            # データ数の確認
            cursor.execute("SELECT COUNT(*) FROM NL_SE_RACE_UMA")
            nl_count = cursor.fetchone()[0]
            print(f"[OK] NL_SE_RACE_UMA: {nl_count:,} 件")
            
            # 最新データの確認
            cursor.execute("SELECT MAX(Year || MonthDay) FROM NL_SE_RACE_UMA")
            latest_date = cursor.fetchone()[0]
            print(f"[OK] 最新データ日: {latest_date}")
            
            if nl_count > 0:
                print("[OK] JVMonitorエラーは修正済み")
                return True
            else:
                print("[WARNING] NL_SE_RACE_UMAにデータがありません")
                return False
        else:
            print("[ERROR] NL_SE_RACE_UMAテーブルが存在しません")
            return False
        
        conn.close()
        
    except Exception as e:
        print(f"[ERROR] JVMonitor修正テストエラー: {e}")
        return False

def test_file_system():
    """ファイルシステムテスト"""
    print("\n=== ファイルシステムテスト ===")
    
    required_files = [
        'ecore.db',
        'complete_race_system.py',
        'fix_jvmonitor_database.py'
    ]
    
    all_files_exist = True
    for file in required_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"[OK] {file}: {size:,} bytes")
        else:
            print(f"[ERROR] {file}: ファイルが見つかりません")
            all_files_exist = False
    
    return all_files_exist

def run_comprehensive_test():
    """包括的テスト実行"""
    print("=" * 60)
    print("🏇 競馬出馬表表示システム - ビルドチェック")
    print("=" * 60)
    
    tests = [
        ("ファイルシステム", test_file_system),
        ("データベース接続", test_database_connection),
        ("データ取得", test_data_retrieval),
        ("UTF-8エンコーディング", test_utf8_encoding),
        ("システムパフォーマンス", test_system_performance),
        ("JVMonitor修正状況", test_jvmonitor_fix)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{test_name}テスト実行中...")
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"[ERROR] {test_name}テストで例外が発生: {e}")
            results[test_name] = False
    
    # 結果サマリー
    print("\n" + "=" * 60)
    print("📊 テスト結果サマリー")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n総合結果: {passed}/{total} テスト通過")
    
    if passed == total:
        print("🎉 すべてのテストが通過しました！システムは正常に動作します。")
        return True
    else:
        print("⚠️  一部のテストが失敗しました。システムに問題がある可能性があります。")
        return False

if __name__ == "__main__":
    run_comprehensive_test()


