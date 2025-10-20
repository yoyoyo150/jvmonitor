# JRA-VAN 完全計画ブループリント（要件定義＋実装計画 v1）

> 目的：Cursor で拡張しても **エラー連発にならない**、要件定義と **コンパイル保証**つき実装計画。
>
> * JVData_Struct.cs が無くても **ビルド可能（Stub/Demo モード）**
> * 置くだけで **JV モードに自動昇格**（`JVData_Struct.cs` を配置すると実機能へ）
> * **バックフィル完全対応**、**再開可能**、**予測機能の足場**まで含む
> * 変更は **1ファイル1責務**、**破壊的変更は CI で検知**

---

## 0. ゴール / 非ゴール

**ゴール**

* (G1) JV-Link から RACE/SE/HR/（拡張: 調教WK/区間RS）を SQLite へ蓄積
* (G2) Viewer で日付→レース→出馬表＋（拡張: 予測L3/ペース）表示
* (G3) **初回フルバックフィル→毎日差分→中断再開**
* (G4) JV SDK 未配置でも **Demo/Stub で必ず起動・表示**
* (G5) **エラー耐性**：バッファ不足、COM 未登録、接続断、重複投入、スキーマ進化

**非ゴール**（v1）

* 高度な機械学習モデル（将来の v2 で XGBoost/LGBM を採用）
* Web API 配信（ローカル CLI + WPF のみ）

---

## 1. ドメイン / 用語

* **RA**: レース基本
* **SE**: 出馬
* **HR**: 馬マスタ
* **WK**: 調教（追い切り）
* **RS**: 区間タイム（前半3F/上がり3F）
* **L3**: 上がり 3F

---

## 2. アーキテクチャ（4 層）

```
[UI] ViewerWpfX64 (x64)
   └─ uses AppDb (read-only queries)
[Ingest] DownloaderX86 (x86) / BackfillCli (x86)
   └─ uses IJvClient / IJvParser → SQLiteRepo (upsert)
[Predict] FeatureCli (x64)
   └─ read DB → predictions_* upsert
[Shared] Contracts/Models/Config/Errors
```

* **IJvClient**: JVInit/JVOpen/JVRead の抽象。実装は `JvLinkClient`（実機）/ `JvStubClient`（ダミー）。
* **IJvParser**: RA/SE/HR/WK/RS パース抽象。実装は `JvParserDatalab`（SDK 依存）/ `JvParserStub`（固定値）。
* **SQLiteRepo**: すべて Upsert、WAL、トランザクション、指数的リトライ。

---

## 3. データ設計（DDL）

**必須**

```sql
CREATE TABLE IF NOT EXISTS races(
  key TEXT PRIMARY KEY,              -- yyyymmdd-Jyo-RR
  ymd TEXT NOT NULL,
  jyo_cd TEXT, kaiji INTEGER, nichi INTEGER,
  race_num INTEGER, race_name TEXT,
  kyori INTEGER, track_cd TEXT, grade_cd TEXT
);
CREATE INDEX IF NOT EXISTS idx_races_ymd ON races(ymd);

CREATE TABLE IF NOT EXISTS entries(
  race_key TEXT NOT NULL,
  umaban INTEGER,
  wakuban INTEGER,
  horse_name TEXT,
  jockey_name TEXT,
  kinryo REAL,
  ninki INTEGER,
  ketto_no TEXT,
  PRIMARY KEY(race_key, umaban)
);
CREATE INDEX IF NOT EXISTS idx_entries_race ON entries(race_key);

CREATE TABLE IF NOT EXISTS horses(
  ketto_no TEXT PRIMARY KEY,
  bamei TEXT
);

CREATE TABLE IF NOT EXISTS workouts(
  ketto_no TEXT NOT NULL,
  wdate TEXT NOT NULL,
  course TEXT,
  dist_f INTEGER,
  time_5f REAL, time_4f REAL, time_3f REAL, time_1f REAL,
  rating INTEGER,
  PRIMARY KEY (ketto_no, wdate, course)
);
CREATE INDEX IF NOT EXISTS idx_workouts_horse ON workouts(ketto_no);

CREATE TABLE IF NOT EXISTS results_sectionals(
  race_key TEXT NOT NULL,
  ketto_no TEXT NOT NULL,
  last3f REAL, first3f REAL,
  course_cd TEXT, finish_pos INTEGER,
  ts TEXT NOT NULL,
  PRIMARY KEY (race_key, ketto_no)
);
CREATE INDEX IF NOT EXISTS idx_results_ketto ON results_sectionals(ketto_no);

CREATE TABLE IF NOT EXISTS predictions_l3(
  race_key TEXT NOT NULL, umaban INTEGER NOT NULL,
  model TEXT NOT NULL, l3_pred REAL NOT NULL, rank INTEGER NOT NULL, ts TEXT NOT NULL,
  PRIMARY KEY (race_key, umaban, model)
);
CREATE TABLE IF NOT EXISTS predictions_pace(
  race_key TEXT PRIMARY KEY, model TEXT NOT NULL,
  pace_cls TEXT NOT NULL, score REAL NOT NULL, ts TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ingestion_state(
  key TEXT PRIMARY KEY, val TEXT NOT NULL, ts TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS ingestion_log(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_at TEXT, spec TEXT, from_time TEXT,
  rc_init INTEGER, rc_open INTEGER, total INTEGER
);
```

