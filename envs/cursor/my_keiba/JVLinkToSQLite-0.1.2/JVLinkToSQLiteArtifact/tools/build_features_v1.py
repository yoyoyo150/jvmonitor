import pandas as pd
import numpy as np
import sqlite3
import json
import re
import os
import sys
import argparse
from pathlib import Path

# 文字化け対策
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

class FeatureBuilder:
    def __init__(self, alias_config_path='alias_config.json'):
        config_path = Path(__file__).parent.parent / alias_config_path
        print(f"設定ファイルを読み込みます: {config_path}")
        with open(config_path, 'r', encoding='utf-8') as f:
            self.aliases = json.load(f)
        self.track_map = {
            '札幌': '01', '函館': '02', '福島': '03', '新潟': '04', '東京': '05',
            '中山': '06', '中京': '07', '京都': '08', '阪神': '09', '小倉': '10',
            '札': '01', '函': '02', '福': '03', '新': '04', '東': '05',
            '中': '06', '名': '07', '京': '08', '阪': '09', '小': '10'
        }

    def _find_col(self, df, keys):
        """エイリアスのリストを受け取り、DataFrameに存在する列名を返す"""
        df_cols = {str(c).strip().lower(): str(c).strip() for c in df.columns}
        for key in keys:
            key_lower = str(key).lower()
            if key_lower in df_cols:
                return df_cols[key_lower]
        return None

    def _process_single_feature(self, df, features, section, key, numeric=False):
        """単一の特徴量を処理してfeatures DataFrameに追加する"""
        aliases = self.aliases[section].get(key)
        if not aliases:
            return

        col = self._find_col(df, aliases)
        if col:
            if numeric:
                features[key] = pd.to_numeric(df[col], errors='coerce')
            else:
                features[key] = df[col].str.strip()
        else:
            print(f"  - 警告: {section} の列 '{key}' が見つかりません。")
            features[key] = np.nan if numeric else None

    def process_file(self, file_path):
        try:
            if file_path.suffix == '.xlsx':
                df = pd.read_excel(file_path, dtype=str).fillna("")
            else:
                df = pd.read_csv(file_path, dtype=str, encoding='cp932', on_bad_lines='warn').fillna("")
        except Exception as e:
            print(f"  - ファイル読み込みエラー: {file_path.name} ({e})")
            return None

        df.columns = [str(c).strip() for c in df.columns]
        features = pd.DataFrame(index=df.index)

        # --- 必須キー: レースキーの特定 ---
        col_track_race = self._find_col(df, self.aliases['race_keys']['track_race_raw'])
        if not col_track_race:
            print(f"  - 必須列 '場 R' が見つかりません。スキップします。")
            return None
        
        track_race_norm = df[col_track_race].str.strip().str.replace(r'[\s　]', '', regex=True)
        features['track_code'] = track_race_norm.str[0].map(self.track_map)
        features['race_num'] = pd.to_numeric(track_race_norm.str[1:].str.extract(r'(\d+)')[0], errors='coerce')

        # --- 必須キー: 馬番 ---
        self._process_single_feature(df, features, 'horse_data', 'horse_number', numeric=True)

        # --- 全ての特徴量を動的に処理 ---
        all_sections = {
            'race_keys': False, 'race_indicators': False, 'horse_data': False,
            'prev_race_horse_data': False, 'bloodline': False
        }
        
        for section, is_numeric_section in all_sections.items():
            if section not in self.aliases:
                continue
            for key in self.aliases[section]:
                # 既に処理済みのキーはスキップ
                if key in ['track_race_raw', 'horse_number']:
                    continue
                # is_numeric_section は将来的な型判定のために残置
                self._process_single_feature(df, features, section, key, numeric=False)

        features['source_file'] = file_path.name
        
        # 必須キーが欠損している行を削除
        final_features = features.dropna(subset=['track_code', 'race_num', 'horse_number'])
        if len(features) > 0 and len(final_features) == 0:
            print(f"  - 警告: ファイル内の全行で必須キー(track_code, race_num, horse_number)が欠損しています。")
        
        return final_features


    def run(self, ydate_dir, out_path):
        all_features = []
        ydate_path = Path(ydate_dir)
        files = [f for f in sorted(ydate_path.glob("**/*")) if (f.suffix in ['.xlsx', '.csv'] and not f.name.startswith('~$'))]
        print(f"{len(files)}個のファイルを処理します...")

        for file_path in files:
            print(f"- 処理中: {file_path.name}")
            processed_df = self.process_file(file_path)
            if processed_df is not None and not processed_df.empty:
                all_features.append(processed_df)

        if not all_features:
            print("有効なデータが1行もありませんでした。alias_config.jsonの列名とExcelのヘッダが一致しているか、必須キーが有効か確認してください。")
            return

        final_df = pd.concat(all_features, ignore_index=True)
        
        # Add a summary of loaded columns
        print("\n--- 読み込み成功列のサマリー ---")
        for col in final_df.columns:
            if col not in ['track_code', 'race_num', 'source_file']:
                 # Count non-null values for each feature
                non_null_count = final_df[col].notna().sum()
                if non_null_count > 0:
                    print(f"  - {col}: {non_null_count}行")
        print("--------------------\n")

        output_dir = Path(out_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        final_df.to_csv(out_path, index=False, encoding='utf-8-sig')
        print(f"特徴量ファイル ({len(final_df)}行) が {out_path} に出力されました。")

def main():
    parser = argparse.ArgumentParser(description="Build features from Excel/CSV files.")
    parser.add_argument("--ydate-dir", required=True, help="Path to yDate directory.")
    parser.add_argument("--out", required=True, help="Output path for the feature CSV file.")
    parser.add_argument("--alias", default="alias_config.json", help="Path to alias config file.")
    args = parser.parse_args()

    print("特徴量生成スクリプト(v1改)を実行します...")
    builder = FeatureBuilder(alias_config_path=args.alias)
    builder.run(ydate_dir=args.ydate_dir, out_path=args.out)
    print("処理完了。")

if __name__ == "__main__":
    main()