import pandas as pd
import numpy as np
import sqlite3
import json
import os
import re
import unicodedata
from datetime import datetime
import sys

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

class EnhancedFeatureBuilder:
    """拡張特徴量ビルダー - alias_config.json対応"""
    
    def __init__(self, db_path="trainer_prediction_system/excel_data.db", config_path="JVLinkToSQLiteArtifact/tools/alias_config.json"):
        self.db_path = db_path
        self.config_path = config_path
        self.conn = None
        self.config = None
        self.connect()
        self.load_config()
    
    def connect(self):
        """データベース接続"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            print("データベース接続成功")
        except Exception as e:
            print(f"データベース接続エラー: {e}")
            return False
        return True
    
    def load_config(self):
        """alias_config.json読み込み"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            print("alias_config.json読み込み成功")
        except Exception as e:
            print(f"設定ファイル読み込みエラー: {e}")
            return False
        return True
    
    def zen2han(self, s):
        """全角→半角変換"""
        return unicodedata.normalize("NFKC", str(s)) if s is not None else s
    
    def parse_track_and_race(self, b_value, track_map):
        """レース名から場コードとレース番号を抽出"""
        s = self.zen2han(b_value).replace("レース", "").replace("R", "").strip()
        # 例: "新1", "中10"
        m = re.match(r"([^\d]+)\s*(\d+)$", s)
        if not m:
            return None, None
        track_raw, r = m.group(1), m.group(2)
        track_cd = track_map.get(track_raw, track_map.get(track_raw[:1], None))
        return track_cd, int(r)
    
    def label_to_ord(self, x, mapping={"堅い": 1, "注意": 2, "チェック": 3, "注目": 4}):
        """ラベル→序数変換"""
        s = self.zen2han(x)
        return mapping.get(s, None)
    
    def clean_num(self, x):
        """数値クリーンアップ"""
        s = self.zen2han(x)
        s = re.sub(r"[^\d.-]", "", s)
        return float(s) if s not in ("", "-", ".") else None
    
    def parse_ai_odds(self, ai):
        """AI列のオッズ変換（29 → 2.9）"""
        v = self.clean_num(ai)
        return None if v is None else (v / 10.0)
    
    def to_gap_num(self, x):
        """R印の数値化"""
        if x is None:
            return None
        s = str(x).strip()
        map_lab = {"堅い": 1, "注意": 2, "チェック": 3, "注目": 4}
        if s in map_lab:
            return map_lab[s]
        try:
            return float(s)
        except:
            return None
    
    def calc_race_roughness(self, r_zi_gap, r_zm_gap, takeuchi_prev23):
        """レース荒れ度計算"""
        # 値があれば z-normalize 前提
        # 直感：ZI/ZMの差が小さい→堅い、大きい→荒れ
        # 竹内：前走2,3着頭数が多いほど"堅い"寄りとする逆符号
        return (+ self.zscore(r_zi_gap) + self.zscore(r_zm_gap) - self.zscore(takeuchi_prev23))
    
    def zscore(self, series):
        """Zスコア計算"""
        if series is None or len(series) == 0:
            return 0
        mean_val = np.mean(series)
        std_val = np.std(series)
        if std_val == 0:
            return 0
        return (series - mean_val) / std_val
    
    def build_enhanced_features(self):
        """拡張特徴量の構築"""
        print("=== 拡張特徴量構築 ===")
        
        try:
            # 1) レースID生成
            self.build_race_id()
            
            # 2) 距離正規化
            self.normalize_distance()
            
            # 3) R印正規化
            self.normalize_r_marks()
            
            # 4) 馬印正規化
            self.normalize_horse_marks()
            
            # 5) 人気・オッズ正規化
            self.normalize_popularity()
            
            # 6) 派生特徴生成
            self.build_derived_features()
            
            # 7) レース荒れ度計算
            self.calculate_race_roughness()
            
            print("✅ 拡張特徴量構築完了")
            return True
            
        except Exception as e:
            print(f"拡張特徴量構築エラー: {e}")
            return False
    
    def build_race_id(self):
        """レースID生成"""
        print("=== レースID生成 ===")
        
        try:
            # A列が空なら、B列から生成
            query = """
            UPDATE SE_FE 
            SET race_id = CASE
                WHEN A IS NULL OR A = '' THEN 
                    CAST(SourceDate AS TEXT) || 
                    CASE 
                        WHEN B LIKE '札%' THEN '01'
                        WHEN B LIKE '函%' THEN '02'
                        WHEN B LIKE '福%' THEN '03'
                        WHEN B LIKE '新%' THEN '04'
                        WHEN B LIKE '東%' THEN '05'
                        WHEN B LIKE '中%' THEN '06'
                        WHEN B LIKE '名%' THEN '07'
                        WHEN B LIKE '京%' THEN '08'
                        WHEN B LIKE '阪%' THEN '09'
                        WHEN B LIKE '小%' THEN '10'
                        ELSE '00'
                    END ||
                    LPAD(CAST(REGEXP_REPLACE(B, '[^0-9]', '') AS INTEGER), 2, '0')
                ELSE A
            END
            """
            cursor = self.conn.cursor()
            cursor.execute(query)
            self.conn.commit()
            print("レースID生成完了")
            
        except Exception as e:
            print(f"レースID生成エラー: {e}")
    
    def normalize_distance(self):
        """距離正規化"""
        print("=== 距離正規化 ===")
        
        try:
            # D列の距離を数値化
            query = """
            UPDATE SE_FE 
            SET distance_num = CASE
                WHEN D IS NULL OR D = '' THEN NULL
                ELSE CAST(REGEXP_REPLACE(D, '[^0-9]', '') AS INTEGER)
            END
            """
            cursor = self.conn.cursor()
            cursor.execute(query)
            self.conn.commit()
            print("距離正規化完了")
            
        except Exception as e:
            print(f"距離正規化エラー: {e}")
    
    def normalize_r_marks(self):
        """R印正規化"""
        print("=== R印正規化 ===")
        
        try:
            # F列（R印1）正規化
            query_f = """
            UPDATE SE_FE 
            SET r_zi_gap_num = CASE
                WHEN F IS NULL OR F = '' THEN NULL
                WHEN F = '堅い' THEN 1
                WHEN F = '注意' THEN 2
                WHEN F = 'チェック' THEN 3
                WHEN F = '注目' THEN 4
                ELSE CAST(F AS REAL)
            END
            """
            cursor = self.conn.cursor()
            cursor.execute(query_f)
            
            # G列（R印2）正規化
            query_g = """
            UPDATE SE_FE 
            SET r_zm_gap_num = CASE
                WHEN G IS NULL OR G = '' THEN NULL
                WHEN G = '堅い' THEN 1
                WHEN G = '注意' THEN 2
                WHEN G = 'チェック' THEN 3
                WHEN G = '注目' THEN 4
                ELSE CAST(G AS REAL)
            END
            """
            cursor.execute(query_g)
            
            # H列（竹内理論）正規化
            query_h = """
            UPDATE SE_FE 
            SET takeuchi_prev23_cnt = CASE
                WHEN H IS NULL OR H = '' THEN NULL
                ELSE CAST(H AS INTEGER)
            END
            """
            cursor.execute(query_h)
            
            self.conn.commit()
            print("R印正規化完了")
            
        except Exception as e:
            print(f"R印正規化エラー: {e}")
    
    def normalize_horse_marks(self):
        """馬印正規化"""
        print("=== 馬印正規化 ===")
        
        try:
            # 馬印1（J列）正規化
            query_j = """
            UPDATE SE_FE 
            SET 
                super_fav_flag = CASE WHEN J LIKE '%△%' OR J LIKE '%▲%' THEN 1 ELSE 0 END,
                late_ZI_candidate = CASE WHEN J LIKE '%♢%' THEN 1 ELSE 0 END,
                no_bet_flag = CASE WHEN J LIKE '%消%' THEN 1 ELSE 0 END,
                low_confidence_flag = CASE WHEN J LIKE '%？%' OR J LIKE '%?%' THEN 1 ELSE 0 END,
                smart_tag_A = CASE WHEN J LIKE '%A%' THEN 1 ELSE 0 END,
                smart_tag_B = CASE WHEN J LIKE '%B%' THEN 1 ELSE 0 END,
                smart_tag_C = CASE WHEN J LIKE '%C%' THEN 1 ELSE 0 END
            """
            cursor = self.conn.cursor()
            cursor.execute(query_j)
            
            # 馬印2（K列）正規化
            query_k = """
            UPDATE SE_FE 
            SET speed_rank = CASE
                WHEN K IS NULL OR K = '' THEN NULL
                ELSE CAST(K AS INTEGER)
            END
            """
            cursor.execute(query_k)
            
            # 馬印3（L列）正規化
            query_l = """
            UPDATE SE_FE 
            SET spirit_rank = CASE
                WHEN L IS NULL OR L = '' THEN NULL
                WHEN L = 'A' THEN 1
                WHEN L = 'B' THEN 2
                WHEN L = 'C' THEN 3
                WHEN L = 'D' THEN 4
                WHEN L = 'E' THEN 5
                WHEN L = 'F' THEN 6
                WHEN L = 'G' THEN 7
                WHEN L = 'H' THEN 8
                ELSE NULL
            END
            """
            cursor.execute(query_l)
            
            # 馬印5/6（N/O列）正規化
            query_n = """
            UPDATE SE_FE 
            SET 
                mark5_score_raw = CASE
                    WHEN N IS NULL OR N = '' THEN NULL
                    WHEN N = '?' OR N = '？' THEN NULL
                    ELSE CAST(N AS REAL)
                END,
                mark5_low_conf_flag = CASE
                    WHEN N = '?' OR N = '？' THEN 1
                    ELSE 0
                END
            """
            cursor.execute(query_n)
            
            query_o = """
            UPDATE SE_FE 
            SET 
                mark6_score_raw = CASE
                    WHEN O IS NULL OR O = '' THEN NULL
                    WHEN O = '?' OR O = '？' THEN NULL
                    ELSE CAST(O AS REAL)
                END,
                mark6_low_conf_flag = CASE
                    WHEN O = '?' OR O = '？' THEN 1
                    ELSE 0
                END
            """
            cursor.execute(query_o)
            
            # 馬印7（P列）正規化
            query_p = """
            UPDATE SE_FE 
            SET zm_score = CASE
                WHEN P IS NULL OR P = '' THEN NULL
                ELSE CAST(P AS REAL)
            END
            """
            cursor.execute(query_p)
            
            self.conn.commit()
            print("馬印正規化完了")
            
        except Exception as e:
            print(f"馬印正規化エラー: {e}")
    
    def normalize_popularity(self):
        """人気・オッズ正規化"""
        print("=== 人気・オッズ正規化 ===")
        
        try:
            # 前人気（AH列）正規化
            query_ah = """
            UPDATE SE_FE 
            SET prev_ninki_rank = CASE
                WHEN AH IS NULL OR AH = '' THEN NULL
                ELSE CAST(AH AS INTEGER)
            END
            """
            cursor = self.conn.cursor()
            cursor.execute(query_ah)
            
            # ZM予想単勝（AI列）正規化
            query_ai = """
            UPDATE SE_FE 
            SET zm_odds_pred = CASE
                WHEN AI IS NULL OR AI = '' THEN NULL
                ELSE CAST(AI AS REAL) / 10.0
            END
            """
            cursor.execute(query_ai)
            
            self.conn.commit()
            print("人気・オッズ正規化完了")
            
        except Exception as e:
            print(f"人気・オッズ正規化エラー: {e}")
    
    def build_derived_features(self):
        """派生特徴生成"""
        print("=== 派生特徴生成 ===")
        
        try:
            # 前脚質（Y列）正規化
            query_y = """
            UPDATE SE_FE 
            SET 
                style_front = CASE WHEN Y LIKE '%前%' THEN 1 ELSE 0 END,
                style_mid = CASE WHEN Y LIKE '%中%' THEN 1 ELSE 0 END,
                style_back = CASE WHEN Y LIKE '%後%' THEN 1 ELSE 0 END
            """
            cursor = self.conn.cursor()
            cursor.execute(query_y)
            
            # 加速・オリジナルスコア（AK/AN列）正規化
            query_ak = """
            UPDATE SE_FE 
            SET accel_score = CASE
                WHEN AK IS NULL OR AK = '' THEN NULL
                ELSE CAST(AK AS REAL)
            END
            """
            cursor.execute(query_ak)
            
            query_an = """
            UPDATE SE_FE 
            SET original_score = CASE
                WHEN AN IS NULL OR AN = '' THEN NULL
                ELSE CAST(AN AS REAL)
            END
            """
            cursor.execute(query_an)
            
            self.conn.commit()
            print("派生特徴生成完了")
            
        except Exception as e:
            print(f"派生特徴生成エラー: {e}")
    
    def calculate_race_roughness(self):
        """レース荒れ度計算"""
        print("=== レース荒れ度計算 ===")
        
        try:
            # レース別に荒れ度を計算
            query = """
            WITH race_stats AS (
                SELECT 
                    race_id,
                    AVG(r_zi_gap_num) as avg_zi_gap,
                    AVG(r_zm_gap_num) as avg_zm_gap,
                    AVG(takeuchi_prev23_cnt) as avg_takeuchi
                FROM SE_FE
                WHERE race_id IS NOT NULL
                GROUP BY race_id
            ),
            race_zscore AS (
                SELECT 
                    race_id,
                    (r_zi_gap_num - avg_zi_gap) / NULLIF(STDDEV(r_zi_gap_num), 0) as zi_zscore,
                    (r_zm_gap_num - avg_zm_gap) / NULLIF(STDDEV(r_zm_gap_num), 0) as zm_zscore,
                    (takeuchi_prev23_cnt - avg_takeuchi) / NULLIF(STDDEV(takeuchi_prev23_cnt), 0) as takeuchi_zscore
                FROM SE_FE se
                JOIN race_stats rs ON se.race_id = rs.race_id
            )
            UPDATE SE_FE 
            SET race_roughness_idx = (
                SELECT zi_zscore + zm_zscore - takeuchi_zscore
                FROM race_zscore rz
                WHERE rz.race_id = SE_FE.race_id
            )
            """
            cursor = self.conn.cursor()
            cursor.execute(query)
            self.conn.commit()
            print("レース荒れ度計算完了")
            
        except Exception as e:
            print(f"レース荒れ度計算エラー: {e}")
    
    def run_enhanced_feature_building(self):
        """拡張特徴量構築実行"""
        print("=== 拡張特徴量構築実行 ===")
        
        try:
            # 1) 拡張特徴量構築
            if not self.build_enhanced_features():
                return False
            
            print("✅ 拡張特徴量構築完了")
            return True
            
        except Exception as e:
            print(f"拡張特徴量構築実行エラー: {e}")
            return False

def main():
    builder = EnhancedFeatureBuilder()
    success = builder.run_enhanced_feature_building()
    
    if success:
        print("\n✅ 拡張特徴量構築成功")
    else:
        print("\n❌ 拡張特徴量構築失敗")

if __name__ == "__main__":
    main()