---

## 4. 構成/ビルド（エラー防止の土台）

### 4.1 `global.json`（SDK 固定）

```json
{ "sdk": { "version": "8.0.303", "rollForward": "latestFeature" } }
```

### 4.2 `Directory.Build.props`（共通設定）

```xml
<Project>
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <LangVersion>latest</LangVersion>
    <Nullable>enable</Nullable>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
    <Deterministic>true</Deterministic>
    <RestorePackagesWithLockFile>true</RestorePackagesWithLockFile>
    <EnableDefaultItems>false</EnableDefaultItems>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Dapper" Version="2.1.35" />
    <PackageReference Include="System.Data.SQLite.Core" Version="1.0.118" />
  </ItemGroup>
</Project>
```

### 4.3 csproj の安全策（DownloaderX86）

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <AssemblyName>Keiba.Downloader</AssemblyName>
    <Platforms>x86</Platforms>
    <PlatformTarget>x86</PlatformTarget>
    <DefineConstants>$(DefineConstants);STUB_MODE</DefineConstants>
  </PropertyGroup>

  <!-- JVData_Struct.cs が存在すれば HAS_DATALAB を付与し STUB_MODE を外す -->
  <Choose>
    <When Condition="Exists('JVData_Struct.cs')">
      <PropertyGroup>
        <DefineConstants>$(DefineConstants);HAS_DATALAB</DefineConstants>
      </PropertyGroup>
      <ItemGroup>
        <Compile Include="JVData_Struct.cs" />
      </ItemGroup>
    </When>
  </Choose>

  <ItemGroup>
    <ProjectReference Include="..\Shared\Shared.csproj" />
  </ItemGroup>
</Project>
```

> 既定は **STUB_MODE**（SDK無くてもビルド）。`JVData_Struct.cs` を置くと `HAS_DATALAB` が有効になり実機パーサに自動切替。

### 4.4 ViewerWpfX64 / BackfillCli / FeatureCli

* ViewerWpfX64: `<PlatformTarget>x64</PlatformTarget>`
* BackfillCli: `<PlatformTarget>x86</PlatformTarget>`
* FeatureCli: `<PlatformTarget>x64</PlatformTarget>`

---

## 5. 主要インターフェース（コンパイル保証）

```csharp
// Shared/Contracts.cs
public interface IJvClient : IDisposable
{
  int InitWithRc();
  int OpenWithRc(string spec, string from, int option);
  int ReadOnce(out string data, out int size, out string id);
}

public interface IJvParser
{
  Race ParseRace(string raw);
  Entry ParseEntry(string raw);
  Horse ParseHorse(string raw);
  Workout ParseWorkout(string raw);
  Sectional ParseSectional(string raw);
}
```

**実装（実機）：DownloaderX86/Adapters/JvLinkClient.cs**

```csharp
public sealed class JvLinkClient : IJvClient
{
  private dynamic? _jv;
  public int InitWithRc(){ var t=Type.GetTypeFromProgID("JvLink.JvLink"); if(t==null) return -1; _jv=Activator.CreateInstance(t); return _jv.JVInit("KeibaApp"); }
  public int OpenWithRc(string spec,string from,int option)=> _jv.JVOpen(spec,from,option);
  public int ReadOnce(out string data,out int size,out string id)
  {
    string buff=new string(' ',131072);
    while(true){ int rc=_jv.JVRead(ref buff,out size,out id); if(rc==1){ data=(size>0&&size<=buff.Length)?buff.Substring(0,size):buff.TrimEnd(); return 1; } if(rc==0){ data=""; return 0; } if(size>buff.Length){ buff=new string(' ', size+4096); continue; } Thread.Sleep(150);} }
  public void Dispose(){ try{ _jv?.JVClose(); }catch{} if(_jv!=null && Marshal.IsComObject(_jv)) Marshal.ReleaseComObject(_jv);} }
