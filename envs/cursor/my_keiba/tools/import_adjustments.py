import sqlite3, sys, argparse, json, hashlib
from pathlib import Path
import pandas as pd
from datetime import datetime
import os

SCHEMA = {
    "required": ["horse_id"],
    "columns": {
        "horse_id": {"type": "str",  "regex": None},
        "form":     {"type": "float","min": -5, "max": 5},
        "train":    {"type": "float","min": -5, "max": 5},
        "note":     {"type": "str"}
    }
}

def file_hash(p: Path) -> str:
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(65536), b""): h.update(b)
    return h.hexdigest()[:12]

def validate_df(df: pd.DataFrame):
    # 必須列
    for col in SCHEMA["required"]:
        if col not in df.columns:
            raise ValueError(f"必須列がありません: {col}")
    errs=[]
    # 列ごとチェック
    for col, rule in SCHEMA["columns"].items():
        if col not in df.columns: 
            continue
        if rule.get("type")=="float":
            # 数値化できない値を検出
            bad = pd.to_numeric(df[col], errors="coerce").isna() & df[col].notna()
            if bad.any(): errs.append(f"{col}: 非数値 {bad.sum()}件")
            # 値域
            x = pd.to_numeric(df[col], errors="coerce")
            if "min" in rule and (x < rule["min"]).fillna(False).any():
                errs.append(f"{col}: 最小{rule["min"]}未満が存在")
            if "max" in rule and (x > rule["max"]).fillna(False).any():
                errs.append(f"{col}: 最大{rule["max"]}超が存在")
        # 文字列型は特に制約しないが空白列の警告だけ
        if rule.get("type")=="str":
            if df[col].dtype == object and df[col].map(lambda v: isinstance(v,str) and v.strip()=="" ).any():
                errs.append(f"{col}: 空文字が存在")
    if errs: 
        raise ValueError("スキーマ検証エラー: " + "; ".join(errs))

def main(db, xlsx, sheet="adjustments", dry_run=False, version_id=None):
    con = sqlite3.connect(db)
    con.execute("PRAGMA foreign_keys=ON")
    ts = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    version_id = version_id or ts.replace(":", "-") # Windowsのパスで使えない文字を置換
    outdir = Path(os.path.join("runs", "import_adjustments", version_id))
    outdir.mkdir(parents=True, exist_ok=True)

    # 1) 読み込み
    xlsx_path = Path(xlsx)
    if not xlsx_path.exists():
        raise FileNotFoundError(f"指定されたExcelファイルが見つかりません: {xlsx_path.resolve()}")
    df = pd.read_excel(xlsx_path, sheet_name=sheet).fillna({"form":0.0, "train":0.0})
    # 列名の安全化（余計な列は無視）
    keep = [c for c in df.columns if c in SCHEMA["columns"].keys()]
    df = df[keep]
    validate_df(df)

    # 2) 参照整合（未知のhorse_idを隔離）
    known = pd.read_sql_query("SELECT horse_id FROM v_known_horses", con)["horse_id"].unique().tolist()
    df["__known__"] = df["horse_id"].isin(known)
    bad = df[~df["__known__"]]
    ok  = df[df["__known__"]].drop(columns="__known__")

    # 3) 証拠保存（ドライランでも保存）
    meta = {
        "db_path": str(Path(db).resolve()),
        "xlsx_path": str(Path(xlsx).resolve()),
        "xlsx_sha": file_hash(Path(xlsx)),
        "version_id": version_id,
        "rows_total": len(df),
        "rows_ok": len(ok),
        "rows_unknown_horse": len(bad),
        "dry_run": bool(dry_run),
        "generated_at": ts
    }
    ok.to_csv(outdir/"ok_rows.csv", index=False, encoding="utf-8-sig")
    bad.to_csv(outdir/"unknown_horse_rows.csv", index=False, encoding="utf-8-sig")
    (outdir/"meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    if dry_run:
        print("[DRY-RUN] 取り込みは行いません。検証結果のみ保存しました。")
        return

    # 4) 反映（トランザクション）
    try:
        con.execute("BEGIN IMMEDIATE")
        con.execute("DELETE FROM stg_adjustments")
        ok.to_sql("stg_adjustments", con, if_exists="append", index=False)

        # 本番へ（新versionでUPSERT）
        con.execute("""
            INSERT INTO x_adjustments (version_id, horse_id, form, train, note, updated_at)
            SELECT ?, horse_id,
                   CAST(form AS REAL), CAST(train AS REAL), note, datetime('now')
            FROM stg_adjustments
            ON CONFLICT(version_id, horse_id) DO UPDATE SET
                form=excluded.form, train=excluded.train, note=datetime('now')
        """, (version_id,))
        con.execute("COMMIT")
        print(f"[OK] version={version_id} で反映しました。")
    except Exception as e:
        con.execute("ROLLBACK")
        raise
    finally:
        con.close()

if __name__=="__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--xlsx", required=True)
    ap.add_argument("--sheet", default="adjustments")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--version", default=None)
    args = ap.parse_args()
    main(args.db, args.xlsx, args.sheet, args.dry_run, args.version)
