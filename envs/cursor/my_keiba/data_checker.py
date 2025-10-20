
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
