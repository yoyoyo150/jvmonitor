import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import pandas as pd
import json
from datetime import datetime
import os

class IntegratedUISystem:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("競馬分析システム - 統合UI")
        self.root.geometry("1400x900")
        
        # データベース接続
        self.ecore_conn = None
        self.excel_conn = None
        self.integrated_conn = None
        
        self.setup_ui()
        self.connect_databases()
    
    def setup_ui(self):
        # メインフレーム
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # タイトル
        title_label = ttk.Label(main_frame, text="競馬分析システム - 統合UI", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # タブの作成
        notebook = ttk.Notebook(main_frame)
        
        # 馬カードタブ
        self.horse_tab = ttk.Frame(notebook)
        notebook.add(self.horse_tab, text="馬カード")
        
        # 調教師分析タブ
        self.trainer_tab = ttk.Frame(notebook)
        notebook.add(self.trainer_tab, text="調教師分析")
        
        # 予想候補タブ
        self.prediction_tab = ttk.Frame(notebook)
        notebook.add(self.prediction_tab, text="予想候補")
        
        # データベース管理タブ
        self.db_tab = ttk.Frame(notebook)
        notebook.add(self.db_tab, text="データベース管理")
        
        notebook.pack(fill='both', expand=True)
        
        # 各タブの内容を設定
        self.setup_horse_tab()
        self.setup_trainer_tab()
        self.setup_prediction_tab()
        self.setup_db_tab()
    
    def setup_horse_tab(self):
        # 馬名検索フレーム
        search_frame = ttk.LabelFrame(self.horse_tab, text="馬名検索")
        search_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(search_frame, text="馬名:").grid(row=0, column=0, padx=5, pady=5)
        self.horse_search_entry = ttk.Entry(search_frame, width=30)
        self.horse_search_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(search_frame, text="検索", 
                  command=self.search_horse).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Button(search_frame, text="血統番号で検索", 
                  command=self.search_by_ketto).grid(row=0, column=3, padx=5, pady=5)
        
        # 検索結果フレーム
        results_frame = ttk.LabelFrame(self.horse_tab, text="検索結果")
        results_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # 検索結果リスト
        self.horse_results_tree = ttk.Treeview(results_frame, columns=('KettoNum', 'Bamei'), show='headings')
        self.horse_results_tree.heading('KettoNum', text='血統番号')
        self.horse_results_tree.heading('Bamei', text='馬名')
        self.horse_results_tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 馬情報表示フレーム
        info_frame = ttk.LabelFrame(self.horse_tab, text="馬情報")
        info_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.horse_info_text = tk.Text(info_frame, height=15, width=100)
        self.horse_info_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # スクロールバー
        scrollbar = ttk.Scrollbar(info_frame, orient='vertical', command=self.horse_info_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.horse_info_text.configure(yscrollcommand=scrollbar.set)
        
        # ダブルクリックで馬カード生成
        self.horse_results_tree.bind('<Double-1>', self.generate_horse_card)
    
    def setup_trainer_tab(self):
        # 調教師分析フレーム
        analysis_frame = ttk.LabelFrame(self.trainer_tab, text="調教師分析")
        analysis_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(analysis_frame, text="調教師分析実行", 
                  command=self.run_trainer_analysis).pack(side='left', padx=5, pady=5)
        
        ttk.Button(analysis_frame, text="結果をCSV出力", 
                  command=self.export_trainer_results).pack(side='left', padx=5, pady=5)
        
        # 分析結果表示
        results_frame = ttk.LabelFrame(self.trainer_tab, text="分析結果")
        results_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.trainer_results_tree = ttk.Treeview(results_frame, 
                                               columns=('TrainerName', 'TotalRaces', 'WinRate', 'PlaceRate', 'Score'),
                                               show='headings')
        self.trainer_results_tree.heading('TrainerName', text='調教師名')
        self.trainer_results_tree.heading('TotalRaces', text='総レース数')
        self.trainer_results_tree.heading('WinRate', text='勝率')
        self.trainer_results_tree.heading('PlaceRate', text='着順率')
        self.trainer_results_tree.heading('Score', text='スコア')
        self.trainer_results_tree.pack(fill='both', expand=True, padx=5, pady=5)
    
    def setup_prediction_tab(self):
        # 予想候補フレーム
        prediction_frame = ttk.LabelFrame(self.prediction_tab, text="予想候補生成")
        prediction_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(prediction_frame, text="予想候補生成", 
                  command=self.generate_predictions).pack(side='left', padx=5, pady=5)
        
        ttk.Button(prediction_frame, text="候補をCSV出力", 
                  command=self.export_predictions).pack(side='left', padx=5, pady=5)
        
        # 予想候補表示
        candidates_frame = ttk.LabelFrame(self.prediction_tab, text="予想候補")
        candidates_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.candidates_tree = ttk.Treeview(candidates_frame, 
                                          columns=('HorseName', 'TrainerName', 'Score', 'Mark5', 'Mark6'),
                                          show='headings')
        self.candidates_tree.heading('HorseName', text='馬名')
        self.candidates_tree.heading('TrainerName', text='調教師')
        self.candidates_tree.heading('Score', text='スコア')
        self.candidates_tree.heading('Mark5', text='Mark5')
        self.candidates_tree.heading('Mark6', text='Mark6')
        self.candidates_tree.pack(fill='both', expand=True, padx=5, pady=5)
    
    def setup_db_tab(self):
        # データベース情報フレーム
        db_info_frame = ttk.LabelFrame(self.db_tab, text="データベース情報")
        db_info_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(db_info_frame, text="データベース情報更新", 
                  command=self.update_db_info).pack(side='left', padx=5, pady=5)
        
        # データベース情報表示
        self.db_info_text = tk.Text(self.db_tab, height=20, width=100)
        self.db_info_text.pack(fill='both', expand=True, padx=10, pady=5)
        
        # スクロールバー
        scrollbar = ttk.Scrollbar(self.db_tab, orient='vertical', command=self.db_info_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.db_info_text.configure(yscrollcommand=scrollbar.set)
    
    def connect_databases(self):
        """データベース接続"""
        try:
            # ecore.db接続
            if os.path.exists("ecore.db"):
                self.ecore_conn = sqlite3.connect("ecore.db")
            
            # excel_data.db接続
            if os.path.exists("trainer_prediction_system/excel_data.db"):
                self.excel_conn = sqlite3.connect("trainer_prediction_system/excel_data.db")
            
            # integrated_horse_system.db接続
            if os.path.exists("integrated_horse_system.db"):
                self.integrated_conn = sqlite3.connect("integrated_horse_system.db")
            
            self.update_db_info()
            
        except Exception as e:
            messagebox.showerror("エラー", f"データベース接続エラー: {e}")
    
    def search_horse(self):
        """馬名検索"""
        search_term = self.horse_search_entry.get()
        if not search_term:
            messagebox.showwarning("警告", "検索語を入力してください")
            return
        
        try:
            if self.ecore_conn:
                query = """
                SELECT KettoNum, Bamei
                FROM N_UMA
                WHERE Bamei LIKE ?
                LIMIT 20
                """
                df = pd.read_sql_query(query, self.ecore_conn, params=[f'%{search_term}%'])
                
                # 検索結果をクリア
                for item in self.horse_results_tree.get_children():
                    self.horse_results_tree.delete(item)
                
                # 検索結果を表示
                for _, row in df.iterrows():
                    self.horse_results_tree.insert('', 'end', values=(row['KettoNum'], row['Bamei']))
                
                if df.empty:
                    messagebox.showinfo("情報", "該当する馬が見つかりませんでした")
            
        except Exception as e:
            messagebox.showerror("エラー", f"検索エラー: {e}")
    
    def search_by_ketto(self):
        """血統番号で検索"""
        ketto_num = tk.simpledialog.askstring("血統番号検索", "血統番号を入力してください:")
        if ketto_num:
            try:
                if self.ecore_conn:
                    query = "SELECT KettoNum, Bamei FROM N_UMA WHERE KettoNum = ?"
                    df = pd.read_sql_query(query, self.ecore_conn, params=[ketto_num])
                    
                    if not df.empty:
                        # 検索結果をクリア
                        for item in self.horse_results_tree.get_children():
                            self.horse_results_tree.delete(item)
                        
                        # 検索結果を表示
                        row = df.iloc[0]
                        self.horse_results_tree.insert('', 'end', values=(row['KettoNum'], row['Bamei']))
                    else:
                        messagebox.showinfo("情報", "該当する馬が見つかりませんでした")
            
            except Exception as e:
                messagebox.showerror("エラー", f"検索エラー: {e}")
    
    def generate_horse_card(self, event):
        """馬カード生成"""
        selection = self.horse_results_tree.selection()
        if not selection:
            return
        
        item = self.horse_results_tree.item(selection[0])
        ketto_num = item['values'][0]
        horse_name = item['values'][1]
        
        try:
            # 基本情報取得
            if self.ecore_conn:
                basic_query = """
                SELECT KettoNum, Bamei, BirthDate, SexCD, HinsyuCD, KeiroCD,
                       TozaiCD, ChokyosiRyakusyo, BreederName, SanchiName, BanusiName
                FROM N_UMA
                WHERE KettoNum = ?
                """
                basic_df = pd.read_sql_query(basic_query, self.ecore_conn, params=[ketto_num])
                
                if not basic_df.empty:
                    basic_info = basic_df.iloc[0]
                    
                    # 血統情報取得
                    pedigree_query = """
                    SELECT Ketto3InfoBamei1 AS Father, Ketto3InfoHansyokuNum1 AS FatherKettoNum,
                           Ketto3InfoBamei2 AS Mother, Ketto3InfoHansyokuNum2 AS MotherKettoNum
                    FROM N_UMA
                    WHERE KettoNum = ?
                    """
                    pedigree_df = pd.read_sql_query(pedigree_query, self.ecore_conn, params=[ketto_num])
                    
                    # レース結果取得
                    race_query = """
                    SELECT Year || MonthDay AS RaceDate, JyoCD, RaceNum, KakuteiJyuni, Odds, Ninki,
                           KisyuRyakusyo AS Jockey, ChokyosiRyakusyo AS Trainer
                    FROM N_UMA_RACE
                    WHERE KettoNum = ?
                    ORDER BY RaceDate DESC
                    LIMIT 5
                    """
                    race_df = pd.read_sql_query(race_query, self.ecore_conn, params=[ketto_num])
                    
                    # 独自変数取得
                    custom_vars = None
                    if self.excel_conn:
                        custom_query = """
                        SELECT SourceDate, Mark5, Mark6, ZI_Index, Trainer_Name
                        FROM excel_marks
                        WHERE HorseNameS = ?
                        ORDER BY SourceDate DESC
                        LIMIT 3
                        """
                        custom_df = pd.read_sql_query(custom_query, self.excel_conn, params=[horse_name])
                        if not custom_df.empty:
                            custom_vars = custom_df
                    
                    # 馬カード表示
                    self.display_horse_card(basic_info, pedigree_df, race_df, custom_vars)
                
        except Exception as e:
            messagebox.showerror("エラー", f"馬カード生成エラー: {e}")
    
    def display_horse_card(self, basic_info, pedigree_df, race_df, custom_vars):
        """馬カード表示"""
        self.horse_info_text.delete(1.0, tk.END)
        
        # 基本情報
        card_text = f"=== 馬カード: {basic_info['Bamei']} ===\n\n"
        card_text += f"血統番号: {basic_info['KettoNum']}\n"
        card_text += f"生年月日: {basic_info['BirthDate']}\n"
        card_text += f"性別: {basic_info['SexCD']}\n"
        card_text += f"品種: {basic_info['HinsyuCD']}\n"
        card_text += f"毛色: {basic_info['KeiroCD']}\n"
        card_text += f"東西: {basic_info['TozaiCD']}\n"
        card_text += f"調教師: {basic_info['ChokyosiRyakusyo']}\n"
        card_text += f"生産者: {basic_info['BreederName']}\n"
        card_text += f"産地: {basic_info['SanchiName']}\n"
        card_text += f"馬主: {basic_info['BanusiName']}\n\n"
        
        # 血統情報
        if not pedigree_df.empty:
            pedigree_info = pedigree_df.iloc[0]
            card_text += "--- 血統情報 ---\n"
            card_text += f"父: {pedigree_info['FatherKettoNum']} - {pedigree_info['Father']}\n"
            card_text += f"母: {pedigree_info['MotherKettoNum']} - {pedigree_info['Mother']}\n\n"
        
        # レース結果
        if not race_df.empty:
            card_text += "--- レース結果（最新5件） ---\n"
            for _, race in race_df.iterrows():
                card_text += f"{race['RaceDate']} {race['JyoCD']}{race['RaceNum']}R "
                card_text += f"着順:{race['KakuteiJyuni']} オッズ:{race['Odds']} "
                card_text += f"人気:{race['Ninki']} 騎手:{race['Jockey']}\n"
            card_text += "\n"
        
        # 独自変数
        if custom_vars is not None and not custom_vars.empty:
            card_text += "--- 独自変数（最新3件） ---\n"
            for _, var in custom_vars.iterrows():
                card_text += f"{var['SourceDate']} Mark5:{var['Mark5']} Mark6:{var['Mark6']} "
                card_text += f"ZI_Index:{var['ZI_Index']} 調教師:{var['Trainer_Name']}\n"
        
        self.horse_info_text.insert(tk.END, card_text)
    
    def run_trainer_analysis(self):
        """調教師分析実行"""
        try:
            # 調教師分析システムを実行
            import subprocess
            result = subprocess.run(['python', 'trainer_prediction_system/run_analysis.py'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                messagebox.showinfo("成功", "調教師分析が完了しました")
                self.load_trainer_results()
            else:
                messagebox.showerror("エラー", f"分析エラー: {result.stderr}")
        
        except Exception as e:
            messagebox.showerror("エラー", f"分析実行エラー: {e}")
    
    def load_trainer_results(self):
        """調教師分析結果を読み込み"""
        try:
            # 最新の分析結果ファイルを検索
            output_dir = "outputs"
            if os.path.exists(output_dir):
                csv_files = [f for f in os.listdir(output_dir) if f.startswith('trainer_analysis_') and f.endswith('.csv')]
                if csv_files:
                    latest_file = max(csv_files)
                    df = pd.read_csv(os.path.join(output_dir, latest_file))
                    
                    # 結果をクリア
                    for item in self.trainer_results_tree.get_children():
                        self.trainer_results_tree.delete(item)
                    
                    # 結果を表示
                    for _, row in df.iterrows():
                        self.trainer_results_tree.insert('', 'end', values=(
                            row['TrainerName'], row['TotalRaces'], 
                            f"{row['WinRate']:.1%}", f"{row['PlaceRate']:.1%}", 
                            f"{row['Score']:.2f}"
                        ))
        
        except Exception as e:
            messagebox.showerror("エラー", f"結果読み込みエラー: {e}")
    
    def export_trainer_results(self):
        """調教師分析結果をCSV出力"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                title="調教師分析結果を保存"
            )
            if filename:
                # 最新の分析結果ファイルをコピー
                output_dir = "outputs"
                if os.path.exists(output_dir):
                    csv_files = [f for f in os.listdir(output_dir) if f.startswith('trainer_analysis_') and f.endswith('.csv')]
                    if csv_files:
                        latest_file = max(csv_files)
                        import shutil
                        shutil.copy2(os.path.join(output_dir, latest_file), filename)
                        messagebox.showinfo("成功", f"結果を保存しました: {filename}")
        
        except Exception as e:
            messagebox.showerror("エラー", f"出力エラー: {e}")
    
    def generate_predictions(self):
        """予想候補生成"""
        try:
            # 予想候補生成システムを実行
            import subprocess
            result = subprocess.run(['python', 'tools/recommend_candidates.py'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                messagebox.showinfo("成功", "予想候補生成が完了しました")
                self.load_predictions()
            else:
                messagebox.showerror("エラー", f"予想候補生成エラー: {result.stderr}")
        
        except Exception as e:
            messagebox.showerror("エラー", f"予想候補生成エラー: {e}")
    
    def load_predictions(self):
        """予想候補を読み込み"""
        try:
            # 最新の予想候補ファイルを検索
            output_dir = "outputs"
            if os.path.exists(output_dir):
                csv_files = [f for f in os.listdir(output_dir) if f.startswith('candidates_') and f.endswith('.csv')]
                if csv_files:
                    latest_file = max(csv_files)
                    df = pd.read_csv(os.path.join(output_dir, latest_file))
                    
                    # 結果をクリア
                    for item in self.candidates_tree.get_children():
                        self.candidates_tree.delete(item)
                    
                    # 結果を表示
                    for _, row in df.iterrows():
                        self.candidates_tree.insert('', 'end', values=(
                            row['HorseName'], row['TrainerName'], 
                            f"{row['Score']:.2f}", row['Mark5'], row['Mark6']
                        ))
        
        except Exception as e:
            messagebox.showerror("エラー", f"予想候補読み込みエラー: {e}")
    
    def export_predictions(self):
        """予想候補をCSV出力"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                title="予想候補を保存"
            )
            if filename:
                # 最新の予想候補ファイルをコピー
                output_dir = "outputs"
                if os.path.exists(output_dir):
                    csv_files = [f for f in os.listdir(output_dir) if f.startswith('candidates_') and f.endswith('.csv')]
                    if csv_files:
                        latest_file = max(csv_files)
                        import shutil
                        shutil.copy2(os.path.join(output_dir, latest_file), filename)
                        messagebox.showinfo("成功", f"予想候補を保存しました: {filename}")
        
        except Exception as e:
            messagebox.showerror("エラー", f"出力エラー: {e}")
    
    def update_db_info(self):
        """データベース情報更新"""
        try:
            self.db_info_text.delete(1.0, tk.END)
            
            info_text = "=== データベース情報 ===\n\n"
            
            # ecore.db情報
            if self.ecore_conn:
                cursor = self.ecore_conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM N_UMA")
                horse_count = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM N_UMA_RACE")
                race_count = cursor.fetchone()[0]
                info_text += f"ecore.db:\n"
                info_text += f"  馬数: {horse_count:,}頭\n"
                info_text += f"  レース数: {race_count:,}件\n\n"
            
            # excel_data.db情報
            if self.excel_conn:
                cursor = self.excel_conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM excel_marks")
                marks_count = cursor.fetchone()[0]
                info_text += f"excel_data.db:\n"
                info_text += f"  独自変数: {marks_count:,}件\n\n"
            
            # integrated_horse_system.db情報
            if self.integrated_conn:
                cursor = self.integrated_conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM horse_master")
                integrated_horse_count = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM race_results")
                integrated_race_count = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM custom_variables")
                integrated_custom_count = cursor.fetchone()[0]
                info_text += f"integrated_horse_system.db:\n"
                info_text += f"  馬数: {integrated_horse_count:,}頭\n"
                info_text += f"  レース数: {integrated_race_count:,}件\n"
                info_text += f"  独自変数: {integrated_custom_count:,}件\n\n"
            
            # 出力ファイル情報
            output_dir = "outputs"
            if os.path.exists(output_dir):
                files = os.listdir(output_dir)
                csv_files = [f for f in files if f.endswith('.csv')]
                json_files = [f for f in files if f.endswith('.json')]
                info_text += f"出力ファイル:\n"
                info_text += f"  CSVファイル: {len(csv_files)}件\n"
                info_text += f"  JSONファイル: {len(json_files)}件\n"
            
            self.db_info_text.insert(tk.END, info_text)
        
        except Exception as e:
            self.db_info_text.insert(tk.END, f"データベース情報取得エラー: {e}")
    
    def run(self):
        """アプリケーション実行"""
        self.root.mainloop()

if __name__ == "__main__":
    app = IntegratedUISystem()
    app.run()




