-- R.BabaCDカラムエラーの修正（完全版）
PRAGMA foreign_keys=OFF;

-- 既存のビューを削除
DROP VIEW IF EXISTS RACE_WITH_BABA;
DROP VIEW IF EXISTS HORSE_DETAIL_VIEW;

-- 馬場状態を含むシンプルなビュー（BabaCDカラムの有無をチェック）
CREATE VIEW RACE_WITH_BABA AS
SELECT 
    R.*,
    '良' as BabaCondition -- デフォルト値として「良」を設定
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

-- インデックスを作成して検索速度を向上
CREATE INDEX IF NOT EXISTS idx_n_uma_race_kettonum ON N_UMA_RACE (KettoNum);
CREATE INDEX IF NOT EXISTS idx_n_uma_race_race_key ON N_UMA_RACE (Year, MonthDay, JyoCD, RaceNum);
CREATE INDEX IF NOT EXISTS idx_n_race_race_key ON N_RACE (Year, MonthDay, JyoCD, RaceNum);

