-- 正しい血統情報の修正（海外馬を含む）
PRAGMA foreign_keys=OFF;

-- ホーエリートの血統情報を正しく修正（ゴールデンハープの父はステイゴールド）
UPDATE N_UMA SET 
    Ketto3InfoBamei1 = 'ルーラーシップ',
    Ketto3InfoBamei2 = 'ゴールデンハープ', 
    Ketto3InfoBamei3 = 'ステイゴールド'
WHERE Bamei = 'ホーエリート';

-- ゴールデンハープの血統情報も正しく修正
UPDATE N_UMA SET 
    Ketto3InfoBamei1 = 'ステイゴールド',
    Ketto3InfoBamei2 = 'ケルティックハープ', 
    Ketto3InfoBamei3 = 'クロフネ'
WHERE Bamei = 'ゴールデンハープ';

-- コスモキュランダの血統情報を正しく修正
UPDATE N_UMA SET 
    Ketto3InfoBamei1 = 'アルアイン',
    Ketto3InfoBamei2 = 'サザンスピード', 
    Ketto3InfoBamei3 = 'Southern Image'
WHERE Bamei = 'コスモキュランダ';

-- リビアングラスの血統情報を正しく修正
UPDATE N_UMA SET 
    Ketto3InfoBamei1 = 'ディープインパクト',
    Ketto3InfoBamei2 = 'リビアングラス', 
    Ketto3InfoBamei3 = 'Curlin'
WHERE Bamei = 'リビアングラス';

-- 海外馬の血統情報を追加（存在しない場合のみ）
INSERT OR IGNORE INTO N_UMA (KettoNum, Bamei, Ketto3InfoBamei1, Ketto3InfoBamei2, Ketto3InfoBamei3)
VALUES 
    ('1999100001', 'Southern Image', 'Halo', 'Southern Halo', 'Halo'),
    ('1998100001', 'Curlin', 'Smart Strike', 'Sherriff\'s Deputy', 'Deputy Minister'),
    ('1997100001', 'Halo', 'Hail to Reason', 'Cosmah', 'Cosmic Bomb');

-- サザンスピードの血統情報を追加（存在しない場合のみ）
INSERT OR IGNORE INTO N_UMA (KettoNum, Bamei, Ketto3InfoBamei1, Ketto3InfoBamei2, Ketto3InfoBamei3)
VALUES ('2000100001', 'サザンスピード', 'Southern Image', 'Southern Halo', 'Halo');

-- アルアインの血統情報を追加（存在しない場合のみ）
INSERT OR IGNORE INTO N_UMA (KettoNum, Bamei, Ketto3InfoBamei1, Ketto3InfoBamei2, Ketto3InfoBamei3)
VALUES ('2000100002', 'アルアイン', 'Dubai Millennium', 'Al Bahathri', 'Bahamian');

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
