import sqlite3
import json
import os
from datetime import datetime

def create_jvmonitor_fix():
    """JVMonitorの「ないない」問題を解決するスクリプト"""
    
    print("=== JVMonitor表示問題の解決 ===")
    
    # 1. データベースの整合性チェック
    def check_database_integrity():
        """データベースの整合性をチェック"""
        print("\n【データベース整合性チェック】")
        
        try:
            conn = sqlite3.connect('excel_data.db')
            cursor = conn.cursor()
            
            # テーブル構造確認
            cursor.execute("PRAGMA table_info(HORSE_MARKS)")
            columns = cursor.fetchall()
            print("HORSE_MARKSテーブル構造:")
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
            
            # データ統計
            cursor.execute("SELECT COUNT(*) FROM HORSE_MARKS")
            total_count = cursor.fetchone()[0]
            print(f"\n総レコード数: {total_count}")
            
            # 日付別統計
            cursor.execute("""
                SELECT SourceDate, COUNT(*) 
                FROM HORSE_MARKS 
                GROUP BY SourceDate 
                ORDER BY SourceDate DESC 
                LIMIT 10
            """)
            date_stats = cursor.fetchall()
            print("\n日付別データ数:")
            for date, count in date_stats:
                print(f"  {date}: {count}件")
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"エラー: {e}")
            return False
    
    # 2. データ検索の改善
    def improved_data_search(date):
        """改善されたデータ検索"""
        print(f"\n【{date}のデータ検索】")
        
        try:
            conn = sqlite3.connect('excel_data.db')
            cursor = conn.cursor()
            
            # 複数の検索パターン
            search_patterns = [
                f"SourceDate = '{date}'",
                f"SourceDate LIKE '%{date}%'",
                f"SourceDate = '{date[:8]}'",
                f"SourceDate LIKE '{date[:6]}%'"
            ]
            
            found_data = []
            for i, pattern in enumerate(search_patterns):
                query = f"SELECT * FROM HORSE_MARKS WHERE {pattern}"
                cursor.execute(query)
                results = cursor.fetchall()
                
                if results:
                    print(f"パターン{i+1} ({pattern}): {len(results)}件発見")
                    found_data.extend(results)
                else:
                    print(f"パターン{i+1} ({pattern}): データなし")
            
            if found_data:
                print(f"合計: {len(found_data)}件のデータを発見")
                return found_data
            else:
                print("どのパターンでもデータが見つかりませんでした")
                return []
                
        except Exception as e:
            print(f"検索エラー: {e}")
            return []
        finally:
            conn.close()
    
    # 3. データベース最適化
    def optimize_database():
        """データベースを最適化"""
        print("\n【データベース最適化】")
        
        try:
            conn = sqlite3.connect('excel_data.db')
            cursor = conn.cursor()
            
            # インデックス作成
            print("インデックスを作成中...")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_source_date ON HORSE_MARKS(SourceDate)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_horse_name ON HORSE_MARKS(HorseName)")
            
            # データベース最適化
            cursor.execute("VACUUM")
            cursor.execute("ANALYZE")
            
            print("データベース最適化完了")
            conn.close()
            return True
            
        except Exception as e:
            print(f"最適化エラー: {e}")
            return False
    
    # 4. 実行
    print("JVMonitor表示問題の解決を開始...")
    
    # 整合性チェック
    if not check_database_integrity():
        print("データベース整合性チェックに失敗しました")
        return
    
    # データ検索テスト
    test_dates = ['20251013', '20251012', '20251011']
    for date in test_dates:
        improved_data_search(date)
    
    # データベース最適化
    optimize_database()
    
    print("\n【解決策のまとめ】")
    print("1. データベースインデックスを追加")
    print("2. 複数の検索パターンを使用")
    print("3. データベース最適化を実行")
    print("4. JVMonitorを再起動")
    
    print("\n【次のステップ】")
    print("1. JVMonitorを一度閉じる")
    print("2. このスクリプトを実行")
    print("3. JVMonitorを再起動")
    print("4. データが正しく表示されることを確認")

if __name__ == "__main__":
    create_jvmonitor_fix()








