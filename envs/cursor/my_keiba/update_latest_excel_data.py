import sqlite3
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def update_latest_excel_data():
    """最新のExcelデータを更新"""
    print("=== 最新のExcelデータ更新 ===")
    
    try:
        # データベース接続
        conn = sqlite3.connect('excel_data.db')
        cursor = conn.cursor()
        
        # yDateディレクトリの最新ファイルを取得
        yDate_dir = Path("yDate")
        excel_files = sorted(list(yDate_dir.glob("*.xlsx")))
        
        if not excel_files:
            print("❌ yDateディレクトリにExcelファイルが見つかりません")
            return False
        
        # 最新5ファイルを処理
        latest_files = excel_files[-5:]
        print(f"処理対象ファイル数: {len(latest_files)}")
        
        total_imported = 0
        
        for file_path in latest_files:
            print(f"\n--- 処理中: {file_path.name} ---")
            
            try:
                # エクセルファイル読み込み
                df = pd.read_excel(file_path, dtype=str, engine='openpyxl').fillna("")
                
                # データ変換
                records_to_insert = []
                for index, row in df.iterrows():
                    horse_name = str(row.get("馬名S", "") or "").strip()
                    if not horse_name:
                        continue
                    
                    # 日付の抽出
                    source_date = str(row.get("レースID(新)", "") or "").strip()
                    if not source_date or len(source_date) < 8:
                        source_date = file_path.stem[:8]
                    
                    record = {
                        'SourceDate': source_date,
                        'HorseName': horse_name,
                        'NormalizedHorseName': horse_name,
                        'RaceId': str(row.get("レースID(新)", "") or "").strip(),
                        'RaceName': str(row.get("レース名", "") or "").strip(),
                        'JyoCD': str(row.get("場", "") or "").strip(),
                        'Kaiji': "",
                        'Nichiji': "",
                        'RaceNum': str(row.get("R", "") or "").strip(),
                        'Umaban': str(row.get("馬番", "") or "").strip(),
                        'MorningOdds': str(row.get("朝オッズ", "") or "").strip(),
                        'Mark1': str(row.get("馬印1", "") or "").strip(),
                        'Mark2': str(row.get("馬印2", "") or "").strip(),
                        'Mark3': str(row.get("馬印3", "") or "").strip(),
                        'Mark4': str(row.get("馬印4", "") or "").strip(),
                        'Mark5': str(row.get("馬印5", "") or "").strip(),
                        'Mark6': str(row.get("馬印6", "") or "").strip(),
                        'Mark7': str(row.get("馬印7", "") or "").strip(),
                        'Mark8': str(row.get("馬印8", "") or "").strip(),
                        'ZI_INDEX': str(row.get("ZI指数", "") or "").strip(),
                        'ZM_VALUE': str(row.get("ZM", "") or "").strip(),
                        'SHIBA_DA': str(row.get("芝ダ", "") or "").strip(),
                        'KYORI_M': str(row.get("距離", "") or "").strip(),
                        'R_MARK1': str(row.get("R印1", "") or "").strip(),
                        'R_MARK2': str(row.get("R印2", "") or "").strip(),
                        'R_MARK3': str(row.get("R印3", "") or "").strip(),
                        'SourceFile': file_path.name,
                        'ImportedAt': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    records_to_insert.append(record)
                
                # データベースに挿入
                if records_to_insert:
                    column_names = list(records_to_insert[0].keys())
                    placeholders = ", ".join(f":{name}" for name in column_names)
                    
                    sql = f"""
                        INSERT OR REPLACE INTO HORSE_MARKS ({', '.join(column_names)})
                        VALUES ({placeholders})
                    """
                    
                    cursor.executemany(sql, records_to_insert)
                    conn.commit()
                    
                    print(f"  ✅ {len(records_to_insert)}件インポート完了")
                    total_imported += len(records_to_insert)
                
            except Exception as e:
                print(f"  ❌ エラー: {e}")
                continue
        
        conn.close()
        
        print(f"\n✅ 総インポート件数: {total_imported:,}")
        print("=== 最新のExcelデータ更新完了 ===")
        
        return True
        
    except Exception as e:
        print(f"エラー: {e}")
        return False

if __name__ == "__main__":
    update_latest_excel_data()




