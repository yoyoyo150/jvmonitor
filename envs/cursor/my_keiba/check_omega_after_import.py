import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def check_omega_after_import():
    conn = sqlite3.connect('ecore.db')
    cursor = conn.cursor()
    
    # オメガタキシードの確認
    cursor.execute("""
        SELECT HorseName, Mark1, Mark2, Mark3, ZI_INDEX, ZM_VALUE 
        FROM HORSE_MARKS 
        WHERE SourceDate = '20250503' AND HorseName = 'オメガタキシード'
    """)
    
    result = cursor.fetchone()
    if result:
        horse_name, m1, m2, m3, zi, zm = result
        print(f"✅ オメガタキシードの2025年5月3日のデータ:")
        print(f"  馬名: {horse_name}")
        print(f"  馬印1: {m1}")
        print(f"  馬印2: {m2}")
        print(f"  馬印3: {m3}")
        print(f"  ZI指数: {zi}")
        print(f"  ZM値: {zm}")
    else:
        print("❌ オメガタキシードの2025年5月3日のデータが見つかりません")
    
    # イデアイゴッソウの確認
    cursor.execute("""
        SELECT HorseName, Mark1, Mark2, Mark3, ZI_INDEX, ZM_VALUE 
        FROM HORSE_MARKS 
        WHERE SourceDate = '20250503' AND HorseName = 'イデアイゴッソウ'
    """)
    
    result = cursor.fetchone()
    if result:
        horse_name, m1, m2, m3, zi, zm = result
        print(f"✅ イデアイゴッソウの2025年5月3日のデータ:")
        print(f"  馬名: {horse_name}")
        print(f"  馬印1: {m1}")
        print(f"  馬印2: {m2}")
        print(f"  馬印3: {m3}")
        print(f"  ZI指数: {zi}")
        print(f"  ZM値: {zm}")
    else:
        print("❌ イデアイゴッソウの2025年5月3日のデータが見つかりません")
    
    # 2025年5月3日の総レコード数
    cursor.execute("SELECT COUNT(*) FROM HORSE_MARKS WHERE SourceDate = '20250503'")
    count = cursor.fetchone()[0]
    print(f"\n2025年5月3日の総レコード数: {count} 件")
    
    conn.close()

if __name__ == '__main__':
    check_omega_after_import()

