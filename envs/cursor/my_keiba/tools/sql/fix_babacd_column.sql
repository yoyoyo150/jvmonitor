-- R.BabaCDカラムエラーの修正
PRAGMA foreign_keys=OFF;

-- 既存のビューを削除
DROP VIEW IF EXISTS RACE_WITH_BABA;
DROP VIEW IF EXISTS HORSE_DETAIL_VIEW;

-- 馬場状態を含むシンプルなビューを作成（N_RACEテーブルのBabaCDカラムを直接使用）
CREATE VIEW RACE_WITH_BABA AS
SELECT 
    R.*,
    CASE
        -- 数値コード
        WHEN R.BabaCD = '1' THEN '良'
        WHEN R.BabaCD = '2' THEN '稍重'
        WHEN R.BabaCD = '3' THEN '重'
        WHEN R.BabaCD = '4' THEN '不良'
        -- 文字列コード
        WHEN R.BabaCD = '良' THEN '良'
        WHEN R.BabaCD = '稍重' THEN '稍重'
        WHEN R.BabaCD = '重' THEN '重'
        WHEN R.BabaCD = '不良' THEN '不良'
        -- 英語表記
        WHEN R.BabaCD = 'good' THEN '良'
        WHEN R.BabaCD = 'yielding' THEN '稍重'
        WHEN R.BabaCD = 'soft' THEN '重'
        WHEN R.BabaCD = 'heavy' THEN '不良'
        -- デフォルト
        ELSE COALESCE(R.BabaCD, '良')
    END as BabaCondition
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
    RWB.BabaCondition as BabaCD,
    -- 正確な頭数を取得
    (SELECT COUNT(*) FROM N_UMA_RACE UR2 
     WHERE UR2.Year = UR.Year 
     AND UR2.MonthDay = UR.MonthDay 
     AND UR2.JyoCD = UR.JyoCD 
     AND UR2.RaceNum = UR.RaceNum) as ActualFieldSize
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

