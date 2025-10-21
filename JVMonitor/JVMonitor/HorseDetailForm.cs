using System;
using System.Collections.Generic;
using System.Data;
using System.Data.SQLite;
using System.Drawing;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using OfficeOpenXml;

namespace JVMonitor
{
    public partial class HorseDetailForm : Form
    {
        private sealed class HorseMarksResult
        {
            public Dictionary<string, string> Marks { get; } = new();
            public string? RaceId { get; set; }
            public string? MorningOdds { get; set; }
            public string? SourceFile { get; set; }
            public string Message { get; set; } = string.Empty;
            public bool HasData => Marks.Count > 0 || !string.IsNullOrEmpty(MorningOdds);
            
            public string? Mark1 { get; set; }
            public string? Mark2 { get; set; }
            public string? Mark3 { get; set; }
            public string? Mark4 { get; set; }
            public string? Mark5 { get; set; }
            public string? Mark6 { get; set; }
            public string? Mark7 { get; set; }
            public string? Mark8 { get; set; }

            public string? ZI_INDEX { get; set; }
            public string? ZM_VALUE { get; set; }
            public string? ZI_RANK { get; set; } // ZI指数の順位

            public string? SHIBA_DA { get; set; }
            public string? KYORI_M { get; set; }
            public string? R_MARK1 { get; set; }
            public string? R_MARK2 { get; set; }
            public string? R_MARK3 { get; set; }
            public string? RACE_CLASS_C { get; set; }
            public string? CHAKU { get; set; }
            public string? SEX { get; set; }
            public string? AGE { get; set; }
            public string? JOCKEY { get; set; }
            public string? KINRYO { get; set; }
            public string? PREV_KYAKUSHITSU { get; set; }
            public string? PREV_MARK1 { get; set; }
            public string? PREV_MARK2 { get; set; }
            public string? PREV_MARK3 { get; set; }
            public string? PREV_MARK4 { get; set; }
            public string? PREV_MARK5 { get; set; }
            public string? PREV_MARK6 { get; set; }
            public string? PREV_MARK7 { get; set; }
            public string? PREV_MARK8 { get; set; }
            public string? PREV_NINKI { get; set; }
            public string? INDEX_RANK1 { get; set; }
            public string? ACCEL_VAL { get; set; }
            public string? INDEX_RANK2 { get; set; }
            public string? INDEX_DIFF2 { get; set; }
            public string? ORIGINAL_VAL { get; set; }
            public string? INDEX_RANK3 { get; set; }
            public string? INDEX_RANK4 { get; set; }
            public string? PREV_CHAKU_JUNI { get; set; }
            public string? PREV_CHAKU_SA { get; set; }
            public string? TANSHO_ODDS { get; set; }
            public string? FUKUSHO_ODDS { get; set; }
            public string? INDEX_DIFF4 { get; set; }
            public string? INDEX_DIFF1 { get; set; }
            public string? PREV_TSUKA1 { get; set; }
            public string? PREV_TSUKA2 { get; set; }
            public string? PREV_TSUKA3 { get; set; }
            public string? PREV_TSUKA4 { get; set; }
            public string? PREV_3F_JUNI { get; set; }
            public string? PREV_TOSU { get; set; }
            public string? PREV_RACE_MARK { get; set; }
            public string? PREV_RACE_MARK2 { get; set; }
            public string? PREV_RACE_MARK3 { get; set; }
            public string? FATHER_TYPE_NAME { get; set; }
            public string? TOTAL_HORSES { get; set; }
            public string? WORK1 { get; set; }
            public string? WORK2 { get; set; }
            public string? PREV_TRACK_NAME { get; set; }
            public string? SAME_TRACK_FLAG { get; set; }
            public string? PREV_KINRYO { get; set; }
            public string? PREV_BATAIJU { get; set; }
            public string? PREV_BATAIJU_ZOGEN { get; set; }
            public string? AGE_AT_RACE { get; set; }
            public string? INTERVAL { get; set; }
            public string? KYUMEI_SENME { get; set; }
            public string? KINRYO_SA { get; set; }
            public string? KYORI_SA { get; set; }
            public string? PREV_SHIBA_DA { get; set; }
            public string? PREV_KYORI_M { get; set; }
            public string? CAREER_TOTAL { get; set; }
            public string? CAREER_LATEST { get; set; }
            public string? CLASS_C { get; set; }
            public string? PREV_UMABAN { get; set; }
            public string? CURRENT_SHIBA_DA { get; set; }
            public string? PREV_BABA_JOTAI { get; set; }
            public string? PREV_CLASS { get; set; }
            public string? DAMSIRE_TYPE_NAME { get; set; }
            public string? T_MARK_DIFF { get; set; }
            public string? MATCHUP_MINING_VAL { get; set; }
            public string? MATCHUP_MINING_RANK { get; set; }
            public string? KOKYUSEN_FLAG { get; set; }
            public string? B_COL_FLAG { get; set; }
            public string? SYOZOKU { get; set; }
            public string? CHECK_TRAINER_TYPE { get; set; }
            public string? CHECK_JOCKEY_TYPE { get; set; }
            public string? TRAINER_NAME { get; set; }
            public string? FUKUSHO_ODDS_LOWER { get; set; }
            public string? FUKUSHO_ODDS_UPPER { get; set; }
            public string? TAN_ODDS { get; set; }
            public string? WAKUBAN { get; set; }
            public string? COURSE_GROUP_COUNT { get; set; }
            public string? COURSE_GROUP_NAME1 { get; set; }
            public string? NINKI_RANK { get; set; }
            public string? NORIKAE_FLAG { get; set; }
            public string? PREV_RACE_ID { get; set; }

            public string? GetValue(params string[] keys)
            {
                // まず直接プロパティをチェック
                if (keys.Contains("ZI指数の順位") && !string.IsNullOrEmpty(ZI_RANK)) return ZI_RANK;
                if (keys.Contains("ZI順位") && !string.IsNullOrEmpty(ZI_RANK)) return ZI_RANK;
                if (keys.Contains("ZI指数") && !string.IsNullOrEmpty(ZI_INDEX)) return ZI_INDEX;
                if (keys.Contains("ZM") && !string.IsNullOrEmpty(ZM_VALUE)) return ZM_VALUE;
                if (keys.Contains("加速") && !string.IsNullOrEmpty(ACCEL_VAL)) return ACCEL_VAL;
                if (keys.Contains("オリジナル") && !string.IsNullOrEmpty(ORIGINAL_VAL)) return ORIGINAL_VAL;
                if (keys.Contains("単勝予想") && !string.IsNullOrEmpty(TANSHO_ODDS)) return TANSHO_ODDS;
                if (keys.Contains("複勝下限") && !string.IsNullOrEmpty(FUKUSHO_ODDS_LOWER)) return FUKUSHO_ODDS_LOWER;
                if (keys.Contains("複勝上限") && !string.IsNullOrEmpty(FUKUSHO_ODDS_UPPER)) return FUKUSHO_ODDS_UPPER;
                if (keys.Contains("指数差1") && !string.IsNullOrEmpty(INDEX_DIFF1)) return INDEX_DIFF1;
                if (keys.Contains("指数差2") && !string.IsNullOrEmpty(INDEX_DIFF2)) return INDEX_DIFF2;
                if (keys.Contains("指数差4") && !string.IsNullOrEmpty(INDEX_DIFF4)) return INDEX_DIFF4;
                if (keys.Contains("馬印1") && !string.IsNullOrEmpty(Mark1)) return Mark1;
                if (keys.Contains("馬印2") && !string.IsNullOrEmpty(Mark2)) return Mark2;
                if (keys.Contains("馬印3") && !string.IsNullOrEmpty(Mark3)) return Mark3;
                if (keys.Contains("馬印4") && !string.IsNullOrEmpty(Mark4)) return Mark4;
                if (keys.Contains("馬印5") && !string.IsNullOrEmpty(Mark5)) return Mark5;
                if (keys.Contains("馬印6") && !string.IsNullOrEmpty(Mark6)) return Mark6;
                if (keys.Contains("馬印7") && !string.IsNullOrEmpty(Mark7)) return Mark7;
                if (keys.Contains("馬印8") && !string.IsNullOrEmpty(Mark8)) return Mark8;

                // 以前のMarksディクショナリの検索ロジックも残す (互換性のため)
                foreach (var key in keys)
                {
                    if (Marks.TryGetValue(key, out var value) && !string.IsNullOrEmpty(value))
                    {
                        return value;
                    }
                }
                return null;
            }
        }

