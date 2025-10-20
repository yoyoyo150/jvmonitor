#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
7日分一括更新システム
投入時刻から7日分のエクセルデータを確実に更新
"""
import os
import subprocess
import sys
from datetime import datetime, timedelta
import sqlite3

def check_7day_data_status():
    """7日分のデータ状況確認"""
    print("=== 7日分データ状況確認 ===")
    
    today = datetime.now()
    missing_dates = []
    existing_dates = []
    
    conn = sqlite3.connect('excel_data.db')
    cursor = conn.cursor()
    
    for i in range(7):
        date = today - timedelta(days=i)
        date_str = date.strftime('%Y%m%d')
        table_name = f"EXCEL_DATA_{date_str}"
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        exists = cursor.fetchone()
        
        if exists:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            existing_dates.append((date_str, count))
            print(f"✅ {date_str}: {count}件")
        else:
            missing_dates.append(date_str)
            print(f"❌ {date_str}: データなし")
    
    conn.close()
    
    return missing_dates, existing_dates

def check_ydate_files():
    """yDateディレクトリのファイル確認"""
    print("\n=== yDateファイル確認 ===")
    
    if not os.path.exists('yDate'):
        print("❌ yDateディレクトリが存在しません")
        return []
    
    files = []
    for file in os.listdir('yDate'):
        if file.endswith('.xlsx') or file.endswith('.csv'):
            files.append(file)
            print(f"📁 {file}")
    
    return files

def run_enhanced_excel_import(mode='incremental'):
    """enhanced_excel_import.pyを実行"""
    print(f"\n=== エクセルインポート実行 ({mode}) ===")
    
    script_path = os.path.join(os.path.dirname(__file__), 'enhanced_excel_import.py')
    
    if not os.path.exists(script_path):
        print(f"❌ スクリプトが見つかりません: {script_path}")
        return False
    
    try:
        cmd = [sys.executable, script_path, '--mode', mode]
        print(f"実行コマンド: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        print(f"終了コード: {result.returncode}")
        
        if result.stdout:
            print("標準出力:")
            print(result.stdout)
        
        if result.stderr:
            print("エラー出力:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ 実行エラー: {e}")
        return False

def force_update_missing_dates(missing_dates):
    """欠損日付のデータを強制更新"""
    print(f"\n=== 欠損データ強制更新 ===")
    
    if not missing_dates:
        print("✅ 欠損データはありません")
        return True
    
    print(f"欠損日付: {missing_dates}")
    
    # yDateディレクトリの対応ファイル確認
    ydate_files = check_ydate_files()
    
    for date_str in missing_dates:
        matching_files = [f for f in ydate_files if date_str in f]
        
        if matching_files:
            print(f"\n📅 {date_str} 対応ファイル: {matching_files}")
            
            # 個別にインポート実行
            for file in matching_files:
                file_path = os.path.join('yDate', file)
                if os.path.exists(file_path):
                    print(f"  処理中: {file}")
                    # ここで個別ファイル処理ロジックを実装
                    # 現在はenhanced_excel_import.pyが全ファイル処理するため、
                    # 個別処理は今後の改善点
        else:
            print(f"❌ {date_str}: 対応するyDateファイルが見つかりません")
    
    return True

def verify_8_10_data():
    """8/10データの特別確認"""
    print("\n=== 8/10データ特別確認 ===")
    
    # EXCEL_DATA_20250810の確認
    conn = sqlite3.connect('excel_data.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='EXCEL_DATA_20250810'")
    exists = cursor.fetchone()
    
    if exists:
        cursor.execute("SELECT COUNT(*) FROM EXCEL_DATA_20250810")
        count = cursor.fetchone()[0]
        print(f"✅ EXCEL_DATA_20250810: {count}件")
        
        # サンプルデータ確認
        cursor.execute("SELECT 馬名S, 加速, オリジナル, ZI指数 FROM EXCEL_DATA_20250810 LIMIT 3")
        samples = cursor.fetchall()
        
        print("サンプルデータ:")
        for sample in samples:
            print(f"  {sample[0]}: 加速={sample[1]}, オリジナル={sample[2]}, ZI指数={sample[3]}")
    else:
        print("❌ EXCEL_DATA_20250810: テーブルが存在しません")
        
        # yDate/20250810rase.xlsxの確認
        file_path = os.path.join('yDate', '20250810rase.xlsx')
        if os.path.exists(file_path):
            print("📁 yDate/20250810rase.xlsx: 存在")
            print("→ enhanced_excel_import.pyで再処理が必要")
        else:
            print("❌ yDate/20250810rase.xlsx: 存在しない")
    
    conn.close()

def main():
    """メイン処理"""
    print("🔄 7日分一括更新システム")
    print("=" * 50)
    
    # 1. 現状確認
    missing_dates, existing_dates = check_7day_data_status()
    
    # 2. yDateファイル確認
    ydate_files = check_ydate_files()
    
    # 3. 8/10データ特別確認
    verify_8_10_data()
    
    # 4. 欠損がある場合は更新実行
    if missing_dates:
        print(f"\n⚠️  {len(missing_dates)}日分のデータが欠損しています")
        
        # インクリメンタル更新実行
        print("\n🔄 インクリメンタル更新実行...")
        success = run_enhanced_excel_import('incremental')
        
        if not success:
            print("\n🔄 フル更新で再試行...")
            success = run_enhanced_excel_import('full')
        
        if success:
            print("\n✅ 更新完了 - 再確認中...")
            missing_after, existing_after = check_7day_data_status()
            
            if not missing_after:
                print("🎉 全ての欠損データが解決されました！")
            else:
                print(f"⚠️  まだ {len(missing_after)} 日分の欠損があります: {missing_after}")
        else:
            print("❌ 更新に失敗しました")
    else:
        print("✅ 7日分のデータは全て存在しています")
    
    print("\n" + "=" * 50)
    print("📋 次のステップ:")
    print("1. JVMonitor.exeで「整合性チェック」ボタンを押して確認")
    print("2. M5第一段階フィルターでテスト実行")
    print("3. 問題があれば「エクセル更新(全件)」で再処理")

if __name__ == "__main__":
    main()
