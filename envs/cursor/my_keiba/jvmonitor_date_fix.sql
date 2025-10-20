
-- JVMonitor日付選択問題修正用SQL
-- 2024年9月4日より過去の日付が選択できない問題を解決

-- 1. 日付選択用テーブルの作成
CREATE TABLE IF NOT EXISTS DateSelection (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Year VARCHAR(4),
    MonthDay VARCHAR(4),
    RaceDate VARCHAR(8),
    DisplayDate VARCHAR(10),
    RaceCount INTEGER,
    VenueCount INTEGER,
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. 既存データのクリア
DELETE FROM DateSelection;

-- 3. 日付データの挿入
INSERT INTO DateSelection (Year, MonthDay, RaceDate, DisplayDate, RaceCount, VenueCount)
SELECT 
    Year,
    MonthDay,
    Year || MonthDay as RaceDate,
    Year || '/' || MonthDay as DisplayDate,
    COUNT(*) as RaceCount,
    COUNT(DISTINCT JyoCD) as VenueCount
FROM N_RACE
GROUP BY Year, MonthDay
ORDER BY Year DESC, MonthDay DESC;

-- 4. インデックスの作成
CREATE INDEX IF NOT EXISTS idx_date_selection_date ON DateSelection (Year, MonthDay);
CREATE INDEX IF NOT EXISTS idx_date_selection_race_date ON DateSelection (RaceDate);

-- 5. 2024年9月4日より過去のデータ確認
SELECT 
    Year,
    MonthDay,
    DisplayDate,
    RaceCount,
    VenueCount
FROM DateSelection
WHERE Year = '2024' AND MonthDay < '0904'
ORDER BY MonthDay DESC
LIMIT 20;

-- 6. 全データの確認
SELECT COUNT(*) as TotalDays FROM DateSelection;
SELECT MIN(RaceDate) as EarliestDate, MAX(RaceDate) as LatestDate FROM DateSelection;
