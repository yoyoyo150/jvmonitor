#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
証拠パケット出力ツール
毎回の検証で証拠（スキーマ、診断結果、個別レース）を自動出力
"""
import sqlite3
import json
import csv
from pathlib import Path
from datetime import datetime
import sys

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def run(db_path: str, outdir: str, race_id: str | None = None):
    """証拠パケット生成"""
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    meta = {"db_path": db_path, "generated_at": ts, "race_id": race_id}

    con = sqlite3.connect(db_path)
    cur = con.cursor()

    # 1) スキーマの証拠（列名）
    schema = {}
    for tname, in cur.execute("SELECT name FROM sqlite_master WHERE type='table'"):
        cols = [r[1] for r in cur.execute(f"PRAGMA table_info('{tname}')")]
        schema[tname] = cols
    (out / f"schema_{ts}.json").write_text(
        json.dumps(schema, ensure_ascii=False, indent=2), 
        encoding="utf-8"
    )

    # 2) 9月診断の要約
    diag_sql_path = Path("sql/diag_september.sql")
    if diag_sql_path.exists():
        q1 = diag_sql_path.read_text(encoding="utf-8").split(";")
    else:
        q1 = []
        print(f"[warning] sql/diag_september.sql not found")
    
    res = []
    for qi in q1:
        sql = qi.strip()
        if not sql: 
            continue
        try:
            rows = list(cur.execute(sql))
            cols = [d[0] for d in cur.description] if cur.description else []
            res.append({"sql": sql, "columns": cols, "rows": rows})
        except Exception as e:
            res.append({"sql": sql, "error": repr(e)})

    (out / f"diag_{ts}.json").write_text(
        json.dumps(res, ensure_ascii=False, indent=2), 
        encoding="utf-8"
    )

    # 3) race_id 個別の証拠（任意）
    if race_id:
        rows = list(cur.execute("""
            SELECT v.race_id, v.horse_name, v.trainer_name, v.finish_pos, v.race_date
            FROM v_results_official v
            WHERE v.race_id = ?
            ORDER BY CAST(v.finish_pos AS INTEGER)
        """, (race_id,)))
        
        with open(out / f"race_{race_id}_{ts}.csv", "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["race_id", "horse_name", "trainer_name", "finish_pos", "race_date"])
            w.writerows(rows)

    con.close()
    (out / f"meta_{ts}.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), 
        encoding="utf-8"
    )
    print(f"[ok] evidence written to {out}")
    print(f"  - schema_{ts}.json")
    print(f"  - diag_{ts}.json")
    if race_id:
        print(f"  - race_{race_id}_{ts}.csv")
    print(f"  - meta_{ts}.json")

if __name__ == "__main__":
    # 使い方例
    run(
        db_path=r"ecore.db", 
        outdir=r"runs\evidence", 
        race_id="202509280611"
    )