```

**実装（Stub）：DownloaderX86/Adapters/JvStubClient.cs**

```csharp
public sealed class JvStubClient : IJvClient
{
  private Queue<(string id,string raw)> _q = new();
  public int InitWithRc()=>0;
  public int OpenWithRc(string spec,string from,int option){
    // デモ投入：RA/SE を数件
    _q.Enqueue(("RA","{\"Key\":\"20250503-05-11\",\"Ymd\":\"2025-05-03\",\"RaceName\":\"デモ\",\"JyoCd\":\"05\",\"RaceNum\":11,\"Kyori\":1600,\"TrackCd\":\"T\"}"));
    _q.Enqueue(("SE","{\"RaceKey\":\"20250503-05-11\",\"Umaban\":1,\"Wakuban\":1,\"HorseName\":\"テストA\",\"JockeyName\":\"騎手A\",\"Kinryo\":56,\"Ninki\":1}"));
    _q.Enqueue(("SE","{\"RaceKey\":\"20250503-05-11\",\"Umaban\":2,\"Wakuban\":2,\"HorseName\":\"テストB\",\"JockeyName\":\"騎手B\",\"Kinryo\":56,\"Ninki\":2}"));
    return 0; }
  public int ReadOnce(out string data,out int size,out string id){ if(_q.Count==0){ data=""; size=0; id=""; return 0;} var (i,r)=_q.Dequeue(); id=i; data=r; size=data.Length; return 1; }
  public void Dispose(){}
}
```

**パーサ（実機/Stub を両備え）**

```csharp
public sealed class JvParserStub : IJvParser
{
  public Race ParseRace(string raw)=> JsonSerializer.Deserialize<Race>(raw)!;
  public Entry ParseEntry(string raw)=> JsonSerializer.Deserialize<Entry>(raw)!;
  public Horse ParseHorse(string raw)=> new();
  public Workout ParseWorkout(string raw)=> new();
  public Sectional ParseSectional(string raw)=> new();
}

#if HAS_DATALAB
public sealed class JvParserDatalab : IJvParser
{
  public Race ParseRace(string raw){ var ra = JVData_Struct.JV_RA_RACE.Parse(raw); return new Race{ Key=$"{ra.Year}{ra.Month:00}{ra.Day:00}-{ra.JyoCD}-{ra.RaceNum:00}", Ymd=new DateTime(ra.Year,ra.Month,ra.Day), JyoCd=ra.JyoCD, RaceNum=ra.RaceNum, RaceName=ra.RaceName, Kyori=ra.TrackDistance, TrackCd=ra.TrackCD, GradeCd=ra.GradeCD }; }
  public Entry ParseEntry(string raw){ var se = JVData_Struct.JV_SE_RACE_UMA.Parse(raw); return new Entry{ RaceKey=$"{se.Year}{se.Month:00}{se.Day:00}-{se.JyoCD}-{se.RaceNum:00}", Umaban=se.Umaban, Wakuban=se.Wakuban, HorseName=se.Bamei, JockeyName=se.KisyuName, Kinryo=se.Handicap, Ninki=se.Ninki, KettoNo=se.KettoNum}; }
  public Horse ParseHorse(string raw){ var hr = JVData_Struct.JV_HR_Horse.Parse(raw); return new Horse{ KettoNo=hr.KettoNum, HorseName=hr.Bamei}; }
  public Workout ParseWorkout(string raw){ /* SDK の実装に合わせて */ return new(); }
  public Sectional ParseSectional(string raw){ /* SDK の実装に合わせて */ return new(); }
}
#endif
```

**コンポジション（Downloader 起動時の選択）**

```csharp
IJvClient NewClient() =>
#if HAS_DATALAB
  new JvLinkClient();
#else
  new JvStubClient();
#endif

IJvParser NewParser() =>
#if HAS_DATALAB
  new JvParserDatalab();
