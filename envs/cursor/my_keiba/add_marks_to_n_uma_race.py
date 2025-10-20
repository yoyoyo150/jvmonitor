import sqlite3
import os

def add_marks_to_n_uma_race():
    """N_UMA_RACEテーブルにMark5/Mark6カラムを追加"""
    
    print("=== N_UMA_RACEテーブルにMark5/Mark6カラムを追加 ===")
    
    # 1. バックアップ作成
    if os.path.exists('ecore.db'):
        import shutil
        shutil.copy2('ecore.db', 'ecore_backup.db')
        print("✅ ecore.dbのバックアップ作成完了")
    
    # 2. データベース接続
    conn = sqlite3.connect('ecore.db')
    cursor = conn.cursor()
    
    # 3. 現在のテーブル構造確認
    cursor.execute("PRAGMA table_info(N_UMA_RACE)")
    columns = cursor.fetchall()
    existing_columns = [col[1] for col in columns]
    print(f"既存カラム数: {len(existing_columns)}")
    
    # 4. Mark5/Mark6カラムを追加
    print("\n=== Mark5/Mark6カラムの追加 ===")
    
    if 'Mark5' not in existing_columns:
        try:
            cursor.execute("ALTER TABLE N_UMA_RACE ADD COLUMN Mark5 TEXT")
            print("✅ Mark5カラム追加完了")
        except Exception as e:
            print(f"❌ Mark5カラム追加エラー: {e}")
    else:
        print("⚠️ Mark5カラムは既に存在")
    
    if 'Mark6' not in existing_columns:
        try:
            cursor.execute("ALTER TABLE N_UMA_RACE ADD COLUMN Mark6 TEXT")
            print("✅ Mark6カラム追加完了")
        except Exception as e:
            print(f"❌ Mark6カラム追加エラー: {e}")
    else:
        print("⚠️ Mark6カラムは既に存在")
    
    # 5. 更新後のテーブル構造確認
    cursor.execute("PRAGMA table_info(N_UMA_RACE)")
    columns = cursor.fetchall()
    mark_columns = [col for col in columns if 'Mark' in col[1]]
    print(f"\nMark関連カラム: {[col[1] for col in mark_columns]}")
    
    # 6. サンプルデータの確認
    cursor.execute("""
        SELECT Kaiji, Nichiji, RaceNum, Bamei, Mark5, Mark6
        FROM N_UMA_RACE
        WHERE Bamei LIKE '%ナムラクレア%'
        ORDER BY Kaiji DESC, Nichiji DESC, RaceNum DESC
        LIMIT 3
    """)
    
    data = cursor.fetchall()
    print(f"\nナムラクレアのデータ（Mark5/Mark6カラム追加後）:")
    for row in data:
        print(f"  {row[0]}/{row[1]} R{row[2]} | {row[3]} | M5:{row[4]} | M6:{row[5]}")
    
    conn.commit()
    conn.close()
    
    print("\n✅ N_UMA_RACEテーブルの更新完了")
    print("次に、JVMonitorでMark5/Mark6データを入力してください")

if __name__ == "__main__":
    add_marks_to_n_uma_race()




