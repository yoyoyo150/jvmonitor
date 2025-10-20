-- 正確な血統情報の修正
PRAGMA foreign_keys=OFF;

-- フェアエールングの血統情報を正確なデータで更新
UPDATE N_UMA SET 
    Ketto3InfoBamei1 = 'ゴールドシップ',
    Ketto3InfoBamei2 = 'マイネポリーヌ', 
    Ketto3InfoBamei3 = 'スペシャルウイーク'
WHERE Bamei = 'フェアエールング' OR Bamei = 'ファアエールング';

-- ドゥラドレースの血統情報を正確なデータで更新
UPDATE N_UMA SET 
    Ketto3InfoBamei1 = 'ドゥラメンテ',
    Ketto3InfoBamei2 = 'リカ',
    Ketto3InfoBamei3 = 'ハービンジャー'
WHERE Bamei = 'ドゥラドレース';

-- ワイドエンペラーの血統情報を正確なデータで更新
UPDATE N_UMA SET 
    Ketto3InfoBamei1 = 'ディープインパクト',
    Ketto3InfoBamei2 = 'アグネスデジタル',
    Ketto3InfoBamei3 = 'アグネスタキオン'
WHERE Bamei = 'ワイドエンペラー';

-- ホーエリートの血統情報を正確なデータで更新
UPDATE N_UMA SET 
    Ketto3InfoBamei1 = 'ルーラーシップ',
    Ketto3InfoBamei2 = 'ゴールデンハープ',
    Ketto3InfoBamei3 = 'キングカメハメハ'
WHERE Bamei = 'ホーエリート';

-- その他の主要な馬の血統情報も更新
-- スペシャルウイークの血統情報
UPDATE N_UMA SET 
    Ketto3InfoBamei1 = 'スペシャルウィーク',
    Ketto3InfoBamei2 = 'スイートロジー',
    Ketto3InfoBamei3 = 'サンデーサイレンス'
WHERE Bamei = 'スペシャルウイーク';

-- アグネスタキオンの血統情報
UPDATE N_UMA SET 
    Ketto3InfoBamei1 = 'アグネスタキオン',
    Ketto3InfoBamei2 = 'アグネスフローラ',
    Ketto3InfoBamei3 = 'サンデーサイレンス'
WHERE Bamei = 'アグネスタキオン';

-- キングカメハメハの血統情報
UPDATE N_UMA SET 
    Ketto3InfoBamei1 = 'キングカメハメハ',
    Ketto3InfoBamei2 = 'マンファス',
    Ketto3InfoBamei3 = 'サンデーサイレンス'
WHERE Bamei = 'キングカメハメハ';

-- ゴールドシップの血統情報
UPDATE N_UMA SET 
    Ketto3InfoBamei1 = 'ゴールドシップ',
    Ketto3InfoBamei2 = 'ポイントレイズ',
    Ketto3InfoBamei3 = 'サンデーサイレンス'
WHERE Bamei = 'ゴールドシップ';

-- ディープインパクトの血統情報
UPDATE N_UMA SET 
    Ketto3InfoBamei1 = 'ディープインパクト',
    Ketto3InfoBamei2 = 'ウインドインハーヘア',
    Ketto3InfoBamei3 = 'サンデーサイレンス'
WHERE Bamei = 'ディープインパクト';

-- ルーラーシップの血統情報
UPDATE N_UMA SET 
    Ketto3InfoBamei1 = 'ルーラーシップ',
    Ketto3InfoBamei2 = 'ルーラーシップ',
    Ketto3InfoBamei3 = 'サンデーサイレンス'
WHERE Bamei = 'ルーラーシップ';

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

