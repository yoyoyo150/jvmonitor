-- 馬場状態カラムの互換性修正
PRAGMA foreign_keys=OFF;

-- 既存のビューがあれば削除
DROP VIEW IF EXISTS RACE_WITH_BABA;

-- 馬場状態を含むレースビューを作成
CREATE VIEW RACE_WITH_BABA AS
SELECT 
    R.*,
    CASE 
        WHEN R.TrackCD LIKE '1%' THEN -- 芝コース
            CASE 
                WHEN EXISTS (SELECT 1 FROM RACE_RESULT WHERE RACE_RESULT.Year = R.Year AND RACE_RESULT.MonthDay = R.MonthDay AND RACE_RESULT.JyoCD = R.JyoCD AND RACE_RESULT.RaceNum = R.RaceNum AND RACE_RESULT.BabaCondition IS NOT NULL) THEN
                    (SELECT BabaCondition FROM RACE_RESULT WHERE RACE_RESULT.Year = R.Year AND RACE_RESULT.MonthDay = R.MonthDay AND RACE_RESULT.JyoCD = R.JyoCD AND RACE_RESULT.RaceNum = R.RaceNum)
                ELSE '1' -- デフォルト：良
            END
        WHEN R.TrackCD LIKE '2%' THEN -- ダートコース
            CASE 
                WHEN EXISTS (SELECT 1 FROM RACE_RESULT WHERE RACE_RESULT.Year = R.Year AND RACE_RESULT.MonthDay = R.MonthDay AND RACE_RESULT.JyoCD = R.JyoCD AND RACE_RESULT.RaceNum = R.RaceNum AND RACE_RESULT.BabaCondition IS NOT NULL) THEN
                    (SELECT BabaCondition FROM RACE_RESULT WHERE RACE_RESULT.Year = R.Year AND RACE_RESULT.MonthDay = R.MonthDay AND RACE_RESULT.JyoCD = R.JyoCD AND RACE_RESULT.RaceNum = R.RaceNum)
                ELSE '1' -- デフォルト：良
            END
        ELSE '1' -- デフォルト：良
    END as BabaCD
FROM N_RACE R;

-- 馬詳細表示用のビュー
DROP VIEW IF EXISTS HORSE_DETAIL_VIEW;

CREATE VIEW HORSE_DETAIL_VIEW AS
SELECT
    UR.Year,
    UR.MonthDay,
    UR.JyoCD,
    UR.RaceNum,
    UR.KettoNum,
    UR.Bamei,
    UR.KisyuRyakusyo,
    UR.Futan,
    UR.KakuteiJyuni,
    UR.DochakuTosu,
    UR.Time as RaceTime,
    UR.TimeDiff,
    UR.HaronTimeL3,
    UR.Jyuni1c,
    UR.Jyuni2c,
    UR.Jyuni3c,
    UR.Jyuni4c,
    UR.Ninki,
    UR.Odds,
    UR.Honsyokin,
    R.TrackCD,
    R.Kyori,
    R.Hondai as RaceName,
    RWB.BabaCD
FROM N_UMA_RACE UR
LEFT JOIN N_RACE R ON 
    UR.Year = R.Year AND 
    UR.MonthDay = R.MonthDay AND 
    UR.JyoCD = R.JyoCD AND 
    UR.RaceNum = R.RaceNum
LEFT JOIN RACE_WITH_BABA RWB ON
    UR.Year = RWB.Year AND 
    UR.MonthDay = RWB.MonthDay AND 
    UR.JyoCD = RWB.JyoCD AND 
    UR.RaceNum = RWB.RaceNum;

-- EveryDB2.3用の互換ビュー
DROP VIEW IF EXISTS EVERYDB_RACE_VIEW;

CREATE VIEW EVERYDB_RACE_VIEW AS
SELECT
    R.*,
    COALESCE(RWB.BabaCD, '1') as BabaCD
FROM N_RACE R
LEFT JOIN RACE_WITH_BABA RWB ON
    R.Year = RWB.Year AND 
    R.MonthDay = RWB.MonthDay AND 
    R.JyoCD = RWB.JyoCD AND 
    R.RaceNum = RWB.RaceNum;


