import sqlite3
import os

def integrate_marks_to_ecore():
    """excel_data.dbのMark5/Mark6データをecore.dbに統合"""
    
    print("=== Mark5/Mark6データの統合 ===")
    
    # 1. バックアップ作成
    if os.path.exists('ecore.db'):
        import shutil
        shutil.copy2('ecore.db', 'ecore_backup.db')
        print("✅ ecore.dbのバックアップ作成完了")
    
    # 2. データベース接続
    conn_excel = sqlite3.connect('excel_data.db')
    conn_ecore = sqlite3.connect('ecore.db')
    
    cursor_excel = conn_excel.cursor()
    cursor_ecore = conn_ecore.cursor()
    
    # 3. ecore.dbのN_UMA_RACEテーブルにMark5/Mark6カラムを追加
    print("\n=== N_UMA_RACEテーブルにMark5/Mark6カラムを追加 ===")
    
    try:
        cursor_ecore.execute("ALTER TABLE N_UMA_RACE ADD COLUMN Mark5 TEXT")
        print("✅ Mark5カラム追加完了")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("⚠️ Mark5カラムは既に存在")
        else:
            print(f"❌ Mark5カラム追加エラー: {e}")
    
    try:
        cursor_ecore.execute("ALTER TABLE N_UMA_RACE ADD COLUMN Mark6 TEXT")
        print("✅ Mark6カラム追加完了")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("⚠️ Mark6カラムは既に存在")
        else:
            print(f"❌ Mark6カラム追加エラー: {e}")
    
    # 4. ナムラクレアのデータ統合テスト
    print("\n=== ナムラクレアのデータ統合テスト ===")
    
    # excel_data.dbからナムラクレアのデータを取得
    cursor_excel.execute("""
        SELECT SourceDate, HorseName, Mark5, Mark6, ZI_INDEX
        FROM HORSE_MARKS
        WHERE HorseName = 'ナムラクレア'
        ORDER BY SourceDate DESC
        LIMIT 3
    """)
    
    excel_data = cursor_excel.fetchall()
    print("excel_data.dbのデータ:")
    for row in excel_data:
        print(f"  {row[0]} | {row[1]} | M5:{row[2]} | M6:{row[3]} | ZI:{row[4]}")
    
    # ecore.dbのN_UMA_RACEでナムラクレアを検索
    cursor_ecore.execute("""
        SELECT Kaiji, Nichiji, RaceNum, Bamei, Mark5, Mark6
        FROM N_UMA_RACE
        WHERE Bamei LIKE '%ナムラクレア%'
        ORDER BY Kaiji DESC, Nichiji DESC, RaceNum DESC
        LIMIT 3
    """)
    
    ecore_data = cursor_ecore.fetchall()
    print("\necore.dbのデータ:")
    for row in ecore_data:
        print(f"  {row[0]}/{row[1]} R{row[2]} | {row[3]} | M5:{row[4]} | M6:{row[5]}")
    
    # 5. 統合の提案
    print("\n=== 統合の提案 ===")
    print("1. 日付と馬名でマッチング")
    print("2. Mark5/Mark6データを更新")
    print("3. 統合後の確認")
    
    conn_excel.close()
    conn_ecore.close()

if __name__ == "__main__":
    integrate_marks_to_ecore()




