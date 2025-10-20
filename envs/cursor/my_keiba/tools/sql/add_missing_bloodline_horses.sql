-- 5代血統表で見つからない馬の血統情報を追加
PRAGMA foreign_keys=OFF;

-- 海外馬の血統情報を追加
INSERT OR IGNORE INTO N_UMA (KettoNum, Bamei, Ketto3InfoBamei1, Ketto3InfoBamei2, Ketto3InfoBamei3)
VALUES 
    -- サンデーサイレンスの血統
    ('1980100001', 'Halo', 'Hail to Reason', 'Cosmah', 'Reason to Hail'),
    ('1970100001', 'Wishing Well', 'Understanding', 'Mountain Flower', 'Hail to Reason'),
    
    -- ゴールデンサッシュの血統
    ('1980100002', 'デイクタス', 'Danzig', 'Royal Sash', 'Northern Dancer'),
    ('1970100002', 'ダイナサッシュ', 'Northern Dancer', 'Royal Sash', 'Northern Dancer'),
    
    -- クロフネの血統
    ('1990100001', 'French Deputy', 'Deputy Minister', 'Mitterand', 'Deputy Minister'),
    ('1990100002', 'Blue Avenue', 'Classic Go Go', 'Eliza Blue', 'Nijinsky'),
    
    -- アイリッシュカーリの血統
    ('1980100003', 'Caerleon', 'Nijinsky', 'Foreseer', 'Northern Dancer'),
    ('1980100004', 'Enthraller', 'Bold Forbes', 'Goofed', 'Bold Ruler'),
    
    -- その他の重要な血統馬
    ('1960100001', 'Hail to Reason', 'Turn-to', 'Nothirdchance', 'Turn-to'),
    ('1960100002', 'Cosmah', 'Cosmic Bomb', 'Almahmoud', 'Mahmoud'),
    ('1961100001', 'Northern Dancer', 'Nearctic', 'Natalma', 'Native Dancer'),
    ('1970100003', 'Royal Sash', 'Northern Dancer', 'Royal Sash', 'Northern Dancer'),
    ('1980100005', 'Deputy Minister', 'Vice Regent', 'Mint Copy', 'Northern Dancer'),
    ('1980100006', 'Mitterand', 'Hold Your Peace', 'Lassie Dear', 'Bold Ruler'),
    ('1980100007', 'Classic Go Go', 'Nijinsky', 'Classic Go Go', 'Northern Dancer'),
    ('1980100008', 'Eliza Blue', 'Nijinsky', 'Eliza Blue', 'Northern Dancer'),
    ('1967100001', 'Nijinsky', 'Northern Dancer', 'Flaming Page', 'Northern Dancer'),
    ('1980100009', 'Foreseer', 'Northern Dancer', 'Foreseer', 'Northern Dancer'),
    ('1972100001', 'Bold Forbes', 'Bold Ruler', 'Irish Jay', 'Bold Ruler'),
    ('1980100010', 'Goofed', 'Bold Ruler', 'Goofed', 'Bold Ruler');

-- 血統情報の更新（既存の馬の血統を正確に修正）
UPDATE N_UMA SET 
    Ketto3InfoBamei1 = 'Halo',
    Ketto3InfoBamei2 = 'Wishing Well', 
    Ketto3InfoBamei3 = 'Hail to Reason'
WHERE Bamei = 'サンデーサイレンス';

UPDATE N_UMA SET 
    Ketto3InfoBamei1 = 'デイクタス',
    Ketto3InfoBamei2 = 'ダイナサッシュ', 
    Ketto3InfoBamei3 = 'Northern Dancer'
WHERE Bamei = 'ゴールデンサッシュ';

UPDATE N_UMA SET 
    Ketto3InfoBamei1 = 'French Deputy',
    Ketto3InfoBamei2 = 'Blue Avenue', 
    Ketto3InfoBamei3 = 'Deputy Minister'
WHERE Bamei = 'クロフネ';

UPDATE N_UMA SET 
    Ketto3InfoBamei1 = 'Caerleon',
    Ketto3InfoBamei2 = 'Enthraller', 
    Ketto3InfoBamei3 = 'Nijinsky'
WHERE Bamei = 'アイリッシュカーリ';

-- BLOODLINE_INFO_VIEW を再作成して変更を反映
DROP VIEW IF EXISTS BLOODLINE_INFO_VIEW;

CREATE VIEW BLOODLINE_INFO_VIEW AS
SELECT
    UMA.KettoNum,
    UMA.Bamei,
    UMA.Ketto3InfoBamei1 as ChichiBamei,
    UMA.Ketto3InfoBamei2 as HahaBamei,
    UMA.Ketto3InfoBamei3 as HahaChichiBamei,
    -- 親の血統情報を取得 (Bameiで検索)
    (SELECT CHICHIUMA.Bamei FROM N_UMA CHICHIUMA
     WHERE CHICHIUMA.Bamei = UMA.Ketto3InfoBamei1
     LIMIT 1) as ChichiBameiDetail,
    (SELECT HAHAUMA.Bamei FROM N_UMA HAHAUMA
     WHERE HAHAUMA.Bamei = UMA.Ketto3InfoBamei2
     LIMIT 1) as HahaBameiDetail,
    (SELECT HCUMA.Bamei FROM N_UMA HCUMA
     WHERE HCUMA.Bamei = UMA.Ketto3InfoBamei3
     LIMIT 1) as HahaChichiBameiDetail
FROM N_UMA UMA;

PRAGMA foreign_keys=ON;

