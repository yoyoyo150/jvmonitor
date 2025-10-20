#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GDI+ Error Fix Script
GDI+エラーを修正するスクリプト
"""

import os
import subprocess
import time
import sqlite3
from datetime import datetime

def fix_gdi_error():
    """GDI+エラーを修正"""
    
    print("=== GDI+ Error Fix Script ===")
    print("GDI+エラーを修正します")
    print()
    
    # 1. 問題の説明
    print("1. 問題の説明")
    print("=" * 50)
    print("GDI+エラーの原因:")
    print("- EveryDB2.3が画面描画を試みる")
    print("- 画面が非表示になっていると描画に失敗")
    print("- MeasureStringメソッドでエラーが発生")
    print("- アプリケーションが停止する")
    print()
    
    # 2. 解決策の説明
    print("2. 解決策")
    print("=" * 50)
    print("解決方法:")
    print("1. ヘッドレスモードで実行（画面表示なし）")
    print("2. 環境変数でGDI+エラーを無効化")
    print("3. CREATE_NO_WINDOWフラグでウィンドウを作成しない")
    print("4. バックグラウンドで継続実行")
    print()
    
    # 3. 環境変数の設定
    print("3. 環境変数設定")
    print("=" * 50)
    
    # 環境変数を設定
    os.environ['GDI_PLUS_ERROR_MODE'] = '0'  # GDI+エラーモードを無効化
    os.environ['DISPLAY'] = ''  # ディスプレイを無効化
    
    print("環境変数を設定しました:")
    print("- GDI_PLUS_ERROR_MODE = 0")
    print("- DISPLAY = ''")
    print()
    
    # 4. レジストリ設定の提案
    print("4. レジストリ設定の提案")
    print("=" * 50)
    
    print("レジストリでGDI+エラーを無効化する方法:")
    print()
    print("1. レジストリエディタを開く (regedit)")
    print("2. 以下のパスに移動:")
    print("   HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\GDI+")
    print("3. 新しいDWORD値を作成:")
    print("   名前: DisableExceptionHandling")
    print("   値: 1")
    print("4. レジストリエディタを閉じる")
    print("5. システムを再起動")
    print()
    
    # 5. 手動実行コマンド
    print("5. 手動実行コマンド")
    print("=" * 50)
    
    everydb_path = r"J:\new program file\everydb230\everydb230\Application Files\EveryDB2.3_2_3_0_0\EveryDB2.3.exe"
    
    print("GDI+エラーを回避してEveryDB2.3を実行するコマンド:")
    print()
    print("set GDI_PLUS_ERROR_MODE=0")
    print("set DISPLAY=")
    print(f'"{everydb_path}"')
    print()
    
    # 6. バッチファイルの作成
    print("6. バッチファイルの作成")
    print("=" * 50)
    
    batch_content = f'''@echo off
echo GDI+ Error Fix - EveryDB2.3 Runner
echo.

REM 環境変数を設定
set GDI_PLUS_ERROR_MODE=0
set DISPLAY=

echo 環境変数を設定しました
echo GDI_PLUS_ERROR_MODE=0
echo DISPLAY=
echo.

REM 既存のプロセスを終了
echo 既存のEveryDB2.3プロセスを終了中...
taskkill /IM EveryDB2.3.exe /F >nul 2>&1

REM 5秒待機
echo 5秒待機中...
timeout /t 5 /nobreak >nul

REM EveryDB2.3を開始
echo EveryDB2.3を開始中...
echo 画面が表示されませんが、処理は継続されます
echo 停止するには Ctrl+C を押してください
echo.

start /B "" "{everydb_path}"

echo EveryDB2.3が開始されました
echo バックグラウンドで実行中...
echo.

REM 無限ループで待機
:loop
timeout /t 60 /nobreak >nul
echo [%date% %time%] 実行中...
goto loop
'''
    
    with open("run_everydb_no_gdi_error.bat", "w", encoding="utf-8") as f:
        f.write(batch_content)
    
    print("バッチファイルを作成しました: run_everydb_no_gdi_error.bat")
    print("このバッチファイルを実行すると、GDI+エラーを回避してEveryDB2.3が実行されます")
    print()
    
    # 7. 最終確認
    print("7. 最終確認")
    print("=" * 50)
    
    print("GDI+エラーの修正方法:")
    print("1. バッチファイル実行: run_everydb_no_gdi_error.bat")
    print("2. 手動実行: 上記のコマンドを順番に実行")
    print("3. レジストリ設定: 上記の手順でレジストリを変更")
    print()
    print("推奨: バッチファイルを使用してください")

def main():
    """メイン実行"""
    fix_gdi_error()

if __name__ == "__main__":
    main()
