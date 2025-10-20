-- 血統情報の強制更新
PRAGMA foreign_keys=OFF;

-- 主要な馬の血統情報を強制的に更新
UPDATE N_UMA SET 
    Ketto3InfoBamei1 = 'ルーラーシップ',
    Ketto3InfoBamei2 = 'ゴールデンハープ', 
    Ketto3InfoBamei3 = 'ステイゴールド'
WHERE Bamei = 'ホーエリート';

UPDATE N_UMA SET 
    Ketto3InfoBamei1 = 'ゴールドシップ',
    Ketto3InfoBamei2 = 'マイネポリーヌ', 
    Ketto3InfoBamei3 = 'スペシャルウイーク'
WHERE Bamei = 'フェアエールング';

UPDATE N_UMA SET 
    Ketto3InfoBamei1 = 'ディープインパクト',
    Ketto3InfoBamei2 = 'アグネスデジタル', 
    Ketto3InfoBamei3 = 'アグネスタキオン'
WHERE Bamei = 'ワイドエンペラー';

UPDATE N_UMA SET 
    Ketto3InfoBamei1 = 'アルアイン',
    Ketto3InfoBamei2 = 'サザンスピード', 
    Ketto3InfoBamei3 = 'Southern Image'
WHERE Bamei = 'コスモキュランダ';

UPDATE N_UMA SET 
    Ketto3InfoBamei1 = 'キズナ',
    Ketto3InfoBamei2 = 'ディルガ', 
    Ketto3InfoBamei3 = 'Curlin'
WHERE Bamei = 'リビアングラス';

UPDATE N_UMA SET 
    Ketto3InfoBamei1 = 'キズナ',
    Ketto3InfoBamei2 = 'ソベラニア', 
    Ketto3InfoBamei3 = 'ディープインパクト'
WHERE Bamei = 'シュバルツクーゲル';

UPDATE N_UMA SET 
    Ketto3InfoBamei1 = 'ディープインパクト',
    Ketto3InfoBamei2 = 'クロウキャニオン', 
    Ketto3InfoBamei3 = 'フレンチデピュティ'
WHERE Bamei = 'ヨーホーレイク';

-- 血統情報ビューを強制的に再作成
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

-- インデックスを再作成してパフォーマンスを向上
CREATE INDEX IF NOT EXISTS idx_n_uma_bloodline ON N_UMA (Ketto3InfoBamei1, Ketto3InfoBamei2, Ketto3InfoBamei3);
CREATE INDEX IF NOT EXISTS idx_n_uma_bamei ON N_UMA (Bamei);

PRAGMA foreign_keys=ON;

