-- 馬詳細ビューのパフォーマンス改善
PRAGMA foreign_keys=OFF;

-- 既存のビューを削除
DROP VIEW IF EXISTS HORSE_DETAIL_VIEW;
DROP VIEW IF EXISTS RACE_WITH_BABA;

-- 必要なインデックスを作成
CREATE INDEX IF NOT EXISTS idx_n_uma_race_kettonum ON N_UMA_RACE(KettoNum);
CREATE INDEX IF NOT EXISTS idx_n_uma_race_race_key ON N_UMA_RACE(Year, MonthDay, JyoCD, RaceNum);
CREATE INDEX IF NOT EXISTS idx_race_result_race_key ON RACE_RESULT(Year, MonthDay, JyoCD, RaceNum);

-- 馬場状態を含むシンプルなビューを作成
CREATE VIEW RACE_WITH_BABA AS
SELECT 
    R.*,
    COALESCE(
        (SELECT BabaCondition FROM RACE_RESULT 
         WHERE RACE_RESULT.Year = R.Year 
         AND RACE_RESULT.MonthDay = R.MonthDay 
         AND RACE_RESULT.JyoCD = R.JyoCD 
         AND RACE_RESULT.RaceNum = R.RaceNum),
        '1'
    ) as BabaCD
FROM N_RACE R;

-- 馬詳細表示用の最適化されたビュー
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
    COALESCE(RWB.BabaCD, '1') as BabaCD
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


