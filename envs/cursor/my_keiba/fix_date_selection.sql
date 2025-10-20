
-- 日付選択問題修正用SQL
-- JVMonitorの日付選択問題を解決するためのSQL

-- 1. 日付インデックスの作成
CREATE INDEX IF NOT EXISTS idx_race_date ON N_RACE (Year, MonthDay);
CREATE INDEX IF NOT EXISTS idx_race_date_desc ON N_RACE (Year DESC, MonthDay DESC);

-- 2. 日付ビューの作成
DROP VIEW IF EXISTS v_race_dates;
CREATE VIEW v_race_dates AS
SELECT 
    Year,
    MonthDay,
    Year || MonthDay as RaceDate,
    COUNT(*) as RaceCount,
    COUNT(DISTINCT JyoCD) as VenueCount
FROM N_RACE
GROUP BY Year, MonthDay
ORDER BY Year DESC, MonthDay DESC;

-- 3. 日付選択用ビューの作成
DROP VIEW IF EXISTS v_date_selection;
CREATE VIEW v_date_selection AS
SELECT 
    Year,
    MonthDay,
    Year || MonthDay as RaceDate,
    Year || '/' || MonthDay as DisplayDate,
    COUNT(*) as RaceCount
FROM N_RACE
GROUP BY Year, MonthDay
ORDER BY Year DESC, MonthDay DESC;

-- 4. 過去データ確認用クエリ
SELECT 
    Year,
    MonthDay,
    RaceDate,
    RaceCount
FROM v_date_selection
WHERE Year = '2024' AND MonthDay < '0904'
ORDER BY MonthDay DESC
LIMIT 20;
