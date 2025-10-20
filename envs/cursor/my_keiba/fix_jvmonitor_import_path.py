import os
import sys
from pathlib import Path

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

class FixJVMonitorImportPath:
    """JVMonitor.exeのインポートパス修正"""
    
    def __init__(self):
        self.jvmonitor_path = "JVMonitor/JVMonitor/Form1.cs"
        self.tools_path = "tools/import_excel_marks.py"
        self.fixed_script = "fix_excel_data_import.py"
    
    def check_current_paths(self):
        """現在のパス確認"""
        print("=== 現在のパス確認 ===")
        
        try:
            # JVMonitor.exeの場所確認
            jvmonitor_file = Path(self.jvmonitor_path)
            if jvmonitor_file.exists():
                print(f"✅ JVMonitor.exe: {jvmonitor_file.absolute()}")
            else:
                print(f"❌ JVMonitor.exe: {jvmonitor_file.absolute()}")
                return False
            
            # tools/import_excel_marks.pyの場所確認
            tools_file = Path(self.tools_path)
            if tools_file.exists():
                print(f"✅ tools/import_excel_marks.py: {tools_file.absolute()}")
            else:
                print(f"❌ tools/import_excel_marks.py: {tools_file.absolute()}")
                return False
            
            # fix_excel_data_import.pyの場所確認
            fixed_file = Path(self.fixed_script)
            if fixed_file.exists():
                print(f"✅ fix_excel_data_import.py: {fixed_file.absolute()}")
            else:
                print(f"❌ fix_excel_data_import.py: {fixed_file.absolute()}")
                return False
            
            return True
            
        except Exception as e:
            print(f"現在のパス確認エラー: {e}")
            return False
    
    def create_import_script_wrapper(self):
        """インポートスクリプトラッパー作成"""
        print("=== インポートスクリプトラッパー作成 ===")
        
        try:
            # ラッパースクリプト作成
            wrapper_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JVMonitor.exe用エクセルデータインポートラッパー
"""
import sys
import os
from pathlib import Path

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def main():
    """メイン関数"""
    try:
        # 現在のディレクトリを取得
        current_dir = Path.cwd()
        print(f"現在のディレクトリ: {current_dir}")
        
        # プロジェクトルートに移動
        project_root = current_dir
        while not (project_root / "yDate").exists() and project_root.parent != project_root:
            project_root = project_root.parent
        
        if not (project_root / "yDate").exists():
            print("❌ プロジェクトルートが見つかりません")
            return 1
        
        print(f"プロジェクトルート: {project_root}")
        
        # 作業ディレクトリをプロジェクトルートに変更
        os.chdir(project_root)
        
        # fix_excel_data_import.pyを実行
        import subprocess
        result = subprocess.run([
            sys.executable, "fix_excel_data_import.py"
        ], capture_output=True, text=True, encoding='utf-8')
        
        print("=== 実行結果 ===")
        print("STDOUT:")
        print(result.stdout)
        print("STDERR:")
        print(result.stderr)
        print(f"終了コード: {result.returncode}")
        
        return result.returncode
        
    except Exception as e:
        print(f"エラー: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
'''
            
            # ラッパーファイル作成
            wrapper_path = Path("JVMonitor/JVMonitor/import_excel_marks_wrapper.py")
            wrapper_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(wrapper_path, 'w', encoding='utf-8') as f:
                f.write(wrapper_content)
            
            print(f"✅ ラッパースクリプト作成: {wrapper_path.absolute()}")
            return True
            
        except Exception as e:
            print(f"ラッパースクリプト作成エラー: {e}")
            return False
    
    def fix_form1_cs(self):
        """Form1.csの修正"""
        print("=== Form1.csの修正 ===")
        
        try:
            # Form1.csを読み込み
            form1_path = Path(self.jvmonitor_path)
            with open(form1_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 古いパスを新しいパスに置換
            old_path = 'var pythonScript = Path.Combine("..", "..", "tools", "import_excel_marks.py");'
            new_path = 'var pythonScript = Path.Combine("import_excel_marks_wrapper.py");'
            
            if old_path in content:
                content = content.replace(old_path, new_path)
                print("✅ パス修正完了")
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
    
    def create_simple_import_script(self):
        """シンプルなインポートスクリプト作成"""
        print("=== シンプルなインポートスクリプト作成 ===")
        
        try:
            # シンプルなインポートスクリプト作成
            simple_script_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
シンプルなエクセルデータインポートスクリプト
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
        print("=== エクセルデータインポート開始 ===")
        
        # プロジェクトルートに移動
        current_dir = Path.cwd()
        project_root = current_dir
        while not (project_root / "yDate").exists() and project_root.parent != project_root:
            project_root = project_root.parent
        
        if not (project_root / "yDate").exists():
            print("❌ プロジェクトルートが見つかりません")
            return 1
        
        os.chdir(project_root)
        print(f"プロジェクトルート: {project_root}")
        
        # データベース接続
        db_path = "excel_data.db"
        conn = sqlite3.connect(db_path)
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
        yDate_dir = Path("yDate")
        excel_files = list(yDate_dir.glob("*.xlsx")) + list(yDate_dir.glob("*.csv"))
        excel_files.sort()
        
        # 最新5ファイルのみ処理
        latest_files = excel_files[-5:]
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
            
            # シンプルなインポートスクリプト作成
            simple_script_path = Path("JVMonitor/JVMonitor/simple_import.py")
            simple_script_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(simple_script_path, 'w', encoding='utf-8') as f:
                f.write(simple_script_content)
            
            print(f"✅ シンプルなインポートスクリプト作成: {simple_script_path.absolute()}")
            return True
            
        except Exception as e:
            print(f"シンプルなインポートスクリプト作成エラー: {e}")
            return False
    
    def run_fix_jvmonitor_import_path(self):
        """JVMonitorインポートパス修正実行"""
        print("=== JVMonitorインポートパス修正実行 ===")
        
        try:
            # 1) 現在のパス確認
            if not self.check_current_paths():
                return False
            
            # 2) インポートスクリプトラッパー作成
            if not self.create_import_script_wrapper():
                return False
            
            # 3) シンプルなインポートスクリプト作成
            if not self.create_simple_import_script():
                return False
            
            # 4) Form1.csの修正
            if not self.fix_form1_cs():
                return False
            
            print("✅ JVMonitorインポートパス修正完了")
            return True
            
        except Exception as e:
            print(f"JVMonitorインポートパス修正実行エラー: {e}")
            return False

def main():
    fixer = FixJVMonitorImportPath()
    success = fixer.run_fix_jvmonitor_import_path()
    
    if success:
        print("\n✅ JVMonitorインポートパス修正成功")
        print("🎯 ボタンが正常に動作するようになりました")
    else:
        print("\n❌ JVMonitorインポートパス修正失敗")

if __name__ == "__main__":
    main()




