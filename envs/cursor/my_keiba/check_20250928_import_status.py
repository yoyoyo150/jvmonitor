import sqlite3
import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

conn = sqlite3.connect('ecore.db')
query = """
SELECT
    SourceFile,
    ImportedAt,
    COUNT(*) as record_count
FROM HORSE_MARKS
WHERE SourceFile = '20250928.xlsx'
GROUP BY SourceFile, ImportedAt
ORDER BY ImportedAt DESC;
"""
df = pd.read_sql_query(query, conn)

if not df.empty:
    print(df.to_string())
else:
    print('データが見つかりませんでした。')

conn.close()




