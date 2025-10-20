# 馬カードシステム設計書

## 概要
血統番号を基にした馬の管理システム。TARGET frontier との互換性を確保し、JRAVANデータと独自変数を統合する。

## システム構成

### 1. データソース
- **JRAVANデータ**: JVMonitor.exe 経由で取得
- **独自変数**: yDate/Excel データ
- **血統情報**: 過去3代前血統など

### 2. 馬カードの構造
```
馬カード {
  血統番号: 主要キー
  馬名: 表示用
  血統情報: {
    父: 父馬情報
    母: 母馬情報
    祖父: 祖父馬情報
    祖母: 祖母馬情報
    曾祖父: 曾祖父馬情報
    曾祖母: 曾祖母馬情報
  }
  レース情報: {
    過去レース: 過去のレース結果
    成績: 勝率、連対率、複勝率
  }
  独自変数: {
    Mark5/Mark6: 馬印データ
    ZI_INDEX: 独自指標
    ZM_VALUE: 独自指標
    その他: yDate の独自変数
  }
}
```

### 3. データベース設計

#### 3.1 馬マスターテーブル (horse_master)
```sql
CREATE TABLE horse_master (
  ketto_num TEXT PRIMARY KEY,  -- 血統番号
  horse_name TEXT NOT NULL,    -- 馬名
  birth_date TEXT,             -- 生年月日
  sex TEXT,                    -- 性別
  color TEXT,                  -- 毛色
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now'))
);
```

#### 3.2 血統テーブル (pedigree)
```sql
CREATE TABLE pedigree (
  ketto_num TEXT PRIMARY KEY,  -- 血統番号
  father_ketto TEXT,           -- 父の血統番号
  mother_ketto TEXT,            -- 母の血統番号
  grandfather_father TEXT,      -- 祖父（父方）
  grandmother_father TEXT,     -- 祖母（父方）
  grandfather_mother TEXT,      -- 祖父（母方）
  grandmother_mother TEXT,     -- 祖母（母方）
  FOREIGN KEY (ketto_num) REFERENCES horse_master(ketto_num)
);
```

#### 3.3 レース結果テーブル (race_results)
```sql
CREATE TABLE race_results (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ketto_num TEXT NOT NULL,     -- 血統番号
  race_date TEXT NOT NULL,      -- レース日
  race_name TEXT,               -- レース名
  finish_order TEXT,            -- 着順
  jockey_name TEXT,             -- 騎手名
  trainer_name TEXT,            -- 調教師名
  odds TEXT,                    -- オッズ
  FOREIGN KEY (ketto_num) REFERENCES horse_master(ketto_num)
);
```

#### 3.4 独自変数テーブル (custom_variables)
```sql
CREATE TABLE custom_variables (
  ketto_num TEXT NOT NULL,     -- 血統番号
  variable_name TEXT NOT NULL, -- 変数名
  variable_value TEXT,         -- 変数値
  source_date TEXT,            -- データソース日
  PRIMARY KEY (ketto_num, variable_name, source_date),
  FOREIGN KEY (ketto_num) REFERENCES horse_master(ketto_num)
);
```

### 4. データ統合フロー

#### 4.1 JRAVANデータの取得
1. JVMonitor.exe でJRAVANデータを取得
2. ecore.db に格納
3. 血統番号を基に馬マスターを更新

#### 4.2 独自変数の統合
1. yDate/Excel データを読み込み
2. 血統番号で馬マスターと照合
3. 独自変数テーブルに格納

#### 4.3 馬カードの生成
1. 血統番号を基に全データを統合
2. 血統情報、レース結果、独自変数を結合
3. 馬カードとして出力

### 5. TARGET frontier との互換性

#### 5.1 血統番号ベースの管理
- 血統番号を主要キーとして使用
- TARGET frontier と同じ血統番号体系を使用

#### 5.2 データ形式の統一
- 血統情報の形式をTARGET frontier と統一
- 独自変数の命名規則を統一

### 6. 実装手順

#### Phase 1: 基盤構築
1. 馬マスターテーブルの作成
2. 血統テーブルの作成
3. 基本的なCRUD操作の実装

#### Phase 2: データ統合
1. JRAVANデータの統合
2. 独自変数の統合
3. データ品質の検証

#### Phase 3: 馬カードシステム
1. 馬カードの生成機能
2. 検索・フィルタリング機能
3. 出力機能（CSV、JSON、HTML）

#### Phase 4: TARGET frontier 連携
1. データ形式の統一
2. インポート/エクスポート機能
3. 互換性の検証

### 7. 技術要件

#### 7.1 データベース
- SQLite (ecore.db との統合)
- 血統番号を主要キーとした設計

#### 7.2 プログラミング言語
- Python (既存システムとの統合)
- SQLite3 ライブラリ

#### 7.3 外部連携
- JVMonitor.exe との連携
- TARGET frontier との互換性

### 8. 品質管理

#### 8.1 データ品質
- 血統番号の一意性確保
- データの整合性チェック
- 重複データの排除

#### 8.2 パフォーマンス
- インデックスの最適化
- クエリの最適化
- 大量データの処理

### 9. 今後の拡張性

#### 9.1 新機能の追加
- 血統分析機能
- 予測機能
- レポート機能

#### 9.2 他システムとの連携
- 他の競馬分析ソフトとの連携
- API の提供
- データのエクスポート

## まとめ
血統番号を基にした馬カードシステムにより、JRAVANデータと独自変数を統合し、TARGET frontier との互換性を確保する。これにより、市販ソフトレベルの半製品を実現する。