        // すべてのレースの馬印データを保持するための辞書
        private Dictionary<string, HorseMarksResult> _allHorseMarks = new Dictionary<string, HorseMarksResult>();

        private static string FormatOddsValue(string? raw)
        {
            if (string.IsNullOrWhiteSpace(raw))
            {
                return string.Empty;
            }

            raw = raw.Trim();

            if (double.TryParse(raw, NumberStyles.Float, CultureInfo.InvariantCulture, out var asDouble))
            {
                return asDouble.ToString(asDouble % 1 == 0 ? "0" : "0.0", CultureInfo.InvariantCulture);
            }

            if (raw.All(char.IsDigit) && double.TryParse(raw, NumberStyles.Integer, CultureInfo.InvariantCulture, out var asInt))
            {
                var converted = asInt / 10.0;
                return converted.ToString(converted % 1 == 0 ? "0" : "0.0", CultureInfo.InvariantCulture);
            }

            return raw;
        }

        private static string NormalizeHorseName(string value)
        {
            if (string.IsNullOrEmpty(value))
            {
                return string.Empty;
            }

            var builder = new StringBuilder(value.Length);
            foreach (var c in value)
            {
                if (!char.IsWhiteSpace(c))
                {
                    builder.Append(c);
                }
            }

            return builder.ToString();
        }

        private readonly string _dbPath;
        private readonly string _kettoNum;
        private readonly string _horseName;
        
        private Panel panelTop = null!;
        private Panel panelBottom = null!;
        private Label lblHorseInfo = null!;
        private Label lblBloodline = null!;
        private Label lblMarks = null!;
        private DataGridView gridRaceHistory = null!;
        private Label lblStats = null!;
        private HorseMarksResult? _latestMarks;
        private string _excelDbPath = "";
        private const string ColumnNameMark = "馬印";
        private const string ColumnNameAlgo = "アルゴ";
        private const string ColumnNameZi = "ZI指数";
        private const string ColumnNameZm = "ZM";
        private const string ColumnNameTraining5 = "馬印5";
        private const string ColumnNameTraining6 = "馬印6";
        private const string ColumnNameRawYear = "__RawYear";
        private const string ColumnNameRawMonthDay = "__RawMonthDay";

        private const string HorseMarksTableName = "HORSE_MARKS"; // テーブル名を定数として定義
        
        public HorseDetailForm(string dbPath, string kettoNum, string horseName)
        {
            _dbPath = dbPath;
            _kettoNum = kettoNum;
            _horseName = horseName;
            
            // excel_data.dbのパスを設定（VLOOKUP用）
            // コンストラクタで受け取ったDBパスからディレクトリを取得し、excel_data.dbへのパスを構築する
            if (!string.IsNullOrEmpty(dbPath))
            {
                _excelDbPath = Path.Combine(Path.GetDirectoryName(dbPath) ?? "", "excel_data.db");
            }
            else
            {
                // フォールバックやエラー処理（必要に応じて）
                _excelDbPath = ""; 
            }
            
            InitializeComponent();
            LoadHorseData();
        }
        
