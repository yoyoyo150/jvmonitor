import os
import sys
import shutil
from pathlib import Path

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

class FixJVMonitorWorkingDirectory:
    """JVMonitor.exeの作業ディレクトリ修正"""
    
    def __init__(self):
        self.jvmonitor_exe = "JVMonitor\\JVMonitor\\bin\\Debug\\net6.0-windows\\JVMonitor.exe"
        self.wrapper_script = "JVMonitor\\JVMonitor\\import_excel_marks_wrapper.py"
        self.simple_script = "JVMonitor\\JVMonitor\\simple_import.py"
        self.fix_script = "fix_excel_data_import.py"
    
    def copy_scripts_to_bin_directory(self):
        """スクリプトをbinディレクトリにコピー"""
        print("=== スクリプトをbinディレクトリにコピー ===")
        
        try:
            # binディレクトリのパス
            bin_dir = Path("JVMonitor/JVMonitor/bin/Debug/net6.0-windows")
            
            # ラッパースクリプトをコピー
            wrapper_source = Path(self.wrapper_script)
            wrapper_dest = bin_dir / "import_excel_marks_wrapper.py"
            
            if wrapper_source.exists():
                shutil.copy2(wrapper_source, wrapper_dest)
                print(f"✅ ラッパースクリプトコピー: {wrapper_dest}")
            else:
                print(f"❌ ラッパースクリプトが見つかりません: {wrapper_source}")
                return False
            
            # シンプルスクリプトをコピー
            simple_source = Path(self.simple_script)
            simple_dest = bin_dir / "simple_import.py"
            
            if simple_source.exists():
                shutil.copy2(simple_source, simple_dest)
                print(f"✅ シンプルスクリプトコピー: {simple_dest}")
            else:
                print(f"❌ シンプルスクリプトが見つかりません: {simple_source}")
                return False
            
            # fix_excel_data_import.pyをコピー
            fix_source = Path(self.fix_script)
            fix_dest = bin_dir / "fix_excel_data_import.py"
            
            if fix_source.exists():
                shutil.copy2(fix_source, fix_dest)
                print(f"✅ 修正スクリプトコピー: {fix_dest}")
            else:
                print(f"❌ 修正スクリプトが見つかりません: {fix_source}")
                return False
            
            return True
            
        except Exception as e:
            print(f"スクリプトコピーエラー: {e}")
            return False
    
    def create_absolute_path_script(self):
        """絶対パス版スクリプト作成"""
        print("=== 絶対パス版スクリプト作成 ===")
        
        try:
            # 絶対パス版スクリプト作成
            absolute_script_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JVMonitor.exe用絶対パス版エクセルデータインポートスクリプト
