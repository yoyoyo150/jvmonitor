import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

DB_PATH = 'excel_data.db'

def check_table_structure():
    print("=== テーブル構造の確認 ===\n")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. HORSE_MARKSテーブルの構造を確認
    print("1. HORSE_MARKSテーブルの構造")
    cursor.execute("PRAGMA table_info(HORSE_MARKS)")
    columns = cursor.fetchall()
    
    print("カラム情報:")
    for col in columns:
        cid, name, type_name, not_null, default_value, pk = col
        pk_info = " (PRIMARY KEY)" if pk else ""
        print(f"  {name}: {type_name}{pk_info}")

    # 2. インデックス情報を確認
    print("\n2. インデックス情報")
    cursor.execute("PRAGMA index_list(HORSE_MARKS)")
    indexes = cursor.fetchall()
    
    for index in indexes:
        seq, name, unique, origin, partial = index
        unique_info = " (UNIQUE)" if unique else ""
        print(f"  インデックス: {name}{unique_info}")

    # 3. 主キー制約を確認
    print("\n3. 主キー制約の確認")
    cursor.execute("PRAGMA table_xinfo(HORSE_MARKS)")
    xinfo = cursor.fetchall()
    
    pk_columns = []
    for col in xinfo:
        if len(col) >= 6:
            cid, name, type_name, not_null, default_value, pk = col[:6]
            if pk > 0:
                pk_columns.append((pk, name))
    
    if pk_columns:
        pk_columns.sort()
        print("主キーカラム:")
        for pk_order, col_name in pk_columns:
            print(f"  {pk_order}: {col_name}")
    else:
        print("[WARNING] 主キーが設定されていません")

    # 4. テーブルの作成SQLを確認
    print("\n4. テーブルの作成SQL")
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='HORSE_MARKS'")
    create_sql = cursor.fetchone()
    
    if create_sql:
        print("CREATE TABLE文:")
        print(create_sql[0])
    else:
        print("[ERROR] テーブル情報が見つかりません")

    conn.close()

if __name__ == '__main__':
    check_table_structure()