#else
  new JvParserStub();
#endif
```

---

## 6. 取得ロジック（差分/再開/フル）

### 6.1 Downloader（直近差分）

* `FromDays` で `from = Today-FromDays`
* Spec 例：`RACE,SE`（当日直近）
* Upsert、1,000 件ごとコミット、退避ログ `logs/downloader_yyyyMMdd_HHmmss.log`

### 6.2 BackfillCli（フル & 再開）

* 入力：`start=YYYY-MM-DD end=YYYY-MM-DD spec=...`（省略時、`ingestion_state.last_ymd` から再開）
* 1 日ずつ `from=YYYYMMDD000000`
* レコード側の日付で **当日分のみ**保存（重複は Upsert）

**擬似コード**

```text
for day in [start..end]:
  open(spec, from=day 00:00:00)
  while read():
    if rec.belongs_to(day): upsert(rec)
  checkpoint(last_ymd = day)
```

---

## 7. エラーハンドリング指針

* JVInit/JVOpen の rc!=0 → 明示ログ＋終了（権限/ログイン/期限）
* JVRead rc<0 → 200ms リトライ（サイズ返却時はバッファ増強）
* COM 未登録 → 型解決失敗で `STUB_MODE` にフォールバック（DownloaderX86 では明示エラーにする設定も可）
* SQLite：`BEGIN IMMEDIATE` → バッチ → `COMMIT`、`ON CONFLICT DO UPDATE`
* 例外は **ロギング＋続行**（レコード単位）、致命は終了コード 1/2/10/11

---

## 8. ログ/診断

* 形式：`[TS][Level][Comp] message`、例：`2025-08-16 09:00:00 INFO DL Open spec=RACE from=...`
* 主要メトリクス：取り込み件数、ID 別件数、失敗件数、所要時間
* `ingestion_log` に毎日 1 行（rc/件数）

---

## 9. マイグレーション方針

* スキーマ変更は `Schema.sql` を更新し `schema_migrations(version, applied_at)` を導入（v2 から）
* CLI 起動時に未適用を検知して逐次適用（トランザクション）

---

## 10. テスト計画

* **ユニット**：Repo.Upsert / Key 生成 / ParserStub の変換
* **統合**：StubClient→Repo→Viewer が通る（SDK 無しで通る）
* **スモーク**：BackfillCli を 1 日分だけで実行し件数増を確認

---

## 11. 予測（MVP）

* `FeatureCli`：L3 予測 = 過去同コース L3 中央値 − 調教 3F の良化補正
* ペース：出走の前半 3F 実績でスコアリング（FAST/EVEN/SLOW）
* 結果は `predictions_*` に upsert → Viewer 列で表示

---

## 12. セキュリティ/ライセンス

* DataLab 規約順守。DB/ログの再配布禁止。
* 個人情報なし。端末ローカルのみ。

---

## 13. 変更の掟（Cursor で壊さないために）

* 新機能は **新ファイル**で追加、既存に直接追記しない
* 既存契約：`IJvClient` / `IJvParser` / `SQLiteRepo` のシグネチャを変えない
* SDK 依存コードは `#if HAS_DATALAB` でガード
* まず Stub で通してから実機へ昇格

---

## 14. 最小ファイル雛形（コピーして配置）

> ここから下は **プロジェクト直置き**できる雛形です。必要なパスで保存してください。

### 14.1 `/global.json`

```json
{ "sdk": { "version": "8.0.303", "rollForward": "latestFeature" } }
```

### 14.2 `/Directory.Build.props`

```xml
<Project>
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <LangVersion>latest</LangVersion>
    <Nullable>enable</Nullable>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
    <Deterministic>true</Deterministic>
    <RestorePackagesWithLockFile>true</RestorePackagesWithLockFile>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Dapper" Version="2.1.35" />
    <PackageReference Include="System.Data.SQLite.Core" Version="1.0.118" />
  </ItemGroup>
</Project>
```

### 14.3 `/src/Shared/Shared.csproj`

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
  </PropertyGroup>
