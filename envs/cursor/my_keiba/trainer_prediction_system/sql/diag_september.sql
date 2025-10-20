-- ① 9月の着順データ状況（件数とNull率）
WITH sept AS (
  SELECT 
    v.race_id,
    v.horse_name,
    v.trainer_name,
    v.finish_pos,
    v.race_date
  FROM v_results_official v
  WHERE substr(v.race_date, 1, 6) = '202509'
)
SELECT 
  COUNT(*) AS rows_total,
  SUM(CASE WHEN finish_pos IS NULL THEN 1 ELSE 0 END) AS rows_missing_pos,
  ROUND(100.0 * SUM(CASE WHEN finish_pos IS NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS missing_rate_pct,
  SUM(CASE WHEN finish_pos BETWEEN '1' AND '3' THEN 1 ELSE 0 END) AS place_hits
FROM sept;

-- ② 成績Nullのサンプル5件（どの結合で落ちた？を見せる）
SELECT * FROM (
  SELECT 
    v.race_id,
    v.horse_name,
    v.trainer_name,
    v.finish_pos,
    v.race_date
  FROM v_results_official v
  WHERE substr(v.race_date, 1, 6) = '202509'
    AND v.finish_pos IS NULL
  LIMIT 5
) AS sample_missing;

-- ③ 指定レース（例：2025-09-28 中山11R）が実在するかの"存在証明"
SELECT EXISTS(
  SELECT 1 FROM v_results_official 
  WHERE race_id = '202509280611'
) AS exists_flag;

SELECT race_id, horse_name, trainer_name, finish_pos, time_sec
FROM v_results_official
WHERE race_id = '202509280611'
ORDER BY CAST(finish_pos AS INTEGER)
LIMIT 5;
