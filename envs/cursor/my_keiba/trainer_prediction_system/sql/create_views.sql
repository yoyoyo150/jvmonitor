-- 成績（着順）ゆらぎを吸収するビュー
CREATE VIEW IF NOT EXISTS v_results_official AS
SELECT 
  -- N_UMA_RACEテーブルのキー
  Year || MonthDay AS race_date,
  JyoCD,
  RaceNum,
  Umaban,
  Year || MonthDay || JyoCD || RaceNum AS race_id,
  Bamei AS horse_name,
  ChokyosiRyakusyo AS trainer_name,
  
  -- 列名ゆらぎを吸収（存在するものを順に採用）
  KakuteiJyuni AS finish_pos,
  Time AS time_sec,
  Odds AS tan_odds,
  
  -- その他の情報
  Ninki AS popularity,
  Honsyokin AS prize_money
FROM N_UMA_RACE
WHERE KakuteiJyuni IS NOT NULL 
  AND KakuteiJyuni != ''
  AND KakuteiJyuni NOT IN ('00', '止', '除', '取');

-- オッズビュー（N_ODDS_TANPUKUから取得）
CREATE VIEW IF NOT EXISTS v_odds_official AS
SELECT 
  Year || MonthDay || JyoCD || RaceNum AS race_id,
  Umaban,
  TanOdds AS tan_odds,
  TanNinki AS tan_ninki,
  FukuOddsLow AS fuku_odds_low,
  FukuOddsHigh AS fuku_odds_high,
  FukuNinki AS fuku_ninki
FROM N_ODDS_TANPUKU;