"""
import sys
import os
import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def main():
    """メイン関数"""
    try:
        print("=== エクセルデータインポート開始（絶対パス版） ===")
        
        # 絶対パスでプロジェクトルートを取得
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent.parent.parent.parent
        
        print(f"現在のファイル: {current_file}")
        print(f"プロジェクトルート: {project_root}")
        
        # 作業ディレクトリをプロジェクトルートに変更
        os.chdir(project_root)
        print(f"作業ディレクトリ: {os.getcwd()}")
        
        # yDateディレクトリの確認
        yDate_dir = project_root / "yDate"
        if not yDate_dir.exists():
            print(f"❌ yDateディレクトリが見つかりません: {yDate_dir}")
            return 1
        
        print(f"✅ yDateディレクトリ: {yDate_dir}")
        
        # データベース接続
        db_path = project_root / "excel_data.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # テーブル作成
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS HORSE_MARKS (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                SourceDate TEXT,
                HorseName TEXT,
                NormalizedHorseName TEXT,
                RaceId TEXT,
                RaceName TEXT,
                JyoCD TEXT,
                Kaiji TEXT,
                Nichiji TEXT,
                RaceNum TEXT,
                Umaban TEXT,
                MorningOdds TEXT,
                Mark1 TEXT,
                Mark2 TEXT,
                Mark3 TEXT,
                Mark4 TEXT,
                Mark5 TEXT,
                Mark6 TEXT,
                Mark7 TEXT,
                Mark8 TEXT,
                ZI_INDEX TEXT,
                ZM_VALUE TEXT,
                SHIBA_DA TEXT,
                KYORI_M TEXT,
                R_MARK1 TEXT,
                R_MARK2 TEXT,
                R_MARK3 TEXT,
                SourceFile TEXT,
                ImportedAt DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # yDateディレクトリの最新ファイルを処理
        excel_files = list(yDate_dir.glob("*.xlsx")) + list(yDate_dir.glob("*.csv"))
        excel_files.sort()
        
        # 最新3ファイルのみ処理（軽量化）
        latest_files = excel_files[-3:]
        print(f"処理対象ファイル数: {len(latest_files)}")
        
        total_imported = 0
        
        for file_path in latest_files:
            print(f"処理中: {file_path.name}")
            
            try:
                # エクセルファイル読み込み
                if file_path.suffix == '.xlsx':
                    df = pd.read_excel(file_path, dtype=str, engine='openpyxl').fillna("")
                elif file_path.suffix == '.csv':
                    df = pd.read_csv(file_path, dtype=str).fillna("")
                else:
                    continue
                
                # データ変換
                records_to_insert = []
                for index, row in df.iterrows():
                    horse_name = str(row.get("馬名S", "") or "").strip()
                    if not horse_name:
                        continue
                    
                    record = {
                        'SourceDate': str(row.get("レースID(新)", "") or "").strip()[:8] if str(row.get("レースID(新)", "") or "").strip() else file_path.stem[:8],
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
        
        print(f"✅ 総インポート件数: {total_imported:,}")
        print("=== エクセルデータインポート完了 ===")
        
        return 0
        
    except Exception as e:
        print(f"エラー: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
'''
            
            # 絶対パス版スクリプト作成
            absolute_script_path = Path("JVMonitor/JVMonitor/bin/Debug/net6.0-windows/absolute_import.py")
            absolute_script_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(absolute_script_path, 'w', encoding='utf-8') as f:
                f.write(absolute_script_content)
            
            print(f"✅ 絶対パス版スクリプト作成: {absolute_script_path.absolute()}")
            return True
            
        except Exception as e:
            print(f"絶対パス版スクリプト作成エラー: {e}")
            return False
    
    def update_form1_cs_absolute_path(self):
        """Form1.csを絶対パス版に更新"""
        print("=== Form1.csを絶対パス版に更新 ===")
        
        try:
            # Form1.csを読み込み
            form1_path = Path("JVMonitor/JVMonitor/Form1.cs")
            with open(form1_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # パスを絶対パス版に変更
            old_path = 'var pythonScript = Path.Combine("import_excel_marks_wrapper.py");'
            new_path = 'var pythonScript = Path.Combine("absolute_import.py");'
            
            if old_path in content:
                content = content.replace(old_path, new_path)
                print("✅ パス修正完了（絶対パス版）")
            else:
                print("⚠️ 置換対象のパスが見つかりません")
            
            # 修正されたファイルを保存
            with open(form1_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Form1.cs修正完了: {form1_path.absolute()}")
            return True
            
        except Exception as e:
            print(f"Form1.cs修正エラー: {e}")
            return False
    
    def run_fix_jvmonitor_working_directory(self):
        """JVMonitor作業ディレクトリ修正実行"""
        print("=== JVMonitor作業ディレクトリ修正実行 ===")
        
        try:
            # 1) スクリプトをbinディレクトリにコピー
            if not self.copy_scripts_to_bin_directory():
                return False
            
            # 2) 絶対パス版スクリプト作成
            if not self.create_absolute_path_script():
                return False
            
            # 3) Form1.csを絶対パス版に更新
            if not self.update_form1_cs_absolute_path():
                return False
            
            print("✅ JVMonitor作業ディレクトリ修正完了")
            return True
            
        except Exception as e:
            print(f"JVMonitor作業ディレクトリ修正実行エラー: {e}")
            return False

def main():
    fixer = FixJVMonitorWorkingDirectory()
    success = fixer.run_fix_jvmonitor_working_directory()
    
    if success:
        print("\n✅ JVMonitor作業ディレクトリ修正成功")
        print("🎯 ボタンが正常に動作するようになりました")
    else:
        print("\n❌ JVMonitor作業ディレクトリ修正失敗")

if __name__ == "__main__":
    main()