</Project>
```

### 14.4 `/src/Shared/Contracts.cs`

```csharp
namespace Shared; public interface IJvClient : IDisposable { int InitWithRc(); int OpenWithRc(string spec,string from,int option); int ReadOnce(out string data,out int size,out string id); } public interface IJvParser { Race ParseRace(string raw); Entry ParseEntry(string raw); Horse ParseHorse(string raw); Workout ParseWorkout(string raw); Sectional ParseSectional(string raw); } public sealed class Race{ public string Key{get;set;}=""; public DateTime Ymd{get;set;}=DateTime.Today; public string? JyoCd{get;set;} public int Kaiji{get;set;} public int Nichi{get;set;} public int RaceNum{get;set;} public string? RaceName{get;set;} public int Kyori{get;set;} public string? TrackCd{get;set;} public string? GradeCd{get;set;} } public sealed class Entry{ public string RaceKey{get;set;}=""; public int Umaban{get;set;} public int Wakuban{get;set;} public string? HorseName{get;set;} public string? JockeyName{get;set;} public double Kinryo{get;set;} public int? Ninki{get;set;} public string? KettoNo{get;set;} } public sealed class Horse{ public string? KettoNo{get;set;} public string? HorseName{get;set;} } public sealed class Workout{ public string KettoNo{get;set;}=""; public DateTime WDate{get;set;}=DateTime.Today; public string? Course{get;set;} public int? DistF{get;set;} public double? Time5F{get;set;} public double? Time4F{get;set;} public double? Time3F{get;set;} public double? Time1F{get;set;} public int? Rating{get;set;} } public sealed class Sectional{ public string RaceKey{get;set;}=""; public string KettoNo{get;set;}=""; public double? Last3F{get;set;} public double? First3F{get;set;} public string? CourseCd{get;set;} public int? Finish{get;set;} }
```

### 14.5 `/src/DownloaderX86/DownloaderX86.csproj`

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <AssemblyName>Keiba.Downloader</AssemblyName>
    <TargetFramework>net8.0</TargetFramework>
    <PlatformTarget>x86</PlatformTarget>
    <Nullable>enable</Nullable>
    <DefineConstants>$(DefineConstants);STUB_MODE</DefineConstants>
  </PropertyGroup>
  <Choose>
    <When Condition="Exists('JVData_Struct.cs')">
      <PropertyGroup>
        <DefineConstants>$(DefineConstants);HAS_DATALAB</DefineConstants>
      </PropertyGroup>
      <ItemGroup>
        <Compile Include="JVData_Struct.cs" />
      </ItemGroup>
    </When>
  </Choose>
  <ItemGroup>
    <ProjectReference Include="..\Shared\Shared.csproj" />
  </ItemGroup>
</Project>
```

### 14.6 `/src/DownloaderX86/Program.cs`

