import sqlite3
import json
import os
from datetime import datetime

def fix_display_issue():
    """データは存在するのに「ないない」と表示される問題の解決"""
    
    print("=== データ表示問題の解決策 ===")
    
    # 1. データベース接続の確認
    print("\n【1. データベース接続確認】")
    
    try:
        conn = sqlite3.connect('excel_data.db')
        cursor = conn.cursor()
        print("OK: excel_data.db に接続成功")
        
        # テーブル存在確認
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"テーブル一覧: {[t[0] for t in tables]}")
        
        conn.close()
    except Exception as e:
        print(f"NG: データベース接続エラー - {e}")
        return
    
    # 2. 正しいクエリ方法の提供
    print("\n【2. 正しいクエリ方法】")
    
    def get_horse_marks_by_date(date):
        """指定日付の馬印データを取得"""
        try:
            conn = sqlite3.connect('excel_data.db')
            cursor = conn.cursor()
            
            # 複数の日付形式で検索
            queries = [
                f"SELECT * FROM HORSE_MARKS WHERE SourceDate = '{date}'",
                f"SELECT * FROM HORSE_MARKS WHERE SourceDate LIKE '%{date}%'",
                f"SELECT * FROM HORSE_MARKS WHERE SourceDate = '{date[:8]}'"
            ]
            
            for i, query in enumerate(queries):
                cursor.execute(query)
                results = cursor.fetchall()
                if results:
                    print(f"クエリ{i+1}で{len(results)}件のデータを発見")
                    return results
            
            print("どのクエリでもデータが見つかりませんでした")
            return []
            
        except Exception as e:
            print(f"クエリエラー: {e}")
            return []
        finally:
            conn.close()
    
    # 3. データ検索のテスト
    print("\n【3. データ検索テスト】")
    test_dates = ['20251013', '20251012', '20251011']
    
    for date in test_dates:
        print(f"\n--- {date} の検索 ---")
        data = get_horse_marks_by_date(date)
        if data:
            print(f"発見: {len(data)}件")
            # 最初の3件を表示
            for i, row in enumerate(data[:3]):
                print(f"  {i+1}: {row[1] if len(row) > 1 else 'N/A'}")
        else:
            print("データなし")
    
    # 4. 解決策の提案
    print("\n【4. 解決策の提案】")
    print("A. クエリ条件の修正")
    print("B. データベースインデックスの追加")
    print("C. キャッシュクリア")
    print("D. アプリケーション再起動")

def create_data_checker():
    """データ存在チェッカーを作成"""
    
    checker_code = '''
import sqlite3
import json

def check_data_exists(date):
    """指定日付のデータ存在確認"""
    try:
        conn = sqlite3.connect('excel_data.db')
        cursor = conn.cursor()
        
        # 複数の検索パターン
        patterns = [
            f"SourceDate = '{date}'",
            f"SourceDate LIKE '%{date}%'",
            f"SourceDate = '{date[:8]}'"
        ]
        
        for pattern in patterns:
            query = f"SELECT COUNT(*) FROM HORSE_MARKS WHERE {pattern}"
            cursor.execute(query)
            count = cursor.fetchone()[0]
            if count > 0:
                print(f"パターン '{pattern}': {count}件発見")
                return True
        
        print("データが見つかりませんでした")
        return False
        
    except Exception as e:
        print(f"エラー: {e}")
        return False
    finally:
        conn.close()

# 使用例
if __name__ == "__main__":
    check_data_exists("20251013")
'''
    
    with open('data_checker.py', 'w', encoding='utf-8') as f:
        f.write(checker_code)
    
    print("\n【5. データチェッカーを作成】")
    print("data_checker.py を作成しました")

if __name__ == "__main__":
    fix_display_issue()
    create_data_checker()








