DROP VIEW IF EXISTS v_prev12_nl;
CREATE VIEW v_prev12_nl AS
WITH cur AS (
  SELECT 
    idYear, idMonthDay, idJyoCD, idRaceNum,
    Umaban, KettoNum,
    (idYear||idMonthDay||idJyoCD||printf('%02d', idRaceNum)) AS cur_key
  FROM NL_SE_RACE_UMA
), prev AS (
  SELECT 
    c.idYear,
    c.idMonthDay,
    c.idJyoCD,
    c.idRaceNum,
    c.Umaban,
    c.KettoNum,
    (SELECT p.idYear FROM NL_SE_RACE_UMA p 
      WHERE p.KettoNum = c.KettoNum
        AND (p.idYear||p.idMonthDay||p.idJyoCD||printf('%02d', p.idRaceNum)) < c.cur_key
      ORDER BY p.idYear DESC, p.idMonthDay DESC, p.idJyoCD DESC, p.idRaceNum DESC
      LIMIT 1) AS prev1_year,
    (SELECT p.idMonthDay FROM NL_SE_RACE_UMA p 
      WHERE p.KettoNum = c.KettoNum
        AND (p.idYear||p.idMonthDay||p.idJyoCD||printf('%02d', p.idRaceNum)) < c.cur_key
      ORDER BY p.idYear DESC, p.idMonthDay DESC, p.idJyoCD DESC, p.idRaceNum DESC
      LIMIT 1) AS prev1_monthday,
    (SELECT p.idJyoCD FROM NL_SE_RACE_UMA p 
      WHERE p.KettoNum = c.KettoNum
        AND (p.idYear||p.idMonthDay||p.idJyoCD||printf('%02d', p.idRaceNum)) < c.cur_key
      ORDER BY p.idYear DESC, p.idMonthDay DESC, p.idJyoCD DESC, p.idRaceNum DESC
      LIMIT 1) AS prev1_jyo,
    (SELECT p.idRaceNum FROM NL_SE_RACE_UMA p 
      WHERE p.KettoNum = c.KettoNum
        AND (p.idYear||p.idMonthDay||p.idJyoCD||printf('%02d', p.idRaceNum)) < c.cur_key
      ORDER BY p.idYear DESC, p.idMonthDay DESC, p.idJyoCD DESC, p.idRaceNum DESC
      LIMIT 1) AS prev1_race,
    (SELECT p.KakuteiJyuni FROM NL_SE_RACE_UMA p 
      WHERE p.KettoNum = c.KettoNum
        AND (p.idYear||p.idMonthDay||p.idJyoCD||printf('%02d', p.idRaceNum)) < c.cur_key
      ORDER BY p.idYear DESC, p.idMonthDay DESC, p.idJyoCD DESC, p.idRaceNum DESC
      LIMIT 1) AS prev1_finish,
    (SELECT p.Jyuni1c FROM NL_SE_RACE_UMA p 
      WHERE p.KettoNum = c.KettoNum
        AND (p.idYear||p.idMonthDay||p.idJyoCD||printf('%02d', p.idRaceNum)) < c.cur_key
      ORDER BY p.idYear DESC, p.idMonthDay DESC, p.idJyoCD DESC, p.idRaceNum DESC
      LIMIT 1) AS prev1_corner1,
    (SELECT p.Jyuni2c FROM NL_SE_RACE_UMA p 
      WHERE p.KettoNum = c.KettoNum
        AND (p.idYear||p.idMonthDay||p.idJyoCD||printf('%02d', p.idRaceNum)) < c.cur_key
      ORDER BY p.idYear DESC, p.idMonthDay DESC, p.idJyoCD DESC, p.idRaceNum DESC
      LIMIT 1) AS prev1_corner2,
    (SELECT p.Jyuni3c FROM NL_SE_RACE_UMA p 
      WHERE p.KettoNum = c.KettoNum
        AND (p.idYear||p.idMonthDay||p.idJyoCD||printf('%02d', p.idRaceNum)) < c.cur_key
      ORDER BY p.idYear DESC, p.idMonthDay DESC, p.idJyoCD DESC, p.idRaceNum DESC
      LIMIT 1) AS prev1_corner3,
    (SELECT p.Jyuni4c FROM NL_SE_RACE_UMA p 
      WHERE p.KettoNum = c.KettoNum
        AND (p.idYear||p.idMonthDay||p.idJyoCD||printf('%02d', p.idRaceNum)) < c.cur_key
      ORDER BY p.idYear DESC, p.idMonthDay DESC, p.idJyoCD DESC, p.idRaceNum DESC
      LIMIT 1) AS prev1_corner4
  FROM cur c
)
SELECT
  idYear,
  idMonthDay,
  idJyoCD,
  idRaceNum,
  Umaban,
  KettoNum,
  prev1_year,
  prev1_monthday,
  prev1_jyo,
  prev1_race,
  prev1_finish,
  CASE
    WHEN prev1_year IS NULL THEN NULL
    ELSE (
      SELECT COUNT(*)
      FROM N_UMA_RACE
      WHERE Year = prev1_year
        AND MonthDay = prev1_monthday
        AND JyoCD = prev1_jyo
        AND RaceNum = prev1_race
    )
  END AS prev1_field_size,
  prev1_corner1,
  prev1_corner2,
  prev1_corner3,
  prev1_corner4
FROM prev;
