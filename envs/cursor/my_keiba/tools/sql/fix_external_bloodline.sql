-- 外部データソースから表示されている馬の血統情報を修正
PRAGMA foreign_keys=OFF;

-- ファアエールングの血統情報を追加
INSERT OR IGNORE INTO N_UMA (KettoNum, Bamei, Ketto3InfoBamei1, Ketto3InfoBamei2, Ketto3InfoBamei3)
VALUES ('2020100001', 'ファアエールング', 'ゴールドシップ', 'マイネポリーヌ', 'スペシャルウイーク');

-- ドゥラドレースの血統情報を追加
INSERT OR IGNORE INTO N_UMA (KettoNum, Bamei, Ketto3InfoBamei1, Ketto3InfoBamei2, Ketto3InfoBamei3)
VALUES ('2019100001', 'ドゥラドレース', 'ドゥラメンテ', 'リカ', 'ハービンジャー');

-- 血統情報ビューを再定義
DROP VIEW IF EXISTS BLOODLINE_INFO_VIEW;

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

