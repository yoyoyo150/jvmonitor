import sqlite3
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def create_excel_db(db_path: Path, sql_script_path: Path):
    print(f"=== 専用ExcelデータDB '{db_path.name}' の作成を開始します ===")

    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        sql_script = sql_script_path.read_text(encoding='utf-8')
        cursor.executescript(sql_script)
        conn.commit()

        print(f"[OK] 専用ExcelデータDB '{db_path.name}' が正常に作成されました。")
        print(f"スキーマ '{sql_script_path.name}' を適用しました。")

    except sqlite3.Error as e:
        print(f"[エラー] SQLiteデータベースの操作中にエラーが発生しました: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"[エラー] 予期せぬエラーが発生しました: {e}")
    finally:
        if conn:
            conn.close()
            print("データベース接続を閉じました。")

if __name__ == "__main__":
    # データベースファイルは 'trainer_prediction_system' ディレクトリの直下に作成
    db_path = Path("trainer_prediction_system/excel_data.db")
    sql_script_path = Path("trainer_prediction_system/sql/create_excel_db.sql")
    
    create_excel_db(db_path, sql_script_path)




