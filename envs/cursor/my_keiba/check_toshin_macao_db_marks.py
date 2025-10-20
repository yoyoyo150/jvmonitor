import sqlite3
import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

conn = sqlite3.connect('ecore.db')
query = """
SELECT
    SourceDate,
    NormalizedHorseName,
    JyoCD,
    RaceNum,
    Mark5,
    Mark6
FROM HORSE_MARKS
WHERE SourceDate = '20250928'
  AND NormalizedHorseName = 'トウシンマカオ'
  AND JyoCD = '06'
  AND RaceNum = '11'
"""
df = pd.read_sql_query(query, conn)

if not df.empty:
    print(df.to_string())
else:
    print('データが見つかりませんでした。')

conn.close()