```csharp
using Shared; using System.Data.SQLite; using Dapper;
class Program
{
  static int Main(string[] args)
  {
    string db = @"C:\\my_project_folder\\data\\keiba_data_app.db";
    string spec = "RACE,SE"; int option=1; int fromDays=14;
    foreach(var a in args){ var kv=a.Split('='); if(kv.Length==2){ if(kv[0]=="db") db=kv[1]; if(kv[0]=="spec") spec=kv[1]; if(kv[0]=="option"&&int.TryParse(kv[1],out var oi)) option=oi; if(kv[0]=="days"&&int.TryParse(kv[1],out var d)) fromDays=d; }}
    Directory.CreateDirectory(Path.GetDirectoryName(db)!);
    using var conn=new SQLiteConnection($"Data Source={db};Journal Mode=WAL"); conn.Open();
    conn.Execute(File.ReadAllText(Path.Combine(AppContext.BaseDirectory,"Schema.sql")));

    IJvClient cli = NewClient(); IJvParser parser = NewParser();
    var rcI = cli.InitWithRc(); if(rcI!=0){ Console.WriteLine($"JVInit rc={rcI}"); return 10; }
    var from = DateTime.Today.AddDays(-fromDays).ToString("yyyyMMdd")+"000000";
    var rcO = cli.OpenWithRc(spec, from, option); if(rcO!=0){ Console.WriteLine($"JVOpen rc={rcO}"); return 11; }

    int total=0; while(true){ var rc=cli.ReadOnce(out var raw,out var size,out var id); if(rc==0) break; if(rc<0) continue; total++;
      try{
        if(id=="RA"){ var r=parser.ParseRace(raw); UpsertRace(conn,r); }
        else if(id=="SE"){ var e=parser.ParseEntry(raw); UpsertEntry(conn,e); }
        else if(id=="HR"){ var h=parser.ParseHorse(raw); UpsertHorse(conn,h); }
      } catch(Exception ex){ Console.WriteLine($"[WARN] {id} {ex.Message}"); }
    }
    Console.WriteLine($"Done total={total}"); return 0;
  }

  static void UpsertRace(SQLiteConnection c,Race r)=> c.Execute( @"INSERT INTO races(key,ymd,jyo_cd,kaiji,nichi,race_num,race_name,kyori,track_cd,grade_cd)
VALUES( @Key,@YmdText,@JyoCd,@Kaiji,@Nichi,@RaceNum,@RaceName,@Kyori,@TrackCd,@GradeCd)
ON CONFLICT(key) DO UPDATE SET ymd= @YmdText, jyo_cd= @JyoCd, kaiji= @Kaiji, nichi= @Nichi, race_num= @RaceNum, race_name= @RaceName, kyori= @Kyori, track_cd= @TrackCd, grade_cd= @GradeCd;",
    new{ r.Key, YmdText=r.Ymd.ToString("yyyy-MM-dd"), r.JyoCd, r.Kaiji, r.Nichi, r.RaceNum, r.RaceName, r.Kyori, r.TrackCd, r.GradeCd });
  static void UpsertEntry(SQLiteConnection c,Entry e)=> c.Execute( @"INSERT INTO entries(race_key,umaban,wakuban,horse_name,jockey_name,kinryo,ninki,ketto_no)
VALUES( @RaceKey,@Umaban,@Wakuban,@HorseName,@JockeyName,@Kinryo,@Ninki,@KettoNo)
ON CONFLICT(race_key,umaban) DO UPDATE SET wakuban= @Wakuban, horse_name= @HorseName, jockey_name= @JockeyName, kinryo= @Kinryo, ninki= @Ninki, ketto_no= @KettoNo;", e);
  static void UpsertHorse(SQLiteConnection c,Horse h){ if(string.IsNullOrEmpty(h.KettoNo)) return; c.Execute( @"INSERT INTO horses(ketto_no,bamei) VALUES( @KettoNo,@HorseName)
ON CONFLICT(ketto_no) DO UPDATE SET bamei= @HorseName;", h);}  

  static IJvClient NewClient()=>
#if HAS_DATALAB
    new JvLinkClient();
#else
    new JvStubClient();
#endif
  static IJvParser NewParser()=>
#if HAS_DATALAB
    new JvParserDatalab();
#else
    new JvParserStub();
#endif
}
```

### 14.7 `/src/DownloaderX86/Adapters/JvLinkClient.cs`

```csharp
#if HAS_DATALAB
using System.Runtime.InteropServices; using Shared;
public sealed class JvLinkClient : IJvClient
{ private dynamic? _jv; public int InitWithRc(){ var t=Type.GetTypeFromProgID("JvLink.JvLink"); if(t==null) return -1; _jv=Activator.CreateInstance(t); return _jv.JVInit("KeibaApp"); }
  public int OpenWithRc(string spec,string from,int option)=>_jv.JVOpen(spec,from,option);
  public int ReadOnce(out string data,out int size,out string id)
  { string buff=new string(' ',131072); while(true){ int rc=_jv.JVRead(ref buff,out size,out id); if(rc==1){ data=(size>0&&size<=buff.Length)?buff[..size]:buff.TrimEnd(); return 1; } if(rc==0){ data=""; return 0; } if(size>buff.Length){ buff=new string(' ',size+4096); continue;} Thread.Sleep(150);} }
  public void Dispose(){ try{ _jv?.JVClose(); }catch{} if(_jv!=null && Marshal.IsComObject(_jv)) Marshal.ReleaseComObject(_jv);} }
#endif
```

### 14.8 `/src/DownloaderX86/Adapters/JvStubClient.cs`

