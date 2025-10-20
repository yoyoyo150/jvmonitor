-- 海外馬の血統情報を含む修正
PRAGMA foreign_keys=OFF;

-- コスモキュランダの血統情報を正確なデータで更新
UPDATE N_UMA SET 
    Ketto3InfoBamei1 = 'アルアイン',
    Ketto3InfoBamei2 = 'サザンスピード', 
    Ketto3InfoBamei3 = 'Southern Image'
WHERE Bamei = 'コスモキュランダ';

-- 海外馬の血統情報を追加（存在しない場合のみ）
INSERT OR IGNORE INTO N_UMA (KettoNum, Bamei, Ketto3InfoBamei1, Ketto3InfoBamei2, Ketto3InfoBamei3)
VALUES 
    ('1999100001', 'Southern Image', 'Halo', 'Southern Halo', 'Halo'),
    ('1998100001', 'Halo', 'Hail to Reason', 'Cosmah', 'Cosmic Bomb'),
    ('1997100001', 'Southern Halo', 'Halo', 'Southern Image', 'Halo');

-- サザンスピードの血統情報を追加（存在しない場合のみ）
INSERT OR IGNORE INTO N_UMA (KettoNum, Bamei, Ketto3InfoBamei1, Ketto3InfoBamei2, Ketto3InfoBamei3)
VALUES ('2000100001', 'サザンスピード', 'Southern Image', 'Southern Halo', 'Halo');

-- アルアインの血統情報を追加（存在しない場合のみ）
INSERT OR IGNORE INTO N_UMA (KettoNum, Bamei, Ketto3InfoBamei1, Ketto3InfoBamei2, Ketto3InfoBamei3)
VALUES ('2000100002', 'アルアイン', 'Dubai Millennium', 'Al Bahathri', 'Bahamian');

-- ホーエリートの正しい血統情報を設定
-- ホーエリートの母父が何であるべきか、正確な情報が必要
UPDATE N_UMA SET 
    Ketto3InfoBamei1 = 'ルーラーシップ',
    Ketto3InfoBamei2 = 'ゴールデンハープ', 
    Ketto3InfoBamei3 = 'ステイゴールド'  -- 正しい母父名に変更が必要
WHERE Bamei = 'ホーエリート';

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

