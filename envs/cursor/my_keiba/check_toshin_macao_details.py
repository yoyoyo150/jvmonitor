import sqlite3
import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

conn = sqlite3.connect('ecore.db')
query = """
SELECT
    HorseName,
    NormalizedHorseName,
    JyoCD,
    RaceNum,
    Mark5,
    Mark6
FROM HORSE_MARKS
WHERE SourceFile = '20250928.xlsx' AND HorseName = 'トウシンマカオ';
"""
df = pd.read_sql_query(query, conn)

if not df.empty:
    print(df.to_string())
else:
    print('データが見つかりませんでした。')

conn.close()