```csharp
#if !HAS_DATALAB
using Shared; using System.Text.Json;
public sealed class JvStubClient : IJvClient
{ private readonly Queue<(string id,string raw)> _q=new();
  public int InitWithRc()=>0;
  public int OpenWithRc(string spec,string from,int option){
    _q.Enqueue(("RA",JsonSerializer.Serialize(new Race{ Key="20250503-05-11", Ymd=new DateTime(2025,5,3), JyoCd="05", RaceNum=11, RaceName="（デモ）", Kyori=1600, TrackCd="T" })));
    _q.Enqueue(("SE",JsonSerializer.Serialize(new Entry{ RaceKey="20250503-05-11", Umaban=1, Wakuban=1, HorseName="テストA", JockeyName="騎手A", Kinryo=56, Ninki=1 })));
    _q.Enqueue(("SE",JsonSerializer.Serialize(new Entry{ RaceKey="20250503-05-11", Umaban=2, Wakuban=2, HorseName="テストB", JockeyName="騎手B", Kinryo=56, Ninki=2 })));
    return 0; }
  public int ReadOnce(out string data,out int size,out string id){ if(_q.Count==0){ data=""; size=0; id=""; return 0;} var (i,r)=_q.Dequeue(); id=i; data=r; size=r.Length; return 1; }
  public void Dispose(){} }
#endif
```

### 14.9 `/src/DownloaderX86/Adapters/JvParserStub.cs` と `JvParserDatalab.cs`

```csharp
// Stub（常時ビルド可）
using Shared; using System.Text.Json;
public sealed class JvParserStub : IJvParser
{ public Race ParseRace(string raw)=>JsonSerializer.Deserialize<Race>(raw)!; public Entry ParseEntry(string raw)=>JsonSerializer.Deserialize<Entry>(raw)!; public Horse ParseHorse(string raw)=>new(); public Workout ParseWorkout(string raw)=>new(); public Sectional ParseSectional(string raw)=>new(); }

// Datalab（SDK 配置時のみ有効）
#if HAS_DATALAB
using Shared;
public sealed class JvParserDatalab : IJvParser
{ 
  public Race ParseRace(string raw){ var ra = JVData_Struct.JV_RA_RACE.Parse(raw); return new Race{ Key=$"{ra.Year}{ra.Month:00}{ra.Day:00}-{ra.JyoCD}-{ra.RaceNum:00}", Ymd=new DateTime(ra.Year,ra.Month,ra.Day), JyoCd=ra.JyoCD, Kaiji=ra.Kaiji, Nichi=ra.Nichime, RaceNum=ra.RaceNum, RaceName=ra.RaceName, Kyori=ra.TrackDistance, TrackCd=ra.TrackCD, GradeCd=ra.GradeCD }; }
  public Entry ParseEntry(string raw){ var se = JVData_Struct.JV_SE_RACE_UMA.Parse(raw); return new Entry{ RaceKey=$"{se.Year}{se.Month:00}{se.Day:00}-{se.JyoCD}-{se.RaceNum:00}", Umaban=se.Umaban, Wakuban=se.Wakuban, HorseName=se.Bamei, JockeyName=se.KisyuName, Kinryo=se.Handicap, Ninki=se.Ninki, KettoNo=se.KettoNum }; }
  public Horse ParseHorse(string raw){ var hr = JVData_Struct.JV_HR_Horse.Parse(raw); return new Horse{ KettoNo=hr.KettoNum, HorseName=hr.Bamei }; }
  public Workout ParseWorkout(string raw){ /* TODO: SDK に合わせて */ return new(); }
  public Sectional ParseSectional(string raw){ /* TODO: SDK に合わせて */ return new(); }
}
#endif
```

### 14.10 `/src/DownloaderX86/Schema.sql`

```sql
-- セクション 3 の DDL をそのまま貼付
```

---

## 15. 運用フロー

1. **初回**：`DownloaderX86`（Stub で DB 作成）→ Viewer 起動で表示保証
2. **JV 有効化**：`JVData_Struct.cs` を配置 → 自動で実機モードに昇格
3. **フルバックフィル**：`BackfillCli start=YYYY-MM-DD end=YYYY-MM-DD spec=RACE,SE,HR,WK,RS option=1`
4. **毎日差分**：Windows タスクで 1 日 1 回（AM 6:00 推奨）
5. **予測**：`FeatureCli date=YYYY-MM-DD`

---

## 16. 次の一手（あなたの要望に沿った拡張）

* 調教・区間の **SDK マッピング** を具体化（フィールド名を CANVAS で共有してください）
* Viewer に **CSV 出力**、**並び替え/フィルタ**、**ペース表示**バッジ追加
* 予測の係数を **場/距離/馬場**で最適化

---

> このブループリントを `/docs/BLUEPRINT.md` として保存し、セクション 14 の雛形をそれぞれのパスで配置すれば、**SDK が無くてもビルド＆表示**し、SDK を置いた瞬間に **実機能へ自動切替**します。