        private void InitializeComponent()
        {
            this.Text = $"馬詳細情報 - {_horseName}";
            this.Size = new Size(1200, 800);
            this.StartPosition = FormStartPosition.CenterParent;
            
            // メインパネル（全体レイアウト）
            var mainPanel = new TableLayoutPanel
            {
                Dock = DockStyle.Fill,
                Padding = new Padding(5),
                ColumnCount = 1,
                RowCount = 2,
                RowStyles = { 
                    new RowStyle(SizeType.Absolute, 140),
                    new RowStyle(SizeType.Percent, 100)
                }
            };
            
            // 上部パネル（基本情報・血統・成績）
            panelTop = new TableLayoutPanel
            {
                Dock = DockStyle.Fill,
                ColumnCount = 3,
                RowCount = 1,
                Margin = new Padding(0, 0, 0, 5)
            };
            if (panelTop is TableLayoutPanel panelTopLayout)
            {
                panelTopLayout.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 33.33F));
                panelTopLayout.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 33.33F));
                panelTopLayout.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 33.34F));
            }
            
            // 馬基本情報（左側）
            var horseInfoPanel = new Panel
            {
                Dock = DockStyle.Fill,
                BorderStyle = BorderStyle.FixedSingle,
                BackColor = Color.LightBlue,
                Margin = new Padding(0, 0, 2, 0)
            };
            
            lblHorseInfo = new Label
            {
                Dock = DockStyle.Fill,
                Margin = new Padding(5),
                Font = new Font("Yu Gothic UI", 9.5F, FontStyle.Regular),
                Text = "読み込み中...",
                TextAlign = ContentAlignment.TopLeft,
                AutoSize = false
            };
            horseInfoPanel.Controls.Add(lblHorseInfo);
            
            // 血統情報（中央）
            var bloodlinePanel = new Panel
            {
                Dock = DockStyle.Fill,
                BorderStyle = BorderStyle.FixedSingle,
                BackColor = Color.LightGreen,
                Margin = new Padding(2, 0, 2, 0)
            };
            
            lblBloodline = new Label
            {
                Dock = DockStyle.Fill,
                Margin = new Padding(5),
                Font = new Font("Yu Gothic UI", 9.5F, FontStyle.Regular),
                Text = "血統情報読み込み中...",
                TextAlign = ContentAlignment.TopLeft,
                AutoSize = false
            };
            bloodlinePanel.Controls.Add(lblBloodline);
            
            // 馬印情報はグリッドに表示するため、ラベルのみ保持（非表示）
            lblMarks = new Label { Visible = false };

            // 成績サマリー（右端）
            var statsPanel = new Panel
            {
                Dock = DockStyle.Fill,
                BorderStyle = BorderStyle.FixedSingle,
                BackColor = Color.LightYellow,
                Margin = new Padding(2, 0, 0, 0)
            };
            
            lblStats = new Label
            {
                Dock = DockStyle.Fill,
                Margin = new Padding(5),
                Font = new Font("Yu Gothic UI", 9.5F, FontStyle.Regular),
                Text = "成績サマリー読み込み中...",
                TextAlign = ContentAlignment.TopLeft,
                AutoSize = false
            };
            statsPanel.Controls.Add(lblStats);
            
            if (panelTop is TableLayoutPanel tlp)
            {
                tlp.Controls.Add(horseInfoPanel, 0, 0);
                tlp.Controls.Add(bloodlinePanel, 1, 0);
                tlp.Controls.Add(statsPanel, 2, 0);
            }
            else
            {
                panelTop.Controls.Add(horseInfoPanel);
                panelTop.Controls.Add(bloodlinePanel);
                panelTop.Controls.Add(statsPanel);
            }
            
            // 戦歴パネル（下部）
            panelBottom = new Panel
            {
                Dock = DockStyle.Fill,
                BorderStyle = BorderStyle.FixedSingle
            };
            
            // 戦歴データグリッド
            gridRaceHistory = new DataGridView
            {
                Dock = DockStyle.Fill,
                ReadOnly = true,
                AllowUserToAddRows = false,
                AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.None,
                RowHeadersVisible = false,
                DefaultCellStyle = { Font = new Font("Yu Gothic UI", 9F) },
                ColumnHeadersDefaultCellStyle = { Font = new Font("Yu Gothic UI", 9.5F, FontStyle.Bold) },
                GridColor = Color.LightGray,
                BackgroundColor = Color.White,
                MultiSelect = true,
                SelectionMode = DataGridViewSelectionMode.FullRowSelect,
                AlternatingRowsDefaultCellStyle = { BackColor = Color.WhiteSmoke }
            };
            
            // コンテキストメニューを追加（コピー機能）
            var contextMenu = new ContextMenuStrip();
            var copyItem = new ToolStripMenuItem("コピー (&C)");
            copyItem.Click += CopySelectedRows;
            contextMenu.Items.Add(copyItem);
            gridRaceHistory.ContextMenuStrip = contextMenu;
            
            panelBottom.Controls.Add(gridRaceHistory);
            
            if (mainPanel is TableLayoutPanel mainTlp)
            {
                mainTlp.Controls.Add(panelTop, 0, 0);
                mainTlp.Controls.Add(panelBottom, 0, 1);
            }
            else
            {
                mainPanel.Controls.Add(panelTop);
                mainPanel.Controls.Add(panelBottom);
            }
            this.Controls.Add(mainPanel);
        }
        
        private void LoadHorseData()
        {
            try
            {
                using var conn = new SQLiteConnection($"Data Source={_dbPath};Version=3;");
                conn.Open();
                
                LoadBasicInfo(conn);
                LoadBloodlineInfo(conn);
                LoadRaceHistory(conn);
                LoadStatsInfo(conn);
            }
            catch (Exception ex)
            {
                string errorMessage = $"データ読み込みエラー:\n{ex.Message}\n\nデータベースパス:\n{_dbPath}";
                MessageBox.Show(errorMessage, "エラー", 
                    MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }
        
        private void LoadBasicInfo(SQLiteConnection conn)
        {
            var sql = @"
                SELECT 
                    Bamei, SexCD, BirthDate, KeiroCD, HinsyuCD,
                    ChokyosiRyakusyo, BanusiName
                FROM N_UMA 
                WHERE KettoNum = @kettoNum
                LIMIT 1";
                
            using var cmd = new SQLiteCommand(sql, conn);
            cmd.Parameters.AddWithValue("@kettoNum", _kettoNum);
            
            using var reader = cmd.ExecuteReader();
            if (reader.Read())
            {
                var sex = GetSexName(reader["SexCD"]?.ToString() ?? "");
                var birthDate = reader["BirthDate"]?.ToString() ?? "";
                var age = CalculateAge(birthDate);
                var color = GetColorName(reader["KeiroCD"]?.ToString() ?? "");
                var breed = GetBreedName(reader["HinsyuCD"]?.ToString() ?? "");
                var trainer = reader["ChokyosiRyakusyo"]?.ToString() ?? "";
                var owner = reader["BanusiName"]?.ToString() ?? "";
                
                lblHorseInfo.Text = $"【基本情報】\n" +
                                   $"馬名: {_horseName}\n" +
                                   $"性別: {sex}  年齢: {age}歳\n" +
                                   $"毛色: {color}  品種: {breed}\n" +
                                   $"調教師: {trainer}\n" +
                                   $"馬主: {owner}";
            }
            else
            {
                lblHorseInfo.Text = $"馬名: {_horseName}\n基本情報が見つかりません";
            }
        }
        
        private static bool TableExists(SQLiteConnection cn, string table)
        {
            using var cmd = new SQLiteCommand("SELECT 1 FROM sqlite_master WHERE type IN ('table', 'view') AND name=@n LIMIT 1", cn);
            cmd.Parameters.AddWithValue("@n", table);
            var v = cmd.ExecuteScalar();
            return v != null && v != DBNull.Value;
        }

        private void LoadBloodlineInfo(SQLiteConnection conn)
        {
            string? viewFather = null;
            string? viewMother = null;
            string? viewMotherFather = null;

            // ビューの存在をチェック
            if (TableExists(conn, "BLOODLINE_INFO_VIEW"))
            {
                var sql = @"
                    SELECT 
                        ChichiBamei,
                        HahaBamei,
                        HahaChichiBamei,
                        COALESCE(ChichiBameiDetail, ChichiBamei) as ChichiBameiDetail,
                        COALESCE(HahaBameiDetail, HahaBamei) as HahaBameiDetail,
                        COALESCE(HahaChichiBameiDetail, HahaChichiBamei) as HahaChichiBameiDetail
                    FROM BLOODLINE_INFO_VIEW 
                    WHERE KettoNum = @kettoNum
                    LIMIT 1";

                try
                {
                    using (var cmd = new SQLiteCommand(sql, conn))
                    {
                        cmd.Parameters.AddWithValue("@kettoNum", _kettoNum);
                        using var reader = cmd.ExecuteReader();
                        if (reader.Read())
                        {
                            viewFather = reader["ChichiBameiDetail"]?.ToString();
                            viewMother = reader["HahaBameiDetail"]?.ToString();
                            viewMotherFather = reader["HahaChichiBameiDetail"]?.ToString();
                        }
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"[WARN] BLOODLINE_INFO_VIEWの読み込みに失敗しました: {ex.Message}");
                }
            }

            var (fallbackFather, fallbackMother, fallbackMotherFather) = GetBloodlineNamesFromNuma(conn);

            var father = ChoosePreferredName(viewFather, fallbackFather);
            var mother = ChoosePreferredName(viewMother, fallbackMother);
            var motherFather = ChoosePreferredName(viewMotherFather, fallbackMotherFather);

            if (string.IsNullOrWhiteSpace(father) && string.IsNullOrWhiteSpace(mother) && string.IsNullOrWhiteSpace(motherFather))
            {
                lblBloodline.Text = "血統情報が見つかりません";
                return;
            }

            lblBloodline.Text = $@"【血統情報】
父: {father}
母: {mother}
母父: {motherFather}";
        }

        private (string? Sire, string? Dam, string? DamSire) GetBloodlineNamesFromNuma(SQLiteConnection conn)
        {
            var sql = @"
                SELECT
                    NULLIF(TRIM(Ketto3InfoBamei1), '') AS SireName,
                    NULLIF(TRIM(Ketto3InfoBamei2), '') AS DamName,
                    NULLIF(TRIM(Ketto3InfoBamei5), '') AS DamSireName,
                    NULLIF(TRIM(Ketto3InfoBamei3), '') AS SireSideFallback
                FROM N_UMA 
                WHERE KettoNum = @kettoNum
                LIMIT 1";

            using var cmd = new SQLiteCommand(sql, conn);
            cmd.Parameters.AddWithValue("@kettoNum", _kettoNum);

            using var reader = cmd.ExecuteReader();
            if (reader.Read())
            {
                string? sire = reader["SireName"]?.ToString();
                string? dam = reader["DamName"]?.ToString();
                string? damSire = reader["DamSireName"]?.ToString();
                if (string.IsNullOrWhiteSpace(damSire))
                {
                    damSire = reader["SireSideFallback"]?.ToString();
                }
                return (sire, dam, damSire);
            }

            return (null, null, null);
        }

        private static string ChoosePreferredName(string? primary, string? secondary, string fallback = "不明")
        {
            if (!string.IsNullOrWhiteSpace(primary))
            {
                return primary.Trim();
            }

            if (!string.IsNullOrWhiteSpace(secondary))
            {
                return secondary.Trim();
            }

            return fallback;
        }

        private void LoadAllMarksFromDatabase()
        {
            System.Diagnostics.Debug.WriteLine("LoadAllMarksFromDatabase開始");
            _allHorseMarks.Clear();

            var normalizedHorseName = NormalizeHorseName(_horseName);
            if (string.IsNullOrEmpty(normalizedHorseName))
            {
                System.Diagnostics.Debug.WriteLine("LoadAllMarksFromDatabase: 正規化した馬名が空です。");
                return;
            }

            if (string.IsNullOrEmpty(_excelDbPath) || !File.Exists(_excelDbPath))
            {
                System.Diagnostics.Debug.WriteLine($"LoadAllMarksFromDatabase: excel_data.dbが見つかりません: {_excelDbPath}");
                return;
            }

            try
            {
                using var conn = new SQLiteConnection($"Data Source={_excelDbPath};Version=3;");
                conn.Open();

                var columnsToLoad = new[]
                {
                    "RaceId",
                    "KYORI_M",
                    "R_MARK1", "R_MARK2", "R_MARK3",
                    "Mark1", "Mark2", "Mark3", "Mark4", "Mark5", "Mark6", "Mark7", "Mark8",
                    "PREV_KYAKUSHITSU",
                    "PREV_MARK1", "PREV_MARK2", "PREV_MARK3", "PREV_MARK4", "PREV_MARK5", "PREV_MARK6", "PREV_MARK7", "PREV_MARK8",
                    "PREV_NINKI",
                    "ZI_INDEX", "ZM_VALUE", "ZI_RANK",
                    "ACCEL_VAL", "ORIGINAL_VAL",
                    "INDEX_DIFF1", "INDEX_DIFF2", "INDEX_DIFF4",
                    "INDEX_RANK1", "INDEX_RANK2", "INDEX_RANK3", "INDEX_RANK4",
                    "TAN_ODDS", "TANSHO_ODDS",
                    "FUKUSHO_ODDS_LOWER", "FUKUSHO_ODDS_UPPER",
                    "FUKUSHO_ODDS",
                    "MATCHUP_MINING_VAL", "MATCHUP_MINING_RANK",
                    "DAMSIRE_TYPE_NAME"
                };

                var distinctColumns = columnsToLoad.Distinct(StringComparer.OrdinalIgnoreCase).ToArray();
                var sql = $"SELECT SourceDate, {string.Join(", ", distinctColumns)} FROM {HorseMarksTableName} WHERE NormalizedHorseName = @normalizedHorseName ORDER BY SourceDate DESC, ImportedAt DESC";

                using var cmd = new SQLiteCommand(sql, conn);
                cmd.Parameters.AddWithValue("@normalizedHorseName", normalizedHorseName);

                using var reader = cmd.ExecuteReader();
                var fieldNames = Enumerable.Range(0, reader.FieldCount)
                                           .Select(reader.GetName)
                                           .ToHashSet(StringComparer.OrdinalIgnoreCase);

                while (reader.Read())
                {
                    string? GetValue(string column)
                    {
                        if (!fieldNames.Contains(column))
                        {
                            return null;
                        }

                        var ordinal = reader.GetOrdinal(column);
                        return reader.IsDBNull(ordinal) ? null : reader.GetValue(ordinal)?.ToString();
                    }

                    var sourceDate = GetValue("SourceDate");
                    if (string.IsNullOrWhiteSpace(sourceDate))
                    {
                        continue;
                    }

                    var marksResult = new HorseMarksResult
                    {
                        RaceId = GetValue("RaceId"),
                        KYORI_M = GetValue("KYORI_M"),
                        R_MARK1 = GetValue("R_MARK1"),
                        R_MARK2 = GetValue("R_MARK2"),
                        R_MARK3 = GetValue("R_MARK3"),
                        Mark1 = GetValue("Mark1"),
                        Mark2 = GetValue("Mark2"),
                        Mark3 = GetValue("Mark3"),
                        Mark4 = GetValue("Mark4"),
                        Mark5 = GetValue("Mark5"),
                        Mark6 = GetValue("Mark6"),
                        Mark7 = GetValue("Mark7"),
                        Mark8 = GetValue("Mark8"),
                        PREV_KYAKUSHITSU = GetValue("PREV_KYAKUSHITSU"),
                        PREV_MARK1 = GetValue("PREV_MARK1"),
                        PREV_MARK2 = GetValue("PREV_MARK2"),
                        PREV_MARK3 = GetValue("PREV_MARK3"),
                        PREV_MARK4 = GetValue("PREV_MARK4"),
                        PREV_MARK5 = GetValue("PREV_MARK5"),
                        PREV_MARK6 = GetValue("PREV_MARK6"),
                        PREV_MARK7 = GetValue("PREV_MARK7"),
                        PREV_MARK8 = GetValue("PREV_MARK8"),
                        PREV_NINKI = GetValue("PREV_NINKI"),
                        ZI_INDEX = GetValue("ZI_INDEX"),
                        ZM_VALUE = GetValue("ZM_VALUE"),
                        ZI_RANK = GetValue("ZI_RANK"),
                        ACCEL_VAL = GetValue("ACCEL_VAL"),
                        ORIGINAL_VAL = GetValue("ORIGINAL_VAL"),
                        INDEX_DIFF1 = GetValue("INDEX_DIFF1"),
                        INDEX_DIFF2 = GetValue("INDEX_DIFF2"),
                        INDEX_DIFF4 = GetValue("INDEX_DIFF4"),
                        INDEX_RANK1 = GetValue("INDEX_RANK1"),
                        INDEX_RANK2 = GetValue("INDEX_RANK2"),
                        INDEX_RANK3 = GetValue("INDEX_RANK3"),
                        INDEX_RANK4 = GetValue("INDEX_RANK4"),
                        MATCHUP_MINING_VAL = GetValue("MATCHUP_MINING_VAL"),
                        MATCHUP_MINING_RANK = GetValue("MATCHUP_MINING_RANK"),
                        DAMSIRE_TYPE_NAME = GetValue("DAMSIRE_TYPE_NAME")
                    };

                    var tanOddsRaw = GetValue("TAN_ODDS") ?? GetValue("TANSHO_ODDS");
                    marksResult.TANSHO_ODDS = FormatOddsValue(tanOddsRaw);
                    marksResult.FUKUSHO_ODDS_LOWER = FormatOddsValue(GetValue("FUKUSHO_ODDS_LOWER"));
                    marksResult.FUKUSHO_ODDS_UPPER = FormatOddsValue(GetValue("FUKUSHO_ODDS_UPPER"));
                    marksResult.FUKUSHO_ODDS = FormatOddsValue(GetValue("FUKUSHO_ODDS"));

                    var raceKey = $"{sourceDate}_{normalizedHorseName}";
                    if (!_allHorseMarks.ContainsKey(raceKey))
                    {
                        _allHorseMarks[raceKey] = marksResult;
                    }

                    var fallbackKey = $"{sourceDate}_01_01";
                    if (!_allHorseMarks.ContainsKey(fallbackKey))
                    {
                        _allHorseMarks[fallbackKey] = marksResult;
                    }

                    if (!string.IsNullOrEmpty(marksResult.RaceId))
                    {
                        var raceIdKey = $"{marksResult.RaceId}_{normalizedHorseName}";
                        if (!_allHorseMarks.ContainsKey(raceIdKey))
                        {
                            _allHorseMarks[raceIdKey] = marksResult;
                        }
                    }
                }

                System.Diagnostics.Debug.WriteLine($"LoadAllMarksFromDatabase: {_allHorseMarks.Count}件を読み込みました。");
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"DBからの全馬印データ読み込みエラー: {ex.Message}");
            }
        }

        // このメソッドはもう使用しないため削除
        // private void LoadMarksFromDatabase()
        // {
        //     System.Diagnostics.Debug.WriteLine("LoadMarksFromDatabase開始");
        //     var marksResult = new HorseMarksResult();
        //
        //     try
        //     {
        //         using var conn = new SQLiteConnection($"Data Source={_dbPath};Version=3;");
        //         conn.Open();
        //
        //         var normalizedHorseName = NormalizeHorseName(_horseName);
        //         if (string.IsNullOrEmpty(normalizedHorseName))
        //         {
        //             marksResult.Message = "無効な馬名";
        //             UpdateHorseMarksDisplay(marksResult);
        //             _latestMarks = marksResult;
        //             return;
        //         }
        //
        //         var sql = @$"
        //             SELECT
        //                 SourceDate, HorseName, RaceId, RaceName,
        //                 JyoCD, Kaiji, Nichiji, RaceNum, Umaban,
        //                 MorningOdds, Mark1, Mark2, Mark3, Mark4,
        //                 Mark5, Mark6, Mark7, Mark8, SourceFile, ImportedAt
        //             FROM {HorseMarksTableName}
        //             WHERE NormalizedHorseName = @normalizedHorseName
        //             ORDER BY SourceDate DESC, ImportedAt DESC
        //             LIMIT 1"; // 最新の馬印データを取得
        //
        //         using var cmd = new SQLiteCommand(sql, conn);
        //         cmd.Parameters.AddWithValue("@normalizedHorseName", normalizedHorseName);
        //
        //         using var reader = cmd.ExecuteReader();
        //         if (reader.Read())
        //         {
        //             marksResult.MorningOdds = reader["MorningOdds"]?.ToString();
        //             marksResult.SourceFile = reader["SourceFile"]?.ToString();
        //
        //             marksResult.Marks["馬印"] = reader["Mark1"]?.ToString() ?? string.Empty;
        //             marksResult.Marks["アルゴ"] = reader["Mark2"]?.ToString() ?? string.Empty;
        //             marksResult.Marks["ZI指数"] = reader["Mark3"]?.ToString() ?? string.Empty;
        //             marksResult.Marks["ZM"] = reader["Mark4"]?.ToString() ?? string.Empty;
        //             marksResult.Marks["馬印5"] = reader["Mark5"]?.ToString() ?? string.Empty;
        //             marksResult.Marks["馬印6"] = reader["Mark6"]?.ToString() ?? string.Empty;
        //             marksResult.Marks["馬印7"] = reader["Mark7"]?.ToString() ?? string.Empty;
        //             marksResult.Marks["馬印8"] = reader["Mark8"]?.ToString() ?? string.Empty;
        //
        //             System.Diagnostics.Debug.WriteLine($"DBから馬印データ読み込み成功: 馬名={_horseName}, SourceFile={marksResult.SourceFile}");
        //         }
        //         else
        //         {
        //             marksResult.Message = "情報のない馬 (DB)";
        //             System.Diagnostics.Debug.WriteLine($"DBに馬印データが見つかりませんでした: 馬名={_horseName}");
        //         }
        //     }
        //     catch (Exception ex)
        //     {
        //         System.Diagnostics.Debug.WriteLine($"DBからの馬印データ読み込みエラー: {ex.Message}");
        //         marksResult.Message = $"DB読み込みエラー: {ex.Message}";
        //     }
        //     finally
        //     {
        //         UpdateHorseMarksDisplay(marksResult);
        //         _latestMarks = marksResult;
        //     }
        // }
        
        private void UpdateHorseMarksDisplay(HorseMarksResult marksResult)
        {
            try
            {
                var sb = new StringBuilder();
                sb.AppendLine("【馬印情報】");

                if (marksResult.HasData)
                {
                    foreach (var (key, value) in marksResult.Marks)
                    {
                        sb.AppendLine($"{key}: {value}");
                    }

                    if (!string.IsNullOrEmpty(marksResult.MorningOdds))
                    {
                        sb.AppendLine($"オッズ: {marksResult.MorningOdds}");
                    }

                    if (!string.IsNullOrEmpty(marksResult.SourceFile))
                    {
                        sb.AppendLine($"データ元: {marksResult.SourceFile}");
                    }
                }
                else
                {
                    sb.AppendLine(marksResult.Message);
                }

                var marksText = sb.ToString().TrimEnd();
                lblMarks.Text = marksText;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"馬印情報表示エラー: {ex.Message}");
            }
        }
        
        private void LoadRaceHistory(SQLiteConnection conn)
        {
            try
            {
                string sql;
                bool viewExists = TableExists(conn, "HORSE_DETAIL_VIEW");

                if (viewExists)
                {
                    sql = @"
                    SELECT 
                        HDV.Year || '/' || SUBSTR(HDV.MonthDay, 1, 2) || '/' || SUBSTR(HDV.MonthDay, 3, 2) as RaceDate,
                        CASE HDV.JyoCD 
                            WHEN '01' THEN '札幌' WHEN '02' THEN '函館' WHEN '03' THEN '福島'
                            WHEN '04' THEN '新潟' WHEN '05' THEN '東京' WHEN '06' THEN '中山'
                            WHEN '07' THEN '中京' WHEN '08' THEN '京都' WHEN '09' THEN '阪神'
                            WHEN '10' THEN '小倉' ELSE HDV.JyoCD END as Jyo,
                        HDV.RaceNum || 'R' as Race,
                        COALESCE(HDV.RaceName, '') as RaceName,
                        CASE 
                            WHEN HDV.KakuteiJyuni = 'H' THEN '取消'
                            WHEN HDV.KakuteiJyuni = 'K' THEN '除外'
                            WHEN HDV.KakuteiJyuni IN ('A','B','C','D') THEN '失格'
                            ELSE HDV.KakuteiJyuni || '着'
                        END as Finish,
                        CASE WHEN HDV.Ninki = '00' OR HDV.Ninki = '' THEN '-' ELSE HDV.Ninki END as Popularity,
                        CASE 
                            WHEN HDV.Odds = '0000' OR HDV.Odds = '' THEN '-'
                            ELSE CAST(CAST(HDV.Odds AS INTEGER) / 10.0 AS TEXT)
                        END as Odds,
                        CASE WHEN HDV.Honsyokin = '' OR HDV.Honsyokin = '00000000' THEN '0' 
                             ELSE CAST(CAST(HDV.Honsyokin AS INTEGER) / 100 AS TEXT) || '万' END as Prize,
                        HDV.KisyuRyakusyo as Jockey,
                        HDV.Futan as Weight,
                        CASE 
                            WHEN COALESCE(HDV.TrackCD, '') = '11' THEN '芝・右'
                            WHEN COALESCE(HDV.TrackCD, '') = '12' THEN '芝・左'
                            WHEN COALESCE(HDV.TrackCD, '') = '13' THEN '芝・直'
                            WHEN COALESCE(HDV.TrackCD, '') = '17' THEN '芝・外'
                            WHEN COALESCE(HDV.TrackCD, '') = '18' THEN '芝・内'
                            WHEN COALESCE(HDV.TrackCD, '') = '21' THEN 'ダ・右'
                            WHEN COALESCE(HDV.TrackCD, '') = '22' THEN 'ダ・左'
                            WHEN COALESCE(HDV.TrackCD, '') = '23' THEN 'ダ・直'
                            WHEN COALESCE(HDV.TrackCD, '') = '24' THEN 'ダ・外'
                            WHEN COALESCE(HDV.TrackCD, '') = '25' THEN 'ダ・内'
                            WHEN COALESCE(HDV.TrackCD, '') = '51' THEN '障芝'
                            WHEN COALESCE(HDV.TrackCD, '') = '52' THEN '障ダ'
                            WHEN COALESCE(HDV.TrackCD, '') = '53' THEN '障芝ダ'
                            WHEN COALESCE(HDV.TrackCD, '') = '54' THEN '障ダ芝'
                            ELSE COALESCE(HDV.TrackCD, '')
                        END as Track,
                        COALESCE(HDV.Kyori, '') as Distance,
                        CASE 
                            WHEN COALESCE(HDV.BabaCD, '') = '1' THEN '良'
                            WHEN COALESCE(HDV.BabaCD, '') = '2' THEN '稍重'
                            WHEN COALESCE(HDV.BabaCD, '') = '3' THEN '重'
                            WHEN COALESCE(HDV.BabaCD, '') = '4' THEN '不良'
                            WHEN COALESCE(HDV.BabaCD, '') = '良' THEN '良'
                            WHEN COALESCE(HDV.BabaCD, '') = '稍重' THEN '稍重'
                            WHEN COALESCE(HDV.BabaCD, '') = '重' THEN '重'
                            WHEN COALESCE(HDV.BabaCD, '') = '不良' THEN '不良'
                            WHEN COALESCE(HDV.BabaCD, '') = 'good' THEN '良'
                            WHEN COALESCE(HDV.BabaCD, '') = 'yielding' THEN '稍重'
                            WHEN COALESCE(HDV.BabaCD, '') = 'soft' THEN '重'
                            WHEN COALESCE(HDV.BabaCD, '') = 'heavy' THEN '不良'
                            ELSE COALESCE(HDV.BabaCD, '良')
                        END as GroundCondition,
                        HDV.ActualFieldSize || '頭' as FieldSize,
                        HDV.RaceTime as RaceTime,
                        HDV.TimeDiff as TimeDifference,
                        HDV.HaronTimeL3 as Last3F,
                        HDV.Jyuni1c || '-' || HDV.Jyuni2c || '-' || HDV.Jyuni3c || '-' || HDV.Jyuni4c as CornerPosition,
                        NULL as レースID,
                        NULL as R印1, NULL as R印2, NULL as R印3, NULL as 馬印1, NULL as 馬印2, NULL as 馬印3, NULL as 馬印4, NULL as 馬印5, NULL as 馬印6, NULL as 馬印7, NULL as 馬印8, NULL as 前脚質, NULL as 前馬印1, NULL as 前馬印2, NULL as 前馬印3, NULL as 前馬印4, NULL as 前馬印5, NULL as 前馬印6, NULL as 前馬印7, NULL as 前馬印8, NULL as 前人気,
                        NULL as ZI指数, NULL as ZI順位, NULL as ZM, NULL as 加速, NULL as オリジナル, NULL as 単勝予想, NULL as 複勝下限, NULL as 複勝上限, NULL as 指数差1, NULL as 指数差2, NULL as 指数差4,
                        HDV.Year as __RawYear, HDV.MonthDay as __RawMonthDay
                    FROM HORSE_DETAIL_VIEW HDV
                    WHERE HDV.KettoNum = @kettoNum
                    ORDER BY HDV.Year DESC, HDV.MonthDay DESC, HDV.JyoCD DESC, HDV.RaceNum DESC
                    LIMIT 120";
                }
                else
                {
                    // HORSE_DETAIL_VIEW がない場合のフォールバッククエリ
                    sql = @"
                    SELECT 
                        UR.Year || '/' || SUBSTR(UR.MonthDay, 1, 2) || '/' || SUBSTR(UR.MonthDay, 3, 2) as RaceDate,
                        CASE UR.JyoCD 
                            WHEN '01' THEN '札幌' WHEN '02' THEN '函館' WHEN '03' THEN '福島'
                            WHEN '04' THEN '新潟' WHEN '05' THEN '東京' WHEN '06' THEN '中山'
                            WHEN '07' THEN '中京' WHEN '08' THEN '京都' WHEN '09' THEN '阪神'
                            WHEN '10' THEN '小倉' ELSE UR.JyoCD END as Jyo,
                        UR.RaceNum || 'R' as Race,
                        COALESCE(R.Hondai, R.RaceName, '') as RaceName,
                        CASE 
                            WHEN UR.KakuteiJyuni = 'H' THEN '取消'
                            WHEN UR.KakuteiJyuni = 'K' THEN '除外'
                            WHEN UR.KakuteiJyuni IN ('A','B','C','D') THEN '失格'
                            ELSE UR.KakuteiJyuni || '着'
                        END as Finish,
                        CASE WHEN UR.Ninki = '00' OR UR.Ninki = '' THEN '-' ELSE UR.Ninki END as Popularity,
                        CASE 
                            WHEN UR.Odds = '0000' OR UR.Odds = '' THEN '-'
                            ELSE CAST(CAST(UR.Odds AS INTEGER) / 10.0 AS TEXT)
                        END as Odds,
                        CASE WHEN UR.Honsyokin = '' OR UR.Honsyokin = '00000000' THEN '0' 
                             ELSE CAST(CAST(UR.Honsyokin AS INTEGER) / 100 AS TEXT) || '万' END as Prize,
                        UR.KisyuRyakusyo as Jockey,
                        UR.Futan as Weight,
                        CASE 
                            WHEN COALESCE(R.TrackCD, '') = '11' THEN '芝・右'
                            WHEN COALESCE(R.TrackCD, '') = '12' THEN '芝・左'
                            WHEN COALESCE(R.TrackCD, '') = '13' THEN '芝・直'
                            WHEN COALESCE(R.TrackCD, '') = '17' THEN '芝・外'
                            WHEN COALESCE(R.TrackCD, '') = '18' THEN '芝・内'
                            WHEN COALESCE(R.TrackCD, '') = '21' THEN 'ダ・右'
                            WHEN COALESCE(R.TrackCD, '') = '22' THEN 'ダ・左'
                            WHEN COALESCE(R.TrackCD, '') = '23' THEN 'ダ・直'
                            WHEN COALESCE(R.TrackCD, '') = '24' THEN 'ダ・外'
                            WHEN COALESCE(R.TrackCD, '') = '25' THEN 'ダ・内'
                            WHEN COALESCE(R.TrackCD, '') = '51' THEN '障芝'
                            WHEN COALESCE(R.TrackCD, '') = '52' THEN '障ダ'
                            WHEN COALESCE(R.TrackCD, '') = '53' THEN '障芝ダ'
                            WHEN COALESCE(R.TrackCD, '') = '54' THEN '障ダ芝'
                            ELSE COALESCE(R.TrackCD, '')
                        END as Track,
                        COALESCE(R.Kyori, '') as Distance,
                        CASE 
                            WHEN COALESCE(R.BabaCD, '') = '1' THEN '良'
                            WHEN COALESCE(R.BabaCD, '') = '2' THEN '稍重'
                            WHEN COALESCE(R.BabaCD, '') = '3' THEN '重'
                            WHEN COALESCE(R.BabaCD, '') = '4' THEN '不良'
                            ELSE COALESCE(R.BabaCD, '良')
                        END as GroundCondition,
                        (SELECT COUNT(1) FROM N_UMA_RACE sub WHERE sub.Year = UR.Year AND sub.MonthDay = UR.MonthDay AND sub.JyoCD = UR.JyoCD AND sub.RaceNum = UR.RaceNum) || '頭' as FieldSize,
                        UR.Time as RaceTime,
                        UR.TimeDiff as TimeDifference,
                        UR.HaronTimeL3 as Last3F,
                        UR.Jyuni1c || '-' || UR.Jyuni2c || '-' || UR.Jyuni3c || '-' || UR.Jyuni4c as CornerPosition,
                        NULL as レースID,
                        NULL as R印1, NULL as R印2, NULL as R印3, NULL as 馬印1, NULL as 馬印2, NULL as 馬印3, NULL as 馬印4, NULL as 馬印5, NULL as 馬印6, NULL as 馬印7, NULL as 馬印8, NULL as 前脚質, NULL as 前馬印1, NULL as 前馬印2, NULL as 前馬印3, NULL as 前馬印4, NULL as 前馬印5, NULL as 前馬印6, NULL as 前馬印7, NULL as 前馬印8, NULL as 前人気,
                        NULL as ZI指数, NULL as ZI順位, NULL as ZM, NULL as 加速, NULL as オリジナル, NULL as 単勝予想, NULL as 複勝下限, NULL as 複勝上限, NULL as 指数差1, NULL as 指数差2, NULL as 指数差4,
                        UR.Year as __RawYear, UR.MonthDay as __RawMonthDay
                    FROM N_UMA_RACE UR
                    LEFT JOIN N_RACE R ON UR.Year = R.Year AND UR.MonthDay = R.MonthDay AND UR.JyoCD = R.JyoCD AND UR.RaceNum = R.RaceNum
                    WHERE UR.KettoNum = @kettoNum
                    ORDER BY UR.Year DESC, UR.MonthDay DESC, UR.JyoCD DESC, UR.RaceNum DESC
                    LIMIT 120";
                }

                using var da = new SQLiteDataAdapter(sql, conn);
                da.SelectCommand.Parameters.AddWithValue("@kettoNum", _kettoNum);
                
                var dt = new DataTable();
                da.Fill(dt);
                
                // DBから馬印データを事前に全て読み込む
                LoadAllMarksFromDatabase();
                
                // カラム名を日本語に変更
                if (dt.Columns.Contains("RaceDate")) dt.Columns["RaceDate"].ColumnName = "日付";
                if (dt.Columns.Contains("Jyo")) dt.Columns["Jyo"].ColumnName = "競馬場";
                if (dt.Columns.Contains("Race")) dt.Columns["Race"].ColumnName = "R";
                if (dt.Columns.Contains("RaceName")) dt.Columns["RaceName"].ColumnName = "レース名";
                if (dt.Columns.Contains("Finish")) dt.Columns["Finish"].ColumnName = "着順";
                if (dt.Columns.Contains("Popularity")) dt.Columns["Popularity"].ColumnName = "人気";
                if (dt.Columns.Contains("Odds")) dt.Columns["Odds"].ColumnName = "オッズ";
                if (dt.Columns.Contains("Prize")) dt.Columns["Prize"].ColumnName = "賞金";
                if (dt.Columns.Contains("Jockey")) dt.Columns["Jockey"].ColumnName = "騎手";
                if (dt.Columns.Contains("Weight")) dt.Columns["Weight"].ColumnName = "斤量";
                if (dt.Columns.Contains("Track")) dt.Columns["Track"].ColumnName = "コース";
                if (dt.Columns.Contains("Distance")) dt.Columns["Distance"].ColumnName = "距離";
                if (dt.Columns.Contains("GroundCondition")) dt.Columns["GroundCondition"].ColumnName = "馬場";
                if (dt.Columns.Contains("FieldSize")) dt.Columns["FieldSize"].ColumnName = "頭数";
                if (dt.Columns.Contains("RaceTime")) dt.Columns["RaceTime"].ColumnName = "タイム";
                if (dt.Columns.Contains("TimeDifference")) dt.Columns["TimeDifference"].ColumnName = "着差";
                if (dt.Columns.Contains("Last3F")) dt.Columns["Last3F"].ColumnName = "上3F";
                if (dt.Columns.Contains("CornerPosition")) dt.Columns["CornerPosition"].ColumnName = "通過";
                
                // 新しい列の値を設定（Excel由来の馬印情報をグリッド表示前に反映）
                ApplyHorseMarksToDataTable(dt);
                
                gridRaceHistory.DataSource = dt;
                
                // 列幅設定
                SetColumnWidths();
                
                
                
                // Excelから読み込んだ馬印情報をグリッドに反映
                ApplyHorseMarksToGrid();
            }
            catch (Exception ex)
            {
                MessageBox.Show($"レース履歴読み込みエラー: {ex.Message}", "エラー", 
                    MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }
        
        private void SetColumnWidths()
        {
            if (gridRaceHistory.Columns.Count > 0)
            {
                var columns = gridRaceHistory.Columns;
                
                void SetColumnWidth(string name, int width)
                {
                    if (columns.Contains(name))
                    {
                        var column = columns[name];
                        if (column != null)
                        {
                            column.Width = width;
                        }
                    }
                }
                
                // 基本情報
                SetColumnWidth("日付", 70);
                SetColumnWidth("競馬場", 45);
                SetColumnWidth("R", 30);
                SetColumnWidth("レースID", 130);
                SetColumnWidth("レース名", 140);
                SetColumnWidth("着順", 40);
                SetColumnWidth("人気", 35);
                SetColumnWidth("オッズ", 45);
                
                // レース条件
                SetColumnWidth("コース", 50);
                SetColumnWidth("距離", 45);
                SetColumnWidth("馬場", 40);
                
                // 騎手・斤量
                SetColumnWidth("騎手", 60);
                SetColumnWidth("斤量", 40);
                
                // レース結果
                SetColumnWidth("タイム", 50);
                SetColumnWidth("着差", 40);
                SetColumnWidth("上3F", 40);
                SetColumnWidth("通過", 70);
                SetColumnWidth("頭数", 40);
                SetColumnWidth("賞金", 50);
                
                // 新しい列の幅設定
                SetColumnWidth("R印1", 40);
                SetColumnWidth("R印2", 40);
                SetColumnWidth("R印3", 40);
                SetColumnWidth("馬印1", 40);
                SetColumnWidth("馬印2", 40);
                SetColumnWidth("馬印3", 40);
                SetColumnWidth("馬印4", 40);
                SetColumnWidth("馬印5", 40);
                SetColumnWidth("馬印6", 40);
                SetColumnWidth("馬印7", 40);
                SetColumnWidth("馬印8", 40);
                SetColumnWidth("前脚質", 50);
                SetColumnWidth("前馬印1", 40);
                SetColumnWidth("前馬印2", 40);
                SetColumnWidth("前馬印3", 40);
                SetColumnWidth("前馬印4", 40);
                SetColumnWidth("前馬印5", 40);
                SetColumnWidth("前馬印6", 40);
                SetColumnWidth("前馬印7", 40);
                SetColumnWidth("前馬印8", 40);
                SetColumnWidth("前人気", 40);
                SetColumnWidth("ZI指数", 55);
                SetColumnWidth("ZI順位", 55);
                SetColumnWidth("ZM", 55);
                SetColumnWidth("加速", 55);
                SetColumnWidth("オリジナル", 60);
                SetColumnWidth("単勝予想", 70);
                SetColumnWidth("複勝下限", 70);
                SetColumnWidth("複勝上限", 70);
                SetColumnWidth("指数差1", 55);
                SetColumnWidth("指数差2", 55);
                SetColumnWidth("指数差4", 55);
            }
        }
        
        private void SetColumnOrder()
        {
            try
            {
                var columns = gridRaceHistory.Columns;
                
                // 列の順序を指定
                var columnOrder = new[]
                {
                    "日付", "競馬場", "R", "レースID", "レース名", "コース", "距離", "馬場", "頭数",
                    "着順", "人気", "騎手", "斤量", "タイム", "着差", "上3F", "通過", "オッズ", "賞金",
                    "R印1", "R印2", "R印3",
                    "馬印1", "馬印2", "馬印3", "馬印4", "馬印5", "馬印6", "馬印7", "馬印8",
                    "前脚質",
                    "前馬印1", "前馬印2", "前馬印3", "前馬印4", "前馬印5", "前馬印6", "前馬印7", "前馬印8",
                    "前人気",
                    "ZI指数", "ZI順位", "ZM", "加速", "オリジナル", "単勝予想", "複勝下限", "複勝上限",
                    "指数差1", "指数差2", "指数差4"
                };
                
                // 存在する列だけを順番に並べる
                int index = 0;
                foreach (var colName in columnOrder)
                {
                    if (columns.Contains(colName) && columns[colName] != null)
                    {
                        columns[colName].DisplayIndex = index++;
                    }
                }
            }
            catch (Exception)
            {
                // 列の順序変更に失敗しても続行
            }
        }
        
        private void ApplyFinishColorCoding()
        {
            if (!gridRaceHistory.Columns.Contains("着順")) return;
            
            foreach (DataGridViewRow row in gridRaceHistory.Rows)
            {
                var finishCell = row.Cells["着順"];
                var finish = finishCell.Value?.ToString() ?? "";
                
                if (finish == "1着")
                {
                    finishCell.Style.BackColor = Color.Gold;
                    finishCell.Style.ForeColor = Color.Black;
                }
                else if (finish == "2着")
                {
                    finishCell.Style.BackColor = Color.Silver;
                    finishCell.Style.ForeColor = Color.Black;
                }
                else if (finish == "3着")
                {
                    finishCell.Style.BackColor = Color.SandyBrown;
                    finishCell.Style.ForeColor = Color.Black;
                }
                else if (finish.Contains("取消") || finish.Contains("除外") || finish.Contains("失格"))
                {
                    finishCell.Style.BackColor = Color.LightGray;
                    finishCell.Style.ForeColor = Color.Red;
                }
            }
        }
        
        private void LoadStatsInfo(SQLiteConnection conn)
        {
            try
            {
                var sql = @"
                    SELECT 
                        COUNT(*) as TotalRaces,
                        SUM(CASE WHEN KakuteiJyuni = '01' THEN 1 ELSE 0 END) as Wins,
                        SUM(CASE WHEN KakuteiJyuni IN ('01','02') THEN 1 ELSE 0 END) as Places,
                        SUM(CASE WHEN KakuteiJyuni IN ('01','02','03') THEN 1 ELSE 0 END) as Shows,
                        SUM(CASE 
                            WHEN Honsyokin IS NULL OR Honsyokin = '' OR Honsyokin = '00000000' 
                            THEN 0 
                            ELSE CAST(Honsyokin AS INTEGER) 
                        END) as TotalPrize
                    FROM N_UMA_RACE 
                    WHERE KettoNum = @kettoNum 
                    AND KakuteiJyuni NOT IN ('H','K','A','B','C','D','')";
                    
                using var cmd = new SQLiteCommand(sql, conn);
                cmd.Parameters.AddWithValue("@kettoNum", _kettoNum);
                
                using var reader = cmd.ExecuteReader();
                if (reader.Read())
                {
                    var total = Convert.ToInt32(reader["TotalRaces"]);
                    var wins = Convert.ToInt32(reader["Wins"]);
                    var places = Convert.ToInt32(reader["Places"]);
                    var shows = Convert.ToInt32(reader["Shows"]);
                    var totalPrize = Convert.ToInt64(reader["TotalPrize"]);
                    
                    var winRate = total > 0 ? (wins * 100.0 / total) : 0;
                    var placeRate = total > 0 ? (places * 100.0 / total) : 0;
                    var showRate = total > 0 ? (shows * 100.0 / total) : 0;
                    
                    lblStats.Text = $"【成績サマリー】\n" +
                                   $"戦績: {wins}-{places - wins}-{shows - places}-{total - shows}\n" +
                                   $"勝率: {winRate:F1}%  連対率: {placeRate:F1}%\n" +
                                   $"複勝率: {showRate:F1}%\n" +
                                   $"総賞金: {totalPrize / 100:N0}万円";
                }
                else
                {
                    lblStats.Text = "成績データが見つかりません";
                }
            }
            catch (Exception ex)
            {
                lblStats.Text = $"成績データ読み込みエラー: {ex.Message}";
            }
        }
        
        private static string GetSexName(string sexCD)
        {
            return sexCD switch
            {
                "1" => "牡",
                "2" => "牝", 
                "3" => "騸",
                _ => sexCD
            };
        }
        
        private static string GetColorName(string keiroCD)
        {
            return keiroCD switch
            {
                "01" => "栗毛",
                "02" => "栃栗毛",
                "03" => "鹿毛",
                "04" => "黒鹿毛",
                "05" => "青鹿毛",
                "06" => "青毛",
                "07" => "芦毛",
                "08" => "栗栗毛",
                "09" => "白毛",
                _ => keiroCD
            };
        }
        
        private static string GetBreedName(string hinsyuCD)
        {
            return hinsyuCD switch
            {
                "1" => "サラブレッド",
                "2" => "アングロアラブ",
                "3" => "アラブ",
                "4" => "中半血",
                "5" => "軽半血",
                "6" => "重半血",
                _ => hinsyuCD
            };
        }
        
        private static string CalculateAge(string birthDate)
        {
            if (string.IsNullOrEmpty(birthDate) || birthDate.Length != 8)
                return "不明";
                
            try
            {
                var year = int.Parse(birthDate.Substring(0, 4));
                var month = int.Parse(birthDate.Substring(4, 2));
                var day = int.Parse(birthDate.Substring(6, 2));
                
                var birth = new DateTime(year, month, day);
                var today = DateTime.Today;
                
                var age = today.Year - birth.Year;
                if (today.Month < birth.Month || (today.Month == birth.Month && today.Day < birth.Day))
                    age--;
                    
                return age.ToString();
            }
            catch
            {
                return "不明";
            }
        }
        
        private void CopySelectedRows(object? sender, EventArgs e)
        {
            try
            {
                if (gridRaceHistory.SelectedRows.Count == 0)
                {
                    MessageBox.Show("コピーする行を選択してください。", "情報", 
                        MessageBoxButtons.OK, MessageBoxIcon.Information);
                    return;
                }
                
                var clipboardText = new System.Text.StringBuilder();
                
                // ヘッダー行を追加
                var headers = new List<string>();
                foreach (DataGridViewColumn column in gridRaceHistory.Columns)
                {
                    headers.Add(column.HeaderText);
                }
                clipboardText.AppendLine(string.Join("\t", headers));
                
                // 選択された行のデータを追加
                foreach (DataGridViewRow row in gridRaceHistory.SelectedRows)
                {
                    var rowData = new List<string>();
                    foreach (DataGridViewCell cell in row.Cells)
                    {
                        rowData.Add(cell.Value?.ToString() ?? "");
                    }
                    clipboardText.AppendLine(string.Join("\t", rowData));
                }
                
                Clipboard.SetText(clipboardText.ToString());
                MessageBox.Show($"{gridRaceHistory.SelectedRows.Count}行のデータをクリップボードにコピーしました。", "完了", 
                    MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
            catch (Exception ex)
            {
                MessageBox.Show($"コピー中にエラーが発生しました: {ex.Message}", "エラー", 
                    MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }
        
        private void ApplyHorseMarksToDataTable(DataTable dataTable)
        {
            if (dataTable == null || dataTable.Rows.Count == 0) return;
            if (_allHorseMarks.Count == 0) return;

            foreach (DataRow row in dataTable.Rows)
            {
                var rawYear = row["__RawYear"]?.ToString();
                var rawMonthDay = row["__RawMonthDay"]?.ToString();
                if (string.IsNullOrEmpty(rawYear) || string.IsNullOrEmpty(rawMonthDay)) continue;
                
                var raceDate = $"{rawYear}{rawMonthDay}";
                var normalizedHorseName = NormalizeHorseName(_horseName);
                var raceKey = $"{raceDate}_{normalizedHorseName}";

                var raceKeyDateOnly = $"{raceDate}_01_01";

                if (_allHorseMarks.TryGetValue(raceKey, out var marks) || _allHorseMarks.TryGetValue(raceKeyDateOnly, out marks))
                {
                    void SetValue(string colName, string value) { if(dataTable.Columns.Contains(colName)) row[colName] = value ?? string.Empty; }

                    SetValue("R印1", marks.R_MARK1);
                    SetValue("R印2", marks.R_MARK2);
                    SetValue("R印3", marks.R_MARK3);
                    SetValue("馬印1", marks.Mark1);
                    SetValue("馬印2", marks.Mark2);
                    SetValue("馬印3", marks.Mark3);
                    SetValue("馬印4", marks.Mark4);
                    SetValue("馬印5", marks.Mark5);
                    SetValue("馬印6", marks.Mark6);
                    SetValue("馬印7", marks.Mark7);
                    SetValue("馬印8", marks.Mark8);
                    SetValue("前脚質", marks.PREV_KYAKUSHITSU);
                    SetValue("前馬印1", marks.PREV_MARK1);
                    SetValue("前馬印2", marks.PREV_MARK2);
                    SetValue("前馬印3", marks.PREV_MARK3);
                    SetValue("前馬印4", marks.PREV_MARK4);
                    SetValue("前馬印5", marks.PREV_MARK5);
                    SetValue("前馬印6", marks.PREV_MARK6);
                    SetValue("前馬印7", marks.PREV_MARK7);
                    SetValue("前馬印8", marks.PREV_MARK8);
                    SetValue("前人気", marks.PREV_NINKI ?? string.Empty);
                    SetValue("レースID", marks.RaceId ?? string.Empty);
                    SetValue("ZI指数", marks.ZI_INDEX ?? string.Empty);
                    SetValue("ZI順位", marks.ZI_RANK ?? string.Empty);
                    SetValue("ZM", marks.ZM_VALUE ?? string.Empty);
                    SetValue("加速", marks.ACCEL_VAL ?? string.Empty);
                    SetValue("オリジナル", marks.ORIGINAL_VAL ?? string.Empty);
                    SetValue("単勝予想", marks.TANSHO_ODDS ?? string.Empty);
                    SetValue("複勝下限", marks.FUKUSHO_ODDS_LOWER ?? string.Empty);
                    SetValue("複勝上限", marks.FUKUSHO_ODDS_UPPER ?? string.Empty);
                    SetValue("指数差1", marks.INDEX_DIFF1 ?? string.Empty);
                    SetValue("指数差2", marks.INDEX_DIFF2 ?? string.Empty);
                    SetValue("指数差4", marks.INDEX_DIFF4 ?? string.Empty);
                }
            }
            
            if (dataTable.Columns.Contains("__RawYear")) dataTable.Columns.Remove("__RawYear");
            if (dataTable.Columns.Contains("__RawMonthDay")) dataTable.Columns.Remove("__RawMonthDay");
        }

        private void ApplyHorseMarksToGrid()
        {
            try
            {
                gridRaceHistory.Refresh();

                var columns = gridRaceHistory.Columns;
                if (columns.Contains(ColumnNameMark))
                {
                    SetColumnFont(columns[ColumnNameMark], FontStyle.Bold);
                }

                if (columns.Contains(ColumnNameAlgo))
                {
                    SetColumnForeColor(columns[ColumnNameAlgo], Color.DarkBlue);
                }

                if (columns.Contains(ColumnNameZm))
                {
                    SetColumnForeColor(columns[ColumnNameZm], Color.DarkGreen);
                }

                if (columns.Contains(ColumnNameZi))
                {
                    SetColumnForeColor(columns[ColumnNameZi], Color.DarkViolet);
                }

                if (columns.Contains(ColumnNameTraining5))
                {
                    SetColumnForeColor(columns[ColumnNameTraining5], Color.DarkOrange);
                }

                if (columns.Contains(ColumnNameTraining6))
                {
                    SetColumnForeColor(columns[ColumnNameTraining6], Color.DarkOrange);
                }

                HideRawMarkColumns(columns);            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"馬印情報のグリッド反映エラー: {ex.Message}");
            }
        }

        
        private static void HideRawMarkColumns(DataGridViewColumnCollection columns)
        {
            string[] hidden =
            {
                "Mark1", "Mark2", "Mark3", "Mark4", "Mark5", "Mark6", "Mark7", "Mark8"
            };

            foreach (var name in hidden)
            {
                if (columns.Contains(name))
                {
                    columns[name]!.Visible = false;
                }
            }
        }

private void SetColumnFont(DataGridViewColumn? column, FontStyle style)
        {
            if (column == null)
            {
                return;
            }

            var originalFont = column.DefaultCellStyle?.Font ?? gridRaceHistory.DefaultCellStyle?.Font;
            if (originalFont == null)
            {
                originalFont = Control.DefaultFont;
            }

            column.DefaultCellStyle.Font = new Font(originalFont, style);
        }

        private void SetColumnForeColor(DataGridViewColumn? column, Color color)
        {
            if (column == null)
            {
                return;
            }

            if (column.DefaultCellStyle == null)
            {
                column.DefaultCellStyle = new DataGridViewCellStyle();
            }

            column.DefaultCellStyle.ForeColor = color;
        }
    }
}
