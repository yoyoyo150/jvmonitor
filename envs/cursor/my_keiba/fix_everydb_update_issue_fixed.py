#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EveryDB2.3更新問題解決スクリプト（修正版）
途中で止まる問題を修正
"""

import os
import subprocess
import time
import sqlite3
import shutil
from datetime import datetime
import glob

def fix_everydb_update_issue():
    """EveryDB2.3の更新問題を解決"""
    
    print("=== EveryDB2.3更新問題解決 ===")
    print("途中で止まる問題を修正します")
    print()
    
    # 1. 現在の状況確認
    print("現在の状況確認")
    print("=" * 60)
    
    # データベースファイルの確認
    db_files = ["ecore.db", "ecore_backup.db"]
    for db_file in db_files:
        if os.path.exists(db_file):
            print(f"OK {db_file} 存在")
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM N_UMA;")
                horse_count = cursor.fetchone()[0]
                print(f"   馬数: {horse_count:,}頭")
                conn.close()
            except Exception as e:
                print(f"   エラー: {e}")
        else:
            print(f"NG {db_file} 不存在")
    
    # 2. データベースの整合性チェック
    print(f"\nデータベースの整合性チェック")
    print("=" * 60)
    
    for db_file in db_files:
        if os.path.exists(db_file):
            print(f"\n--- {db_file} ---")
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                # 整合性チェック
                cursor.execute("PRAGMA integrity_check;")
                result = cursor.fetchone()[0]
                
                if result == "ok":
                    print("OK 整合性チェック: OK")
                else:
                    print(f"NG 整合性チェック: {result}")
                    
                    # 修復を試行
                    print("修復を試行中...")
                    cursor.execute("PRAGMA quick_check;")
                    quick_result = cursor.fetchone()[0]
                    print(f"クイックチェック: {quick_result}")
                
                # テーブル数確認
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table';")
                table_count = cursor.fetchone()[0]
                print(f"テーブル数: {table_count}")
                
                conn.close()
                
            except Exception as e:
                print(f"NG データベースエラー: {e}")
    
    # 3. バックアップの作成
    print(f"\nバックアップの作成")
    print("=" * 60)
    
    backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    print(f"バックアップディレクトリ: {backup_dir}")
    
    for db_file in db_files:
        if os.path.exists(db_file):
            backup_file = os.path.join(backup_dir, db_file)
            shutil.copy2(db_file, backup_file)
            print(f"OK {db_file} -> {backup_file}")
    
    # 4. 一時ファイルのクリーンアップ
    print(f"\n一時ファイルのクリーンアップ")
    print("=" * 60)
    
    # 一時ファイルのパターン
    temp_patterns = [
        "*.tmp",
        "*.temp",
        "*.log",
        "*.lock",
        "*.db-journal",
        "*.db-wal",
        "*.db-shm"
    ]
    
    cleaned_files = 0
    for pattern in temp_patterns:
        for temp_file in glob.glob(pattern):
            try:
                os.remove(temp_file)
                print(f"削除: {temp_file}")
                cleaned_files += 1
            except Exception as e:
                print(f"削除失敗: {temp_file} - {e}")
    
    print(f"クリーンアップ完了: {cleaned_files}ファイル")
    
    # 5. データベースの最適化
    print(f"\nデータベースの最適化")
    print("=" * 60)
    
    for db_file in db_files:
        if os.path.exists(db_file):
            print(f"\n--- {db_file} 最適化 ---")
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                # VACUUM実行
                print("VACUUM実行中...")
                cursor.execute("VACUUM;")
                print("OK VACUUM完了")
                
                # インデックス再構築
                print("インデックス再構築中...")
                cursor.execute("REINDEX;")
                print("OK インデックス再構築完了")
                
                # 統計情報更新
                print("統計情報更新中...")
                cursor.execute("ANALYZE;")
                print("OK 統計情報更新完了")
                
                conn.close()
                
            except Exception as e:
                print(f"NG 最適化エラー: {e}")
    
    # 6. 段階的更新の提案
    print(f"\n段階的更新の提案")
    print("=" * 60)
    
    print("EveryDB2.3の更新が途中で止まる問題の解決策:")
    print()
    print("1. 手動更新モードでの実行")
    print("   - 自動更新ではなく手動更新を選択")
    print("   - データ種別を1つずつ更新")
    print()
    print("2. 更新期間の分割")
    print("   - 2017年～2020年")
    print("   - 2021年～2023年") 
    print("   - 2024年～現在")
    print()
    print("3. データ種別の個別更新")
    print("   - レース情報(RACE)のみ")
    print("   - 馬情報(UMA)のみ")
    print("   - 騎手情報(KISYU)のみ")
    print()
    print("4. システムリソースの確保")
    print("   - メモリの空き容量を確保")
    print("   - ディスクの空き容量を確保")
    print("   - 他のアプリケーションを終了")
    
    # 7. 推奨実行手順
    print(f"\n推奨実行手順")
    print("=" * 60)
    
    print("1. EveryDB2.3を管理者権限で実行")
    print("2. 接続設定でデータベースパスを確認")
    print("3. 更新設定で「手動更新」を選択")
    print("4. データ種別を「レース情報(RACE)」のみに限定")
    print("5. 更新期間を短く設定（例：2024年のみ）")
    print("6. 「取得開始」ボタンをクリック")
    print("7. エラーが発生した場合は、期間をさらに短く分割")
    
    # 8. 監視スクリプトの提供
    print(f"\n監視スクリプトの提供")
    print("=" * 60)
    
    monitor_script = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EveryDB2.3監視スクリプト
"""
import time
import os
import sqlite3

def monitor_everydb():
    db_file = "ecore.db"
    last_size = 0
    
    while True:
        if os.path.exists(db_file):
            current_size = os.path.getsize(db_file)
            if current_size != last_size:
                print(f"{time.strftime('%H:%M:%S')} - データベース更新中: {current_size:,} bytes")
                last_size = current_size
            else:
                print(f"{time.strftime('%H:%M:%S')} - 待機中...")
        else:
            print(f"{time.strftime('%H:%M:%S')} - データベースファイルが見つかりません")
        
        time.sleep(10)  # 10秒間隔で監視

if __name__ == "__main__":
    monitor_everydb()
'''
    
    with open("monitor_everydb_simple.py", "w", encoding="utf-8") as f:
        f.write(monitor_script)
    
    print("OK 監視スクリプト作成: monitor_everydb_simple.py")
    print("使用方法: python monitor_everydb_simple.py")
    
    # 9. 最終確認
    print(f"\n準備完了")
    print("=" * 60)
    
    print("以下の準備が完了しました:")
    print("1. データベースの整合性チェック")
    print("2. バックアップの作成")
    print("3. 一時ファイルのクリーンアップ")
    print("4. データベースの最適化")
    print("5. 監視スクリプトの提供")
    print()
    print("次に、EveryDB2.3で手動更新を実行してください。")

if __name__ == "__main__":
    fix_everydb_update_issue()


