# -*- coding: utf-8 -*-
import sqlite3
import sys
import io

# UTF-8エンコーディング設定
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def quick_check():
    """プラダリアの2023年データをクイックチェック"""
    try:
        conn = sqlite3.connect('ecore.db')
        cursor = conn.cursor()
        
        # プラダリアの2023年出馬数確認
        cursor.execute("""
            SELECT COUNT(*) FROM N_UMA_RACE 
            WHERE Bamei = 'プラダリア' AND Year = '2023'
        """)
        pradaria_2023 = cursor.fetchone()[0]
        print(f"プラダリアの2023年出馬数: {pradaria_2023} 件")
        
        if pradaria_2023 > 0:
            print("✅ プラダリアの2023年データが取得できました！")
            
            # 詳細データを表示
            cursor.execute("""
                SELECT 
                    MonthDay,
                    JyoCD,
                    RaceNum,
                    NyusenJyuni,
                    KakuteiJyuni,
                    KisyuRyakusyo,
                    Honsyokin,
                    Time
                FROM N_UMA_RACE
                WHERE Bamei = 'プラダリア' AND Year = '2023'
                ORDER BY MonthDay DESC
            """)
            races = cursor.fetchall()
            
            print("\nプラダリアの2023年成績:")
            for race in races:
                monthday, jyo_cd, race_num, nyusen, kakutei, kisyu, honsyokin, time = race
                date_str = f"{monthday[:2]}月{monthday[2:]}日"
                print(f"  {date_str} 場{jyo_cd} {race_num}R ({kakutei or nyusen}位)")
                print(f"    騎手: {kisyu}, 賞金: {honsyokin}円, タイム: {time}")
        else:
            print("❌ プラダリアの2023年データがまだ取得できていません")
            print("EveryDB2.3で再度データダウンロードが必要です")
        
        conn.close()
        
    except sqlite3.OperationalError as e:
        if "database is locked" in str(e):
            print("⚠️ データベースがロックされています")
            print("EveryDB2.3がまだ処理中です。しばらく待ってから再実行してください")
        else:
            print(f"❌ データベースエラー: {e}")
    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == "__main__":
    quick_check()


