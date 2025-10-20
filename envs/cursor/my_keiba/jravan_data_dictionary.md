# JRAVAN データ辞書（初版）

- バージョン: **0.1.0**
- 更新日: **2025-09-08**

**注意事項**
- この辞書はプロジェクト用の暫定版です。公式仕様の数値コードは必ずJV-Dataのドキュメントで照合してください。
- コード表は `codes` にまとめ、ここからMarkdownに自動整形します。
- 必要に応じて codes に項目を追加してください。

## フィールド共通仕様（抜粋）

- **キー形式**: `RaceKey`（例: `202409070811` = YYYYMMDD + 開催場 + R）
- **オッズ表記**: JV-Dataの4桁固定文字列は 10 分の 1 にスケール（例: `0024` → 2.4、`0907` → 90.7）
- **時刻**: `HHMM`（例: `1530` = 15:30）。必要に応じて `:` を挿入して整形。
- **距離**: メートル単位の整数（例: `1200`, `2400`）

### オッズ変換（C#例）
```csharp
decimal ParseOdds(string s) {
    if (string.IsNullOrWhiteSpace(s)) return 0m;
    if (!int.TryParse(s.Trim(), out var raw)) return 0m;
    return raw / 10m; // '0024' -> 2.4, '0907' -> 90.7
}
```

## コード表

### 脚質コード
走法タイプの分類。一般的な通称（暫定）。

| コード | 意味 |
|:-----:|:-----|
| 1 | 逃げ |
| 2 | 先行 |
| 3 | 差し |
| 4 | 追込 |

### 性別コード
競走馬の性別（一般的な慣例）。

| コード | 意味 |
|:-----:|:-----|
| 1 | 牡 |
| 2 | 牝 |
| 3 | 騸 |

## テーブル定義（スケルトン）

以下は記入用の雛形です。必要に応じて列を追加してください。

### races（レース情報 / RA）

| 列名 | 型 | 説明 | 例 |
|---|---|---|---|
| RaceKey | TEXT | レース一意キー（YYYYMMDD + 場 + R） | 202409070811 |
| RaceDate | TEXT | 施行日（YYYY-MM-DD） | 2024-09-07 |
| TrackCD | TEXT | 競馬場コード（要コード表） | 05 |
| CourseCD | TEXT | コース種別（芝/ダ/障など） | T |
| Distance | INTEGER | 距離(m) | 1600 |
| GradeCD | TEXT | 格付コード（要コード表） | G3 |
| RaceInfoKubun | TEXT | レース区分（要コード表） | 一般 |
| WeatherCD | TEXT | 天候コード（要コード表） | 1 |
| BabaCD | TEXT | 馬場状態コード（要コード表） | 1 |

### entries（出走馬 / SE）

| 列名 | 型 | 説明 | 例 |
|---|---|---|---|
| RaceKey | TEXT | レースキー | 202409070811 |
| Umaban | INTEGER | 馬番 | 7 |
| Wakuban | INTEGER | 枠番 | 4 |
| HorseID | TEXT | 馬ID | 2018100012 |
| UmaName | TEXT | 馬名 | サンプルホース |
| SexCD | TEXT | 性別コード（codes.sex を参照） | 2 |
| Age | INTEGER | 年齢 | 4 |
| Jockey | TEXT | 騎手名 | サンプル太郎 |
| BurdenWeight | REAL | 斤量(kg) | 55.0 |
| Kyakusitsu | TEXT | 脚質コード（codes.kyakusitsu を参照） | 3 |

### odds（オッズ / O1, O2等）

| 列名 | 型 | 説明 | 例 |
|---|---|---|---|
| RaceKey | TEXT | レースキー | 202409070811 |
| Umaban | INTEGER | 馬番 | 7 |
| TanshoRaw | TEXT | 生オッズ（4桁固定） | 0024 |
| Tansho | REAL | 変換済みオッズ（`TanshoRaw`/10） | 2.4 |
| Ninki | INTEGER | 人気 | 1 |
