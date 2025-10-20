#!/usr/bin/env python3
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
