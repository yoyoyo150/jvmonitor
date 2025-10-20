-- 血統情報の修正
PRAGMA foreign_keys=OFF;

-- 血統情報を正確に取得するためのビューを作成
CREATE VIEW IF NOT EXISTS BLOODLINE_INFO_VIEW AS
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


