PRAGMA foreign_keys = ON;

-- 1) 本番テーブル（例：Excelからの補正を集約）
CREATE TABLE IF NOT EXISTS x_adjustments (
  version_id   TEXT NOT NULL,       -- スナップショットID（例: 2025-10-01T11:20）
  horse_id     TEXT NOT NULL,
  form         REAL,                 -- 任意
  train        REAL,                 -- 任意
  note         TEXT,
  updated_at   TEXT NOT NULL DEFAULT (datetime('now')),
  PRIMARY KEY (version_id, horse_id)
);

-- 2) ステージング（今回の取り込み一時置き場）
CREATE TABLE IF NOT EXISTS stg_adjustments (
  horse_id     TEXT,
  form         REAL,
  train        REAL,
  note         TEXT
);

-- 3) 参照整合チェック用の存在ビュー（例：登録済み馬のみOK）
-- v_results_official は既に存在するので、それを利用して v_known_horses を作成
CREATE VIEW IF NOT EXISTS v_known_horses AS
SELECT DISTINCT horse_name AS horse_id FROM v_results_official;

-- 4) アプリ参照用ビュー（最新versionのみ見せる）
CREATE VIEW IF NOT EXISTS v_adjustments AS
WITH latest AS (
  SELECT version_id FROM x_adjustments
  ORDER BY version_id DESC LIMIT 1
)
SELECT a.*
FROM x_adjustments a
JOIN latest l ON l.version_id = a.version_id;




