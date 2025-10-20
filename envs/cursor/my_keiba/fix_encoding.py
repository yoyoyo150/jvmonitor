#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文字化け修正スクリプト
PowerShellの文字エンコーディング問題を解決
"""

import subprocess
import sys
import os
from datetime import datetime

def fix_powershell_encoding():
    """PowerShellの文字エンコーディングを修正"""
    print("PowerShellの文字エンコーディングを修正中...")
    
    try:
        # PowerShellの文字エンコーディング設定
        ps_commands = [
            "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8",
            "[Console]::InputEncoding = [System.Text.Encoding]::UTF8",
            "$OutputEncoding = [System.Text.Encoding]::UTF8",
            "chcp 65001"
        ]
        
        for cmd in ps_commands:
            try:
                result = subprocess.run(
                    ["powershell", "-Command", cmd],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='ignore'
                )
                print(f"実行: {cmd}")
            except Exception as e:
                print(f"エラー: {cmd} - {e}")
        
        print("文字エンコーディング設定完了")
        return True
        
    except Exception as e:
        print(f"文字エンコーディング設定エラー: {e}")
        return False

def test_encoding():
    """文字エンコーディングのテスト"""
    print("\n文字エンコーディングテスト:")
    
    test_strings = [
        "競馬データ",
        "レース印",
        "馬印",
        "予想システム",
        "今日の日付: 2025年10月13日"
    ]
    
    for test_str in test_strings:
        try:
            # UTF-8エンコード/デコードテスト
            encoded = test_str.encode('utf-8')
            decoded = encoded.decode('utf-8')
            print(f"OK {decoded}")
        except Exception as e:
            print(f"NG {test_str} - エラー: {e}")

def run_with_fixed_encoding(script_path):
    """修正されたエンコーディングでスクリプトを実行"""
    print(f"\n修正されたエンコーディングでスクリプトを実行: {script_path}")
    
    try:
        # 環境変数を設定
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        env['PYTHONUTF8'] = '1'
        
        # スクリプトを実行
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            env=env
        )
        
        print("標準出力:")
        print(result.stdout)
        
        if result.stderr:
            print("標準エラー:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"スクリプト実行エラー: {e}")
        return False

def main():
    """メイン処理"""
    print("=" * 60)
    print("文字化け修正システム")
    print("=" * 60)
    
    # 現在の日時を表示
    now = datetime.now()
    print(f"実行日時: {now.strftime('%Y年%m月%d日 %H:%M:%S')}")
    
    # 文字エンコーディング修正
    if fix_powershell_encoding():
        print("OK PowerShell文字エンコーディング修正完了")
    else:
        print("NG PowerShell文字エンコーディング修正失敗")
    
    # 文字エンコーディングテスト
    test_encoding()
    
    # データベース確認スクリプトを修正されたエンコーディングで実行
    print("\n" + "=" * 60)
    print("修正されたエンコーディングでデータベース確認")
    print("=" * 60)
    
    if run_with_fixed_encoding("check_data_status.py"):
        print("OK データベース確認完了")
    else:
        print("NG データベース確認失敗")
    
    print("\n" + "=" * 60)
    print("文字化け修正完了")
    print("=" * 60)

if __name__ == "__main__":
    main()
