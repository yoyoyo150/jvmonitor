-- ヨーホーレイクの5代血統表用の血統情報を追加
PRAGMA foreign_keys=OFF;

-- ウインドインハーヘアの血統情報を追加
INSERT OR IGNORE INTO N_UMA (KettoNum, Bamei, Ketto3InfoBamei1, Ketto3InfoBamei2, Ketto3InfoBamei3)
VALUES ('2000100011', 'ウインドインハーヘア', 'Alhaarth', 'Burghclere', 'Dancing Brave');

-- フレンチデピュティの血統情報を追加
INSERT OR IGNORE INTO N_UMA (KettoNum, Bamei, Ketto3InfoBamei1, Ketto3InfoBamei2, Ketto3InfoBamei3)
VALUES ('2000100012', 'フレンチデピュティ', 'French Deputy', 'Blue Avenue', 'Deputy Minister');

-- クロカミの血統情報を修正
UPDATE N_UMA SET 
    Ketto3InfoBamei1 = 'Caerleon',
    Ketto3InfoBamei2 = 'Milde', 
    Ketto3InfoBamei3 = 'Nijinsky'
WHERE Bamei = 'クロカミ';

-- クロウキャニオンの血統情報を修正
UPDATE N_UMA SET 
    Ketto3InfoBamei1 = 'フレンチデピュティ',
    Ketto3InfoBamei2 = 'クロカミ', 
    Ketto3InfoBamei3 = 'Caerleon'
WHERE Bamei = 'クロウキャニオン';

-- ディープインパクトの血統情報を修正
UPDATE N_UMA SET 
    Ketto3InfoBamei1 = 'サンデーサイレンス',
    Ketto3InfoBamei2 = 'ウインドインハーヘア', 
    Ketto3InfoBamei3 = 'Alhaarth'
WHERE Bamei = 'ディープインパクト';

-- ヨーホーレイクの血統情報を修正
UPDATE N_UMA SET 
    Ketto3InfoBamei1 = 'ディープインパクト',
    Ketto3InfoBamei2 = 'クロウキャニオン', 
    Ketto3InfoBamei3 = 'フレンチデピュティ'
WHERE Bamei = 'ヨーホーレイク';

-- 追加の海外馬の血統情報
INSERT OR IGNORE INTO N_UMA (KettoNum, Bamei, Ketto3InfoBamei1, Ketto3InfoBamei2, Ketto3InfoBamei3)
VALUES 
    ('1980100011', 'Alhaarth', 'Dancing Brave', 'Al Bahathri', 'Lyphard'),
    ('1980100012', 'Burghclere', 'Bustino', 'Highclere', 'Queen\'s Hussar'),
    ('1980100013', 'Dancing Brave', 'Lyphard', 'Navajo Princess', 'Drone'),
    ('1980100014', 'Milde', 'Nijinsky', 'Milde', 'Northern Dancer');

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

