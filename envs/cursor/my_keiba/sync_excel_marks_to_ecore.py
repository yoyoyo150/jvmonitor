#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
excel_data.db に取り込んだ馬印データを ecore.db の HORSE_MARKS テーブルへ同期するスクリプト
"""

import sqlite3
from pathlib import Path
from typing import List, Optional


def find_project_root() -> Path:
    """ecore.db と excel_data.db が揃っているディレクトリを探索する"""
    current = Path.cwd()
    while current != current.parent:
        if (current / "ecore.db").exists() and (current / "excel_data.db").exists():
            return current
        current = current.parent
    return Path.cwd()


def fetch_columns(conn: sqlite3.Connection, table_name: str) -> List[str]:
    """テーブルのカラム一覧を取得"""
    conn.row_factory = sqlite3.Row
    rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    return [row["name"] for row in rows]


def main() -> int:
    project_root = find_project_root()
    excel_db = project_root / "excel_data.db"
    ecore_db = project_root / "ecore.db"

    if not excel_db.exists():
        print(f"[ERROR] excel_data.db not found: {excel_db}")
        return 1

    if not ecore_db.exists():
        print(f"[ERROR] ecore.db not found: {ecore_db}")
        return 1

    src_conn: Optional[sqlite3.Connection] = None
    dest_conn: Optional[sqlite3.Connection] = None

    try:
        src_conn = sqlite3.connect(excel_db)
        dest_conn = sqlite3.connect(ecore_db)
        src_conn.row_factory = sqlite3.Row

        src_columns = fetch_columns(src_conn, "HORSE_MARKS")
        dest_columns = fetch_columns(dest_conn, "HORSE_MARKS")
        common_columns = [c for c in src_columns if c in dest_columns]

        if not common_columns:
            print("[ERROR] No shared columns between source and destination HORSE_MARKS tables.")
            return 1

        column_list = ", ".join(common_columns)
        placeholders = ", ".join("?" for _ in common_columns)

        rows = src_conn.execute(f"SELECT {column_list} FROM HORSE_MARKS").fetchall()
        if not rows:
            print("[WARN] No rows found in source HORSE_MARKS table.")
            return 0

        payload = [[row[col] for col in common_columns] for row in rows]

        dest_conn.execute("BEGIN")
        dest_conn.executemany(
            f"INSERT OR REPLACE INTO HORSE_MARKS ({column_list}) VALUES ({placeholders})",
            payload,
        )
        dest_conn.commit()

        print(f"[OK] HORSE_MARKS synchronized: {len(payload):,} rows.")
        return 0

    except Exception as exc:  # pylint: disable=broad-except
        if dest_conn is not None:
            dest_conn.rollback()
        print(f"[ERROR] Synchronization failed: {exc}")
        return 1

    finally:
        if src_conn is not None:
            src_conn.close()
        if dest_conn is not None:
            dest_conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
