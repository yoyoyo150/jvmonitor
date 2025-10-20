-- ワイドエンペラーの母父をアグネスタキオンに修正
PRAGMA foreign_keys=OFF;

-- 既存のビューを削除
DROP VIEW IF EXISTS BLOODLINE_INFO_VIEW;

-- 血統情報ビューを作成
CREATE VIEW BLOODLINE_INFO_VIEW AS
SELECT 
    UMA.KettoNum,
    UMA.Bamei,
    UMA.Ketto3InfoBamei1 as ChichiBamei,
    UMA.Ketto3InfoBamei2 as HahaBamei,
    UMA.Ketto3InfoBamei3 as HahaChichiBamei,
    -- 親の血統情報を取得
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

-- ワイドエンペラーの母父をアグネスタキオンに修正
UPDATE N_UMA
SET Ketto3InfoBamei3 = 'アグネスタキオン'
WHERE KettoNum = '2018101660' AND Bamei = 'ワイドエンペラー';

-- 変更を確認
SELECT KettoNum, Bamei, Ketto3InfoBamei1, Ketto3InfoBamei2, Ketto3InfoBamei3
FROM N_UMA
WHERE KettoNum = '2018101660';

