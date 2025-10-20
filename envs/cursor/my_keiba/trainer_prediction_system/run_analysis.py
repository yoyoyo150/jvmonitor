#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
調教師予想システム実行スクリプト
"""
import sys
import os
from pathlib import Path

# パス設定
sys.path.append(str(Path(__file__).parent / "src"))

from trainer_prediction_system import TrainerPredictionSystem

def main():
    """メイン実行"""
    print("=== 調教師予想システム実行 ===")
    
    try:
        # システム初期化
        system = TrainerPredictionSystem()
        
        # 分析実行
        results = system.run_full_analysis(
            target_dates=['20250927', '20250928'],
            min_place_rate=0.25
        )
        
        if results:
            print("\n=== 分析結果サマリー ===")
            print(f"調教師数: {len(results['trainer_stats'])}")
            print(f"候補数: {len(results['candidates'])}")
            print(f"JVMonitor連携: {'OK' if results['jvmonitor_alignment'] else 'NG'}")
            
            # 上位候補の表示
            if not results['candidates'].empty:
                print("\n=== 上位候補 ===")
                for _, row in results['candidates'].head(10).iterrows():
                    print(f"  {row['TrainerName']}: {row['Result']} (着順率: {row['PlaceRate']:.2f})")
        else:
            print("分析に失敗しました")
            
    except Exception as e:
        print(f"実行エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()




