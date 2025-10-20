import sqlite3
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

# ヒューリスティック係数（初版・控えめ）
ALPHA0 = 3.0  # 事前の複勝的中 (相当)
BETA0 = 7.0   # 事前の複勝失敗 (相当)
WEIGHT_MARK5 = 0.6
WEIGHT_MARK6 = 0.4
OVERLAY_THRESHOLD = 1.12  # p_est * odds > 1.12 を候補
MIN_RACES_STABLE = 5


def to_float_safe(x: str | None) -> float | None:
    if x is None:
        return None
    s = str(x).strip()
    if s == "":
        return None
    # 2.1-3.4 のような範囲は下限を採用
    if "-" in s:
        try:
            return float(s.split("-")[0])
        except Exception:
            return None
    try:
        return float(s)
    except Exception:
        return None


def load_joined(conn: sqlite3.Connection, target_dates: list[str]) -> pd.DataFrame:
    placeholders = ",".join(["?"] * len(target_dates))
    # 最小限のJOIN：複雑な文字列処理を削除
    sql = f"""
    SELECT
        HM.SourceDate,
        HM.JyoCD,
        HM.RaceNum,
        HM.HorseName,
        HM.TRAINER_NAME AS TrainerName,
        HM.Mark5,
        HM.Mark6,
        HM.FUKUSHO_ODDS,
        HM.FUKUSHO_ODDS_LOWER,
        HM.TANSHO_ODDS,
        HM.TAN_ODDS,
        CASE
            WHEN NUL.KakuteiJyuni GLOB '[0-9]*' THEN CAST(NUL.KakuteiJyuni AS INTEGER)
            ELSE NULL
        END AS FinishOrder
    FROM HORSE_MARKS AS HM
    LEFT JOIN N_UMA_RACE AS NUL
        ON HM.SourceDate = (NUL.Year || NUL.MonthDay)
        AND HM.HorseName = NUL.Bamei
    WHERE HM.SourceDate IN ({placeholders})
    LIMIT 500
    """
    print("SQLクエリ実行開始 (load_joined)...")
    df = pd.read_sql_query(sql, conn, params=target_dates)
    print("SQLクエリ実行完了 (load_joined).")
    return df


def compute_stable_strength(df_all: pd.DataFrame) -> pd.DataFrame:
    df = df_all.copy()
    df['Mark5_Num'] = pd.to_numeric(df['Mark5'], errors='coerce')
    df['Mark6_Num'] = pd.to_numeric(df['Mark6'], errors='coerce')
    df.dropna(subset=['TrainerName', 'Mark5_Num', 'Mark6_Num'], inplace=True)

    df['IsPlace'] = (df['FinishOrder'].apply(lambda x: int(x) if str(x).isdigit() else None)).apply(
        lambda x: True if (x is not None and x <= 3) else False
    )

    grouped = df.groupby('TrainerName').agg(
        AvgMark5=('Mark5_Num', 'mean'),
        AvgMark6=('Mark6_Num', 'mean'),
        PlaceWins=('IsPlace', 'sum'),
        TotalRaces=('TrainerName', 'count')
    ).reset_index()

    grouped['PlaceRate_shrunk'] = ((grouped['PlaceWins'] + ALPHA0) / (grouped['TotalRaces'] + ALPHA0 + BETA0))
    grouped = grouped[grouped['TotalRaces'] >= MIN_RACES_STABLE]

    # Markは小さいほど良い → 反転してスコア化（0〜1規模に粗正規化）
    for col in ['AvgMark5', 'AvgMark6']:
        maxv = grouped[col].max()
        minv = grouped[col].min()
        if pd.notna(maxv) and pd.notna(minv) and maxv > minv:
            grouped[col + '_score'] = 1.0 - (grouped[col] - minv) / (maxv - minv)
        else:
            grouped[col + '_score'] = 0.5

    grouped['StableScore'] = (
        WEIGHT_MARK5 * grouped['AvgMark5_score'] + WEIGHT_MARK6 * grouped['AvgMark6_score']
    )
    # 厩舎の期待複勝率（収縮）
    grouped['StableP'] = grouped['PlaceRate_shrunk']

    return grouped[['TrainerName', 'StableScore', 'StableP', 'TotalRaces', 'AvgMark5', 'AvgMark6']]


