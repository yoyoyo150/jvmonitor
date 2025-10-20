-- 5代血統表の正確な情報でデータベースを修正
PRAGMA foreign_keys=OFF;

-- ゴールデンハープの血統情報を5代血統表の正確な情報で更新
UPDATE N_UMA SET 
    Ketto3InfoBamei1 = 'ステイゴールド',
    Ketto3InfoBamei2 = 'ケルティックハープ', 
    Ketto3InfoBamei3 = 'クロフネ'
WHERE Bamei = 'ゴールデンハープ';

-- ステイゴールドの血統情報を追加（存在しない場合のみ）
INSERT OR IGNORE INTO N_UMA (KettoNum, Bamei, Ketto3InfoBamei1, Ketto3InfoBamei2, Ketto3InfoBamei3)
VALUES ('1994100001', 'ステイゴールド', 'サンデーサイレンス', 'ゴールデンサッシュ', 'デイクタス');

-- ケルティックハープの血統情報を追加（存在しない場合のみ）
INSERT OR IGNORE INTO N_UMA (KettoNum, Bamei, Ketto3InfoBamei1, Ketto3InfoBamei2, Ketto3InfoBamei3)
VALUES ('2004100001', 'ケルティックハープ', 'クロフネ', 'アイリッシュカーリ', 'Caerleon');

-- クロフネの血統情報を追加（存在しない場合のみ）
INSERT OR IGNORE INTO N_UMA (KettoNum, Bamei, Ketto3InfoBamei1, Ketto3InfoBamei2, Ketto3InfoBamei3)
VALUES ('1998100001', 'クロフネ', 'French Deputy', 'Blue Avenue', 'Deputy Minister');

-- サンデーサイレンスの血統情報を追加（存在しない場合のみ）
INSERT OR IGNORE INTO N_UMA (KettoNum, Bamei, Ketto3InfoBamei1, Ketto3InfoBamei2, Ketto3InfoBamei3)
VALUES ('1986100001', 'サンデーサイレンス', 'Halo', 'Wishing Well', 'Hail to Reason');

-- ホーエリートの血統情報を正しく修正（ゴールデンハープの父はステイゴールド）
UPDATE N_UMA SET 
    Ketto3InfoBamei1 = 'ルーラーシップ',
    Ketto3InfoBamei2 = 'ゴールデンハープ', 
    Ketto3InfoBamei3 = 'ステイゴールド'
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

