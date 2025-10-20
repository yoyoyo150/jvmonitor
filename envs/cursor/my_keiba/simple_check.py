import sqlite3

conn = sqlite3.connect('excel_data.db')
cursor = conn.cursor()

# 最新日のレコード数
cursor.execute('SELECT COUNT(*) FROM HORSE_MARKS WHERE SourceDate = "20251005"')
count = cursor.fetchone()[0]
print(f'20251005のレコード数: {count:,} 件')

# 馬印データの確認
cursor.execute('''
    SELECT 
        COUNT(*) as total,
        COUNT(CASE WHEN Mark1 IS NOT NULL AND Mark1 != '' THEN 1 END) as mark1_count,
        COUNT(CASE WHEN Mark2 IS NOT NULL AND Mark2 != '' THEN 1 END) as mark2_count,
        COUNT(CASE WHEN Mark3 IS NOT NULL AND Mark3 != '' THEN 1 END) as mark3_count
    FROM HORSE_MARKS
    WHERE SourceDate = "20251005"
''')

stats = cursor.fetchone()
print(f'総レコード数: {stats[0]:,} 件')
print(f'馬印1: {stats[1]:,} 件 ({stats[1]/stats[0]*100:.1f}%)')
print(f'馬印2: {stats[2]:,} 件 ({stats[2]/stats[0]*100:.1f}%)')
print(f'馬印3: {stats[3]:,} 件 ({stats[3]/stats[0]*100:.1f}%)')

# サンプルデータ
cursor.execute('''
    SELECT HorseName, Mark1, Mark2, Mark3, ZI_INDEX, ZM_VALUE
    FROM HORSE_MARKS 
    WHERE SourceDate = "20251005" 
    LIMIT 3
''')

samples = cursor.fetchall()
print('\nサンプルデータ:')
for sample in samples:
    print(f'  {sample[0]}: 馬印1={sample[1]}, 馬印2={sample[2]}, 馬印3={sample[3]}, ZI={sample[4]}, ZM={sample[5]}')

conn.close()