def create_html_report(candidates: pd.DataFrame, out_dir: Path, output_base_name: str) -> None:
    """HTMLレポートを生成"""
    if candidates.empty:
        html_content = "<h2>購入候補なし</h2><p>該当する候補がありません。</p>"
    else:
        # データを整形
        df_show = candidates.copy()
        df_show['SourceDate'] = df_show['SourceDate'].apply(lambda x: f"{x[:4]}/{x[4:6]}/{x[6:8]}")
        df_show['RaceInfo'] = df_show['JyoCD'] + '-' + df_show['RaceNum']
        
        # 期待値で色分け
        def get_color_class(ev):
            if ev > 1.5:
                return "bg-success"
            elif ev > 1.2:
                return "bg-warning"
            else:
                return "bg-info"
        
        df_show['ColorClass'] = df_show['expected_value'].apply(get_color_class)
        
        # HTMLテーブル生成
        html_rows = []
        for _, row in df_show.iterrows():
            html_rows.append(f"""
            <tr class="{row['ColorClass']}">
                <td>{row['SourceDate']}</td>
                <td>{row['RaceInfo']}</td>
                <td>{row['HorseName']}</td>
                <td>{row['TrainerName']}</td>
                <td>{row['Mark5_Num']:.1f}</td>
                <td>{row['Mark6_Num']:.1f}</td>
                <td>{row['StableP']:.3f}</td>
                <td>{row['odds_fuku']:.2f}</td>
                <td>{row['p_est']:.3f}</td>
                <td>{row['expected_value']:.3f}</td>
            </tr>
            """)
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>購入候補 2025/09/27-28</title>
            <style>
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .bg-success {{ background-color: #d4edda; }}
                .bg-warning {{ background-color: #fff3cd; }}
                .bg-info {{ background-color: #d1ecf1; }}
            </style>
        </head>
        <body>
            <h2>購入候補（複勝・オーバーレイ判定）2025/09/27-28</h2>
            <p>期待値 > {OVERLAY_THRESHOLD} の候補を表示</p>
            <table>
                <tr>
                    <th>日付</th><th>レース</th><th>馬名</th><th>調教師</th>
                    <th>Mark5</th><th>Mark6</th><th>厩舎複勝率</th>
                    <th>複勝オッズ</th><th>推定確率</th><th>期待値</th>
                </tr>
                {''.join(html_rows)}
            </table>
        </body>
        </html>
        """
    
    with open(out_dir / f'{output_base_name}.html', 'w', encoding='utf-8') as f:
        f.write(html_content)


def create_visualizations(candidates: pd.DataFrame, out_dir: Path, output_base_name: str) -> None:
    """グラフを生成"""
    if candidates.empty:
        print("候補なしのためグラフをスキップ")
        return
    
    # 日本語フォント設定（Windows環境に適応）
    plt.rcParams['font.family'] = ['DejaVu Sans', 'Yu Gothic', 'Meiryo', 'sans-serif']
    
    # 1. 期待値の棒グラフ（レース単位）
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # レースごとの最大期待値
    race_ev = candidates.groupby(['SourceDate', 'JyoCD', 'RaceNum'])['expected_value'].max().reset_index()
    race_ev['RaceLabel'] = race_ev['JyoCD'] + '-' + race_ev['RaceNum']
    
    bars = ax1.bar(range(len(race_ev)), race_ev['expected_value'])
    ax1.set_xlabel('レース')
    ax1.set_ylabel('最大期待値')
    ax1.set_title('レース別最大期待値')
    ax1.set_xticks(range(len(race_ev)))
    ax1.set_xticklabels(race_ev['RaceLabel'], rotation=45)
    
    # 閾値ライン
    ax1.axhline(y=OVERLAY_THRESHOLD, color='r', linestyle='--', label=f'閾値 {OVERLAY_THRESHOLD}')
    ax1.legend()
    
    # 2. 確率 vs オッズの散布図
    scatter = ax2.scatter(candidates['odds_fuku'], candidates['p_est'], 
                         c=candidates['expected_value'], cmap='RdYlGn', alpha=0.7)
    ax2.set_xlabel('複勝オッズ')
    ax2.set_ylabel('推定確率')
    ax2.set_title('確率 vs オッズ（色：期待値）')
    
    # 等価線
    odds_range = np.linspace(candidates['odds_fuku'].min(), candidates['odds_fuku'].max(), 100)
    ax2.plot(odds_range, OVERLAY_THRESHOLD / odds_range, 'r--', label=f'閾値 {OVERLAY_THRESHOLD}')
    ax2.legend()
    
    plt.colorbar(scatter, ax=ax2, label='期待値')
    plt.tight_layout()
    plt.savefig(out_dir / f'{output_base_name}_charts.png', dpi=150, bbox_inches='tight')
    plt.close()


def estimate_prob(mark5: float | None, mark6: float | None, stable_p: float | None) -> float | None:
    # 単純なヒューリスティック: mark値が低いほど上乗せ、厩舎複勝率で下支え
    if mark5 is None or mark6 is None or stable_p is None:
        return None
    # markの優秀度（小さい＝良い）を反転（仮に1〜10程度のレンジを想定して線形）
    m5 = max(0.0, min(1.0, (10.0 - mark5) / 9.0))
    m6 = max(0.0, min(1.0, (10.0 - mark6) / 9.0))
    m_score = WEIGHT_MARK5 * m5 + WEIGHT_MARK6 * m6
    # 安全側に 0.5*(stable_p) + 0.5*(m_score) を採用
    return 0.5 * stable_p + 0.5 * m_score


def main() -> int:
    print("スクリプト開始: recommend_candidates.py")
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

    db_path = Path("ecore.db")
    if not db_path.exists():
        print(f"エラー: DBが見つかりません: {db_path}", file=sys.stderr)
        return 1

    target_dates = [
        "20250913", "20250914", "20250915", "20250916", "20250917", 
        "20250918", "20250919", "20250920", "20250921", "20250922", 
        "20250923", "20250924", "20250925", "20250926", "20250927"
    ]

    conn = sqlite3.connect(db_path)
    try:
        print("データベース接続成功、処理開始...")
        # ここで先に作っておく
        out_dir = Path('outputs')
        out_dir.mkdir(exist_ok=True)
        print(f"出力ディレクトリ作成: {out_dir}")

        # 出力ファイル名を動的に生成
        start_date_str = target_dates[0]
        end_date_str = target_dates[-1]
        output_base_name = f"reco_{start_date_str}_{end_date_str}"

        print("df_all (load_joined) の読み込み開始...")
        # 全期間で厩舎の安定度を評価
        df_all = load_joined(conn, target_dates)
        print(f"df_all 読み込み完了。行数: {len(df_all)}")

        print("df_all_full (HORSE_MARKS) の読み込み開始...")
        df_all_full = pd.read_sql_query("SELECT * FROM HORSE_MARKS", conn)
        print(f"df_all_full 読み込み完了。行数: {len(df_all_full)}")

        df_all_full['SourceDate'] = df_all_full['SourceDate'].astype(str)
        # 過去分もJOINしてFinishOrderを得るため再利用
        df_past = load_joined(conn, sorted(df_all_full['SourceDate'].unique().tolist()))

        stable_tbl = compute_stable_strength(df_past)

        # 対象日のデータに厩舎評価をJOIN
        df_all['Mark5_Num'] = pd.to_numeric(df_all['Mark5'], errors='coerce')
        df_all['Mark6_Num'] = pd.to_numeric(df_all['Mark6'], errors='coerce')
        df_all = df_all.merge(stable_tbl, on='TrainerName', how='left')

        # オッズ取得（複勝の下限優先 → 単勝の参考）
        df_all['odds_fuku'] = df_all['FUKUSHO_ODDS_LOWER'].apply(to_float_safe)
        df_all['odds_fuku'] = df_all['odds_fuku'].fillna(df_all['FUKUSHO_ODDS'].apply(to_float_safe))
        df_all['odds_tan'] = df_all['TAN_ODDS'].apply(to_float_safe)
        df_all['odds_tan'] = df_all['odds_tan'].fillna(df_all['TANSHO_ODDS'].apply(to_float_safe))

        # 確率推定
        df_all['p_est'] = df_all.apply(
            lambda r: estimate_prob(r['Mark5_Num'], r['Mark6_Num'], r['StableP']), axis=1
        )

        # 期待値判定（複勝を基本）
        df_all['expected_value'] = df_all['p_est'] * df_all['odds_fuku']

        # 候補抽出
        candidates = df_all[(df_all['p_est'].notna()) & (df_all['odds_fuku'].notna())]
        candidates = candidates[candidates['expected_value'] > OVERLAY_THRESHOLD]
        candidates = candidates.sort_values(['SourceDate', 'JyoCD', 'RaceNum', 'expected_value'], ascending=[True, True, True, False])

        # 表示
        if candidates.empty:
            print("該当候補がありません（閾値を下げると出ます）。")
        else:
            cols_show = ['SourceDate', 'JyoCD', 'RaceNum', 'HorseName', 'TrainerName',
                         'Mark5_Num', 'Mark6_Num', 'StableP', 'odds_fuku', 'p_est', 'expected_value']
            print("\n--- 購入候補（複勝・オーバーレイ判定） 2025/09/27-28 ---")
            print(candidates[cols_show].to_string(index=False, formatters={
                'StableP': '{:.3f}'.format,
                'odds_fuku': '{:.2f}'.format,
                'p_est': '{:.3f}'.format,
                'expected_value': '{:.3f}'.format,
                'Mark5_Num': '{:.1f}'.format,
                'Mark6_Num': '{:.1f}'.format,
            }))

            # CSV保存
            out_csv = out_dir / f'{output_base_name}.csv'
            candidates.to_csv(out_csv, index=False)
            print(f"\nCSV保存: {out_csv}")

        # 可視化
        create_html_report(candidates, out_dir, output_base_name)
        print(f"HTML保存: {out_dir / f'{output_base_name}.html'}")

        create_visualizations(candidates, out_dir, output_base_name)
        print(f"グラフ保存: {out_dir / f'{output_base_name}_charts.png'}")

        return 0

    except sqlite3.Error as e:
        print(f"データベースエラー: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"エラー: {e}", file=sys.stderr)
        return 1
    finally:
        conn.close()

if __name__ == "__main__":
    raise SystemExit(main())
