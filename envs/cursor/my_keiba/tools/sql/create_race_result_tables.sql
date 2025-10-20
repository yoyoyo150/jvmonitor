-- RACE_RESULT tables creation
CREATE TABLE IF NOT EXISTS RACE_RESULT (
    Year TEXT NOT NULL,
    MonthDay TEXT NOT NULL,
    JyoCD TEXT NOT NULL,
    RaceNum TEXT NOT NULL,
    RaceName TEXT,
    TrackCD TEXT,
    Kyori INTEGER,
    BabaCondition TEXT,
    FieldSize INTEGER,
    HassoTime TEXT,
    PRIMARY KEY (Year, MonthDay, JyoCD, RaceNum)
);

CREATE TABLE IF NOT EXISTS RACE_RESULT_HORSE (
    Year TEXT NOT NULL,
    MonthDay TEXT NOT NULL,
    JyoCD TEXT NOT NULL,
    RaceNum TEXT NOT NULL,
    Umaban TEXT NOT NULL,
    KettoNum TEXT,
    Bamei TEXT,
    KakuteiJyuni TEXT,
    DochakuTosu INTEGER,
    Ninki TEXT,
    Odds TEXT,
    Futan REAL,
    Jockey TEXT,
    Time TEXT,
    Jyuni1c TEXT,
    Jyuni2c TEXT,
    Jyuni3c TEXT,
    Jyuni4c TEXT,
    Last3F TEXT,
    PRIMARY KEY (Year, MonthDay, JyoCD, RaceNum, Umaban)
);
