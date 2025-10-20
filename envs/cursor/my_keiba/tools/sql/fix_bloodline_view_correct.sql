-- 血統情報ビューの修正（海外馬対応）
PRAGMA foreign_keys=OFF;

-- 既存のビューを削除
DROP VIEW IF EXISTS BLOODLINE_INFO_VIEW;

-- 修正された血統情報ビューを作成
CREATE VIEW BLOODLINE_INFO_VIEW AS
SELECT 
    UMA.KettoNum,
    UMA.Bamei,
    UMA.Ketto3InfoBamei1 as ChichiBamei,
    UMA.Ketto3InfoBamei2 as HahaBamei,
    UMA.Ketto3InfoBamei3 as HahaChichiBamei,
    -- 親の血統情報を取得（存在しない場合は元の値を返す）
    COALESCE(
        (SELECT CHICHIUMA.Bamei FROM N_UMA CHICHIUMA 
         WHERE CHICHIUMA.Bamei = UMA.Ketto3InfoBamei1 
         LIMIT 1),
        UMA.Ketto3InfoBamei1
    ) as ChichiBameiDetail,
    COALESCE(
        (SELECT HAHAUMA.Bamei FROM N_UMA HAHAUMA 
         WHERE HAHAUMA.Bamei = UMA.Ketto3InfoBamei2 
         LIMIT 1),
        UMA.Ketto3InfoBamei2
    ) as HahaBameiDetail,
    COALESCE(
        (SELECT HCUMA.Bamei FROM N_UMA HCUMA 
         WHERE HCUMA.Bamei = UMA.Ketto3InfoBamei3 
         LIMIT 1),
        UMA.Ketto3InfoBamei3
    ) as HahaChichiBameiDetail
FROM N_UMA UMA;

