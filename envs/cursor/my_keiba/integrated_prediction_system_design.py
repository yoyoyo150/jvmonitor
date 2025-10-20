import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
import json
import os
import sys
import subprocess
import time

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

class IntegratedPredictionSystem:
    """統合予想理論システム（JVMonitor.exeベース）"""
    
    def __init__(self):
        self.jvmonitor_path = "C:\\my_project_folder\\envs\\cursor\\my_keiba\\JVMonitor\\JVMonitor\\bin\\Debug\\net6.0-windows\\JVMonitor.exe"
        self.ecore_db_path = "C:\\my_project_folder\\envs\\cursor\\my_keiba\\ecore.db"
        self.excel_db_path = "C:\\my_project_folder\\envs\\cursor\\my_keiba\\excel_data.db"
        self.jvmonitor_process = None
        
    def check_system_status(self):
        """システム状況確認"""
        print("=== 統合予想理論システム状況確認 ===")
        
        try:
            # JVMonitor.exeの存在確認
            if os.path.exists(self.jvmonitor_path):
                print("✅ JVMonitor.exe: 存在確認")
            else:
                print("❌ JVMonitor.exe: 見つかりません")
                return False
            
            # データベースの存在確認
            if os.path.exists(self.ecore_db_path):
                print("✅ ecore.db: 存在確認")
            else:
                print("❌ ecore.db: 見つかりません")
                return False
            
            if os.path.exists(self.excel_db_path):
                print("✅ excel_data.db: 存在確認")
            else:
                print("⚠️ excel_data.db: 存在しません（作成が必要）")
            
            return True
            
        except Exception as e:
            print(f"システム状況確認エラー: {e}")
            return False
    
    def start_jvmonitor(self):
        """JVMonitor.exe起動"""
        print("=== JVMonitor.exe起動 ===")
        
        try:
            # JVMonitor.exe起動
            self.jvmonitor_process = subprocess.Popen([
                self.jvmonitor_path
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            print("✅ JVMonitor.exe起動成功")
            return True
            
        except Exception as e:
            print(f"JVMonitor.exe起動エラー: {e}")
            return False
    
    def stop_jvmonitor(self):
        """JVMonitor.exe停止"""
        print("=== JVMonitor.exe停止 ===")
        
        try:
            if self.jvmonitor_process:
                self.jvmonitor_process.terminate()
                self.jvmonitor_process.wait(timeout=5)
                print("✅ JVMonitor.exe停止成功")
            else:
                print("⚠️ JVMonitor.exeプロセスが見つかりません")
            
        except Exception as e:
            print(f"JVMonitor.exe停止エラー: {e}")
    
    def check_database_connection(self):
        """データベース接続確認"""
        print("=== データベース接続確認 ===")
        
        try:
            # ecore.db接続確認
            conn_ecore = sqlite3.connect(self.ecore_db_path)
            cursor_ecore = conn_ecore.cursor()
            cursor_ecore.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 5")
            tables_ecore = cursor_ecore.fetchall()
            print(f"✅ ecore.db: {len(tables_ecore)}テーブル確認")
            conn_ecore.close()
            
            # excel_data.db接続確認（存在する場合）
            if os.path.exists(self.excel_db_path):
                conn_excel = sqlite3.connect(self.excel_db_path)
                cursor_excel = conn_excel.cursor()
                cursor_excel.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 5")
                tables_excel = cursor_excel.fetchall()
                print(f"✅ excel_data.db: {len(tables_excel)}テーブル確認")
                conn_excel.close()
            else:
                print("⚠️ excel_data.db: 作成が必要")
            
            return True
            
        except Exception as e:
            print(f"データベース接続確認エラー: {e}")
            return False
    
    def create_excel_database(self):
        """excel_data.db作成"""
        print("=== excel_data.db作成 ===")
        
        try:
            # excel_data.db作成
            conn = sqlite3.connect(self.excel_db_path)
            cursor = conn.cursor()
            
            # 基本テーブル作成
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS excel_marks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    SourceDate TEXT,
                    HorseNameS TEXT,
                    Trainer_Name TEXT,
                    Chaku INTEGER,
                    Mark5 TEXT,
                    Mark6 TEXT,
                    ZI_Index REAL,
                    ZM_Value REAL,
                    ImportedAt DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            
            print("✅ excel_data.db作成成功")
            return True
            
        except Exception as e:
            print(f"excel_data.db作成エラー: {e}")
            return False
    
    def run_integrated_system(self):
        """統合システム実行"""
        print("=== 統合予想理論システム実行 ===")
        
        try:
            # 1) システム状況確認
            if not self.check_system_status():
                return False
            
            # 2) データベース接続確認
            if not self.check_database_connection():
                return False
            
            # 3) excel_data.db作成（必要に応じて）
            if not os.path.exists(self.excel_db_path):
                if not self.create_excel_database():
                    return False
            
            # 4) JVMonitor.exe起動
            if not self.start_jvmonitor():
                return False
            
            print("✅ 統合予想理論システム起動完了")
            print("📋 運用フロー:")
            print("   1. JVMonitor.exeでデータ確認")
            print("   2. 予想理論システムで分析")
            print("   3. 結果を統合システムで管理")
            
            return True
            
        except Exception as e:
            print(f"統合システム実行エラー: {e}")
            return False

def main():
    system = IntegratedPredictionSystem()
    success = system.run_integrated_system()
    
    if success:
        print("\n✅ 統合予想理論システム起動成功")
        print("🎯 JVMonitor.exeが基本システムとして動作中")
    else:
        print("\n❌ 統合予想理論システム起動失敗")

if __name__ == "__main__":
    main()




