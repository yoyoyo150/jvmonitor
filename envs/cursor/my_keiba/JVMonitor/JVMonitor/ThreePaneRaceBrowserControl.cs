using System;
using System.Collections.Generic;
using System.Data;
using System.Data.SQLite;
using System.Drawing;
using System.Linq;
using System.Windows.Forms;
using System.Text;
using System.IO; // Added for Path.Combine
using Microsoft.Extensions.Configuration; // Add this using directive

namespace JVMonitor
{
    public sealed class ThreePaneRaceBrowserControl : UserControl
    {
        readonly string _dbPath;
        private readonly IConfiguration _configuration; // Add this field

        SplitContainer scLeftRight = null!;   // 左(開催日) / 右(開催場+出馬表)
        SplitContainer scMidRight  = null!;    // 中(開催場/レース) / 右(出馬表)
        ListView lvDays = null!;              // 開催日
        TreeView tvMeetings = null!;          // 開催場(親)→レース(子)
        DataGridView grid = null!;            // 出馬表
        StatusStrip status = null!; ToolStripStatusLabel lbl = null!;
        Panel raceInfoPanel = null!; Label lblSummary = null!;

        readonly Dictionary<string, string> jyoMap = new()
        {
            {"01","札幌"},{"02","函館"},{"03","福島"},{"04","新潟"},{"05","東京"},
            {"06","中山"},{"07","中京"},{"08","京都"},{"09","阪神"},{"10","小倉"},
            {"30","門別"},{"31","盛岡"},{"32","水沢"},{"33","浦和"},{"34","船橋"},
            {"35","大井"},{"36","川崎"},{"37","金沢"},{"38","笠松"},{"39","名古屋"},
            {"40","園田"},{"41","姫路"},{"42","高知"},{"43","佐賀"}
        };

        public ThreePaneRaceBrowserControl(string dbPath, IConfiguration configuration)
        {
            _dbPath = dbPath;
            _configuration = configuration;
            BuildUi();
            this.Load += (_, __) => { LoadRecentDays(); ApplyLayoutSizing(); };
            this.Resize += (_, __) => ApplyLayoutSizing();
        }

        void BuildUi()
        {
            Dock = DockStyle.Fill;

            scLeftRight = new SplitContainer { Dock = DockStyle.Fill, Orientation = Orientation.Vertical, SplitterDistance = 200 };
            scMidRight = new SplitContainer { Dock = DockStyle.Fill, Orientation = Orientation.Vertical, SplitterDistance = 200 };

            lvDays = new ListView { Dock = DockStyle.Fill, View = View.Details, FullRowSelect = true, HideSelection = false };
            lvDays.Columns.Add("開催日", 200);
            lvDays.ItemActivate += (s, e) => LoadMeetingsOfSelectedDay();
            lvDays.Resize += (s, e) =>
            {
                if (lvDays.Columns.Count > 0)
                {
                    var sbw = SystemInformation.VerticalScrollBarWidth;
                    lvDays.Columns[0].Width = Math.Max(120, lvDays.ClientSize.Width - sbw - 6);
                }
            };

            tvMeetings = new TreeView { Dock = DockStyle.Fill };
            tvMeetings.AfterSelect += (s, e) => { if (e.Node?.Tag is RaceKey rk && !string.IsNullOrEmpty(rk.RaceNum)) LoadEntries(rk); };

            grid = new DataGridView
            {
                Dock = DockStyle.Fill,
                ReadOnly = true,
                AllowUserToAddRows = false,
                AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.None
            };
            grid.RowHeadersVisible = false;
            grid.AutoSizeRowsMode = DataGridViewAutoSizeRowsMode.None; // 2段に見えないよう固定高さ
            grid.RowTemplate.Height = 22;
            grid.DefaultCellStyle.WrapMode = DataGridViewTriState.False;
            grid.DefaultCellStyle.Font = new Font("Yu Gothic UI", 10F, FontStyle.Regular, GraphicsUnit.Point);
            grid.ColumnHeadersDefaultCellStyle.Font = new Font("Yu Gothic UI", 10F, FontStyle.Bold, GraphicsUnit.Point);
            grid.ColumnHeadersDefaultCellStyle.WrapMode = DataGridViewTriState.False; // 見出し2段化を防ぐ
            grid.ColumnHeadersHeightSizeMode = DataGridViewColumnHeadersHeightSizeMode.DisableResizing;
            grid.ColumnHeadersHeight = 24;
            
            // 馬名ダブルクリックで馬詳細画面を開く
            grid.CellDoubleClick += Grid_CellDoubleClick;

            // 行のスタイル設定
            grid.CellFormatting += (s, e) =>
            {
                if (e.RowIndex < 0 || grid.Columns.Count <= e.ColumnIndex) return;
                if (grid.Columns[e.ColumnIndex].Name == "馬評価")
                {
                    var rank = e.Value?.ToString() ?? "E";
                    switch (rank)
                    {
                        case "S": e.CellStyle.BackColor = Color.LightCoral; break;
                        case "A": e.CellStyle.BackColor = Color.LightSkyBlue; break;
                        case "B": e.CellStyle.BackColor = Color.LightGreen; break;
                        case "C": e.CellStyle.BackColor = Color.LightYellow; break;
                        case "D": e.CellStyle.BackColor = Color.LightGray; break;
                        case "E": e.CellStyle.BackColor = Color.WhiteSmoke; break;
                    }
                }
            };

            // レース概要（距離・コース・クラス・発走）
            raceInfoPanel = new Panel { Dock = DockStyle.Top, Height = 60, Padding = new Padding(6, 4, 6, 4) };
            lblSummary = new Label { Dock = DockStyle.Fill, Text = "", AutoEllipsis = true };
            raceInfoPanel.Controls.Add(lblSummary);

            status = new StatusStrip();
            lbl = new ToolStripStatusLabel("準備中…");
            status.Items.Add(lbl);

            scLeftRight.Panel1.Controls.Add(lvDays);
            scMidRight.Panel1.Controls.Add(tvMeetings);
            scMidRight.Panel2.Controls.Add(grid);
            scMidRight.Panel2.Controls.Add(raceInfoPanel);
            scLeftRight.Panel2.Controls.Add(scMidRight);
            Controls.Add(scLeftRight);
            Controls.Add(status);
        }

        void ApplyLayoutSizing()
        {
            // 左ペイン固定幅、中央と右は同じサイズ
            // 左右スプリッタの位置を安全に調整
            var minLeft = scLeftRight.Panel1MinSize;
            var minRight = scLeftRight.Panel2MinSize;
            if (scLeftRight.Width > minLeft + minRight)
            {
                var maxDistance = scLeftRight.Width - minRight;
                var desired = 200;
                var safeDistance = Math.Max(minLeft, Math.Min(desired, maxDistance));
                scLeftRight.SplitterDistance = safeDistance;
            }

            var midMinLeft = scMidRight.Panel1MinSize;
            var midMinRight = scMidRight.Panel2MinSize;
            var availableWidth = scMidRight.Width - midMinRight;
            if (availableWidth > midMinLeft)
            {
                if (availableWidth <= Math.Max(midMinLeft, 180))
                {
                    scMidRight.SplitterDistance = Math.Max(midMinLeft, availableWidth);
                }
                else
                {
                    var desiredRatio = (int)(scMidRight.Width * 0.32);
                    var minPanel = Math.Max(midMinLeft, 180);
                    var maxPanel = Math.Max(minPanel, Math.Min(availableWidth, 340));
                    var safeDistance2 = Math.Clamp(desiredRatio, minPanel, maxPanel);
                    scMidRight.SplitterDistance = safeDistance2;
                }
            }

            // 日付リストの幅調整
            if (lvDays.Columns.Count > 0)
            {
                var sbw = SystemInformation.VerticalScrollBarWidth;
                lvDays.Columns[0].Width = Math.Max(120, lvDays.ClientSize.Width - sbw - 6);
            }
        }

        static string TranslateTrack(string code)
        {
            // 代表的なTrackCDの簡易表示（不明はコード表示）
            var map = new Dictionary<string, string>
            {
                {"11", "芝 右"}, {"12", "芝 左"}, {"13", "芝 直"},
                {"21", "ダート 右"}, {"22", "ダート 左"}, {"23", "ダート 直"},
                {"31", "障害 芝"}, {"32", "障害 ダート"}
            };
            return map.TryGetValue(code ?? string.Empty, out var v) ? v : (code ?? string.Empty);
        }

        SQLiteConnection Open()
        {
            var cn = new SQLiteConnection($"Data Source={_dbPath};Version=3;");
            cn.Open(); return cn;
        }
        static bool HasCol(SQLiteConnection cn, string table, string col)
        {
            using var cmd = new SQLiteCommand($"PRAGMA table_info({table})", cn);
            using var rd = cmd.ExecuteReader();
            while (rd.Read())
                if (string.Equals(rd["name"]?.ToString(), col, StringComparison.OrdinalIgnoreCase)) return true;
            return false;
        }
        static bool TableExists(SQLiteConnection cn, string table)
        {
            using var cmd = new SQLiteCommand("SELECT 1 FROM sqlite_master WHERE type='table' AND name=@n LIMIT 1", cn);
            cmd.Parameters.AddWithValue("@n", table);
            var v = cmd.ExecuteScalar();
            return v != null && v != DBNull.Value;
        }
        static string Pick(SQLiteConnection cn, string table, params string[] candidates)
            => candidates.FirstOrDefault(c => HasCol(cn, table, c)) ?? candidates[0];

        // レース名の式を動的に構築（列が無ければ安全にフォールバック）
        static string BuildRaceNameExpr(SQLiteConnection cn)
        {
            // よくある候補
            var nameCols = new[] { "RaceName", "RaceNameJ", "Racename", "レース名" };
            var hondai = HasCol(cn, "N_RACE", "Hondai");
            var fukudai = HasCol(cn, "N_RACE", "Fukudai");
            if (hondai && fukudai)
            {
                return "COALESCE(Hondai || ' ' || Fukudai, Hondai)";
            }
            if (hondai)
            {
                return "Hondai";
            }
            var first = nameCols.FirstOrDefault(c => HasCol(cn, "N_RACE", c));
            if (first != null)
            {
                return first;
            }
            // 最終手段: idRaceNumを文字列で返す
            return "CAST(idRaceNum AS TEXT)";
        }

        void LoadRecentDays()
        {
            lvDays.Items.Clear();
            using var cn = Open();
            using var cmd = new SQLiteCommand(
                "SELECT DISTINCT Year, MonthDay FROM N_RACE ORDER BY Year DESC, MonthDay DESC LIMIT 365*3", cn);
            using var rd = cmd.ExecuteReader();
            while (rd.Read())
            {
                var y = rd["Year"]?.ToString();
                var md = rd["MonthDay"]?.ToString();
                if (string.IsNullOrEmpty(y) || string.IsNullOrEmpty(md) || md.Length < 4) continue;
                var dt = DateTime.Parse($"{y}-{md[..2]}-{md[2..]}");
                lvDays.Items.Add(new ListViewItem(dt.ToString("yyyy/MM/dd")) { Tag = (y, md) });
            }
            if (lvDays.Items.Count > 0)
            {
                lvDays.Items[0].Selected = true; LoadMeetingsOfSelectedDay();
            }
            lbl.Text = $"開催日: {lvDays.Items.Count} 件";
        }

        void LoadMeetingsOfSelectedDay()
        {
            tvMeetings.BeginUpdate();
            tvMeetings.Nodes.Clear();
            grid.DataSource = null;
            if (lvDays.SelectedItems.Count == 0) { tvMeetings.EndUpdate(); return; }
            var (y, md) = ((string y, string md))lvDays.SelectedItems[0].Tag;

            using var cn = Open();
            var raceNameExpr = BuildRaceNameExpr(cn);
            bool hasTime = HasCol(cn, "N_RACE", "HassoTime");

            using var cmdJ = new SQLiteCommand(
                "SELECT DISTINCT JyoCD FROM N_RACE WHERE Year=@y AND MonthDay=@md ORDER BY JyoCD", cn);
            cmdJ.Parameters.AddWithValue("@y", y); cmdJ.Parameters.AddWithValue("@md", md);
            using var rdJ = cmdJ.ExecuteReader();
            while (rdJ.Read())
            {
                var j = rdJ["JyoCD"]?.ToString() ?? "";
                var jName = jyoMap.TryGetValue(j, out var nm) ? nm : j;
                var parent = new TreeNode($"{jName}（{j}）") { Tag = new RaceKey(y, md, j, "") };
                tvMeetings.Nodes.Add(parent);

                string sql = $"SELECT RaceNum, {raceNameExpr} AS RN" + (hasTime ? ", HassoTime" : "") +
                             " FROM N_RACE WHERE Year=@y AND MonthDay=@md AND JyoCD=@j " +
                             "ORDER BY CAST(RaceNum AS INTEGER)";
                using var cmdR = new SQLiteCommand(sql, cn);
                cmdR.Parameters.AddWithValue("@y", y);
                cmdR.Parameters.AddWithValue("@md", md);
                cmdR.Parameters.AddWithValue("@j", j);
                using var rdR = cmdR.ExecuteReader();
                while (rdR.Read())
                {
                    var r = rdR["RaceNum"]?.ToString() ?? "";
                    var tm = hasTime ? $" [{rdR["HassoTime"]}]" : "";
                    parent.Nodes.Add(new TreeNode($"{r}R{tm}") { Tag = new RaceKey(y, md, j, r) });
                }
                parent.Expand();
            }
            tvMeetings.EndUpdate();
            lbl.Text = $"{y}/{md}: 場 {tvMeetings.Nodes.Count}";
        }

        void LoadEntries(RaceKey k)
        {
            const string RawUmabanColumn = "__UmabanRaw";
            if (string.IsNullOrEmpty(k.RaceNum))
            {
                grid.DataSource = null;
                return;
            }

            using var cn = Open();

            // 1. 予測データを先にメモリに読み込む
            var predictions = new Dictionary<string, string>();
            var predictionsDbPath = _configuration["PredictionsDbPath"];
            if (!string.IsNullOrEmpty(predictionsDbPath) && File.Exists(predictionsDbPath))
            {
                try
                {
                    using (var attachCmd = new SQLiteCommand($"ATTACH DATABASE '{predictionsDbPath.Replace("'", "''")}' AS predictionsDb", cn))
                    {
                        attachCmd.ExecuteNonQuery();
                    }

                    // テーブル存在チェック
                    using (var checkTableCmd = new SQLiteCommand("SELECT 1 FROM predictionsDb.sqlite_master WHERE type='table' AND name='Predictions'", cn))
                    {
                        if (checkTableCmd.ExecuteScalar() != null)
                        {
                            // 予測データを読み込んでDictionaryに格納
                            using var cmdPred = new SQLiteCommand("SELECT Year, MonthDay, JyoCD, RaceNum, Umaban, RankGrade FROM predictionsDb.Predictions", cn);
                            using var reader = cmdPred.ExecuteReader();
                            while (reader.Read())
                            {
                                // 複合キーを生成して格納
                                var key = $"{reader["Year"]}{reader["MonthDay"]}{reader["JyoCD"]}{reader["RaceNum"]}{reader["Umaban"]}";
                                predictions[key] = reader["RankGrade"]?.ToString() ?? "E";
                            }
                            Console.WriteLine($"[DEBUG] {predictions.Count}件の予測データを読み込みました。");
                        }
                        else
                        {
                            Console.WriteLine("[WARN] predictions.dbにPredictionsテーブルが見つかりません。");
                        }
                    }
                    
                    // 用が済んだらデタッチする
                    using (var detachCmd = new SQLiteCommand("DETACH DATABASE predictionsDb", cn))
                    {
                        detachCmd.ExecuteNonQuery();
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"[ERROR] predictions.dbの処理中にエラーが発生しました: {ex.Message}");
                }
            }
            else
            {
                Console.WriteLine($"[INFO] predictions.dbが見つかりません。パス: {predictionsDbPath}");
            }



            static string CoalesceExisting(SQLiteConnection cn, string table, string alias, params string[] candidates)
            {
                var prefix = string.IsNullOrEmpty(alias) ? "" : $"{alias}.";
                var exist = candidates.Where(c => HasCol(cn, table, c)).Select(c => $"{prefix}{c}").ToArray();
                return exist.Length > 0 ? (exist.Length == 1 ? exist[0] : ($"COALESCE({string.Join(", ", exist)})")) : "NULL";
            }

            var exprU = CoalesceExisting(cn, "N_UMA_RACE", "U", "Umaban", "UMABAN", "馬番");
            var exprN = CoalesceExisting(cn, "N_UMA_RACE", "U", "Bamei", "UmaName", "UMANAME", "馬名");
            var exprK = CoalesceExisting(cn, "N_UMA_RACE", "U", "KisyuRyakusyo", "KisyuName", "KisyuNM", "KISYUNM", "騎手名", "騎手");
            var exprF = CoalesceExisting(cn, "N_UMA_RACE", "U", "Futan", "BurdenWeight", "斤量");
            var exprW = CoalesceExisting(cn, "N_UMA_RACE", "U", "Wakuban", "WakuNum", "枠番", "枠");
            var exprTrainer = CoalesceExisting(cn, "N_UMA_RACE", "U", "ChokyosiRyakusyo", "ChokyosiName", "ChokyoShiName", "ChokyosiNM", "Chokyosi", "調教師名", "調教師");
            var exprOwner   = CoalesceExisting(cn, "N_UMA_RACE", "U", "BanusiName", "BanushiName", "BannushiName", "Banushi", "Bannushi", "馬主名", "馬主");

            var exprTrack = CoalesceExisting(cn, "N_RACE", "", "TrackCD", "Course", "Track");
            var exprDist  = CoalesceExisting(cn, "N_RACE", "", "Kyori", "距離");
            var exprClass = CoalesceExisting(cn, "N_RACE", "", "GradeCD", "RaceInfoKubun", "JyokenName");
            var exprTime  = CoalesceExisting(cn, "N_RACE", "", "HassoTime", "発走");
            var exprName  = BuildRaceNameExpr(cn);
            
            var exprHahaChichi = CoalesceExisting(cn, "N_UMA", "UM", "Ketto3InfoBamei2", "母父名");

            // 2. JOINなしでメインのSQLを構築
            var sql =
                $"SELECT U.Year AS idYear, U.MonthDay AS idMonthDay, U.JyoCD AS idJyoCD, U.RaceNum AS idRaceNum, U.Umaban AS idUmaban, " +
                $"       {exprW} AS 枠番, {exprU} AS 馬番, {exprN} AS 馬名, {exprK} AS 騎手, {exprF} AS 斤量, {exprTrainer} AS 調教師, {exprOwner} AS 馬主, " +
                $"       U.Umaban AS {RawUmabanColumn}, " +
                $"       {exprHahaChichi} AS 母父, " +
                $"       U.KettoNum, U.KyakusituKubun AS 脚質, U.ChakusaCD AS 前走, " +
                $"       NULL AS ichaku, NULL AS nichaku, NULL AS sanchaku, NULL AS yonchaku, NULL AS gochaku, " +
                $"       NULL AS win_rate, NULL AS place_rate, NULL AS total_races " +
                "  FROM N_UMA_RACE U " +
                "  LEFT JOIN N_UMA UM ON U.KettoNum = UM.KettoNum " +
                " WHERE U.Year=@y AND U.MonthDay=@md AND U.JyoCD=@j AND U.RaceNum=@r " +
                (exprU != "NULL" ? $" ORDER BY CAST({exprU} AS INTEGER)" : " ORDER BY U.ROWID");

            using var da = new SQLiteDataAdapter(sql, cn);
            da.SelectCommand.Parameters.AddWithValue("@y", k.Year);
            da.SelectCommand.Parameters.AddWithValue("@md", k.MonthDay);
            da.SelectCommand.Parameters.AddWithValue("@j", k.JyoCD);
            da.SelectCommand.Parameters.AddWithValue("@r", k.RaceNum);
            var dt = new DataTable();
            da.Fill(dt);

            // 3. DataTableに予測列を追加し、メモリ上のデータで更新
            dt.Columns.Add("馬評価", typeof(string));
            foreach (DataRow row in dt.Rows)
            {
                var key = $"{row["idYear"]}{row["idMonthDay"]}{row["idJyoCD"]}{row["idRaceNum"]}{row["idUmaban"]}";
                if (predictions.TryGetValue(key, out var rank))
                {
                    row["馬評価"] = rank;
                }
                else
                {
                    // 予測がない場合はオッズ等から簡易評価（既存ロジック）
                    var o = row.Table.Columns.Contains("オッズ") ? (row["オッズ"]?.ToString() ?? "") : "";
                    if (double.TryParse(o, out var v))
                    {
                        row["馬評価"] = v <= 3.0 ? "S" : v <= 5.0 ? "A" : v <= 10.0 ? "B" : "C";
                    }
                    else
                    {
                        row["馬評価"] = "E"; // デフォルト
                    }
                }
            }

            if (dt.Columns.Contains("idYear")) dt.Columns.Remove("idYear");
            if (dt.Columns.Contains("idMonthDay")) dt.Columns.Remove("idMonthDay");
            if (dt.Columns.Contains("idJyoCD")) dt.Columns.Remove("idJyoCD");
            if (dt.Columns.Contains("idRaceNum")) dt.Columns.Remove("idRaceNum");
            if (dt.Columns.Contains("idUmaban")) dt.Columns.Remove("idUmaban");
            if (dt.Columns.Contains("idYear")) dt.Columns.Remove("idYear");
            if (dt.Columns.Contains("idMonthDay")) dt.Columns.Remove("idMonthDay");
            if (dt.Columns.Contains("idJyoCD")) dt.Columns.Remove("idJyoCD");
            if (dt.Columns.Contains("idRaceNum")) dt.Columns.Remove("idRaceNum");

            // まず「オッズ」列を用意（無くても列だけ見せる）
            if (!dt.Columns.Contains("オッズ")) dt.Columns.Add("オッズ", typeof(string));

            // 単勝率・複勝率の列を追加
            if (!dt.Columns.Contains("単勝率")) dt.Columns.Add("単勝率", typeof(string));
            if (!dt.Columns.Contains("複勝率")) dt.Columns.Add("複勝率", typeof(string));

            static bool TryFormatOdds(string? oddsValue, out string formatted)
            {
                formatted = string.Empty;
                if (string.IsNullOrWhiteSpace(oddsValue)) return false;
                if (!int.TryParse(oddsValue, out var oddsInt) || oddsInt <= 0) return false;
                formatted = (oddsInt / 10.0).ToString("F1");
                return true;
            }

            void StoreOdds(IDictionary<string, string> buffer, string? uma, string? oddsValue)
            {
                if (string.IsNullOrWhiteSpace(uma)) return;
                if (!TryFormatOdds(oddsValue, out var formatted)) return;

                var key = uma.Trim();
                if (key.Length == 0) return;
                buffer[key] = formatted;

                var normalized = key.TrimStart('0');
                if (!string.IsNullOrEmpty(normalized))
                {
                    buffer[normalized] = formatted;
                }
            }

            void LoadOddsFromSimpleTable(IDictionary<string, string> buffer, string tableName)
            {
                if (!TableExists(cn, tableName)) return;

                var sqlOdds = $"SELECT Umaban, TanOdds FROM {tableName} WHERE Year=@y AND MonthDay=@md AND JyoCD=@j AND RaceNum=@r";
                using var cmdOdds = new SQLiteCommand(sqlOdds, cn);
                cmdOdds.Parameters.AddWithValue("@y", k.Year);
                cmdOdds.Parameters.AddWithValue("@md", k.MonthDay);
                cmdOdds.Parameters.AddWithValue("@j", k.JyoCD);
                cmdOdds.Parameters.AddWithValue("@r", k.RaceNum);

                using var rdr = cmdOdds.ExecuteReader();
                while (rdr.Read())
                {
                    var uma = rdr["Umaban"]?.ToString();
                    var oddsValue = rdr["TanOdds"]?.ToString();
                    StoreOdds(buffer, uma, oddsValue);
                }
            }

            var tan = new Dictionary<string, string>();
            LoadOddsFromSimpleTable(tan, "N_ODDS_TANPUKU");
            if (tan.Count == 0)
            {
                LoadOddsFromSimpleTable(tan, "S_ODDS_TANPUKU");
            }

            if (tan.Count == 0 && TableExists(cn, "NL_O1_ODDS_TANFUKUWAKU"))
            {
                const int MaxEntries = 27;
                var sqlO1 = @"SELECT
                    OddsTansyoInfo0Umaban as U0, OddsTansyoInfo0Odds as O0,
                    OddsTansyoInfo1Umaban as U1, OddsTansyoInfo1Odds as O1,
                    OddsTansyoInfo2Umaban as U2, OddsTansyoInfo2Odds as O2,
                    OddsTansyoInfo3Umaban as U3, OddsTansyoInfo3Odds as O3,
                    OddsTansyoInfo4Umaban as U4, OddsTansyoInfo4Odds as O4,
                    OddsTansyoInfo5Umaban as U5, OddsTansyoInfo5Odds as O5,
                    OddsTansyoInfo6Umaban as U6, OddsTansyoInfo6Odds as O6,
                    OddsTansyoInfo7Umaban as U7, OddsTansyoInfo7Odds as O7,
                    OddsTansyoInfo8Umaban as U8, OddsTansyoInfo8Odds as O8,
                    OddsTansyoInfo9Umaban as U9, OddsTansyoInfo9Odds as O9,
                    OddsTansyoInfo10Umaban as U10, OddsTansyoInfo10Odds as O10,
                    OddsTansyoInfo11Umaban as U11, OddsTansyoInfo11Odds as O11,
                    OddsTansyoInfo12Umaban as U12, OddsTansyoInfo12Odds as O12,
                    OddsTansyoInfo13Umaban as U13, OddsTansyoInfo13Odds as O13,
                    OddsTansyoInfo14Umaban as U14, OddsTansyoInfo14Odds as O14,
                    OddsTansyoInfo15Umaban as U15, OddsTansyoInfo15Odds as O15,
                    OddsTansyoInfo16Umaban as U16, OddsTansyoInfo16Odds as O16,
                    OddsTansyoInfo17Umaban as U17, OddsTansyoInfo17Odds as O17,
                    OddsTansyoInfo18Umaban as U18, OddsTansyoInfo18Odds as O18,
                    OddsTansyoInfo19Umaban as U19, OddsTansyoInfo19Odds as O19,
                    OddsTansyoInfo20Umaban as U20, OddsTansyoInfo20Odds as O20,
                    OddsTansyoInfo21Umaban as U21, OddsTansyoInfo21Odds as O21,
                    OddsTansyoInfo22Umaban as U22, OddsTansyoInfo22Odds as O22,
                    OddsTansyoInfo23Umaban as U23, OddsTansyoInfo23Odds as O23,
                    OddsTansyoInfo24Umaban as U24, OddsTansyoInfo24Odds as O24,
                    OddsTansyoInfo25Umaban as U25, OddsTansyoInfo25Odds as O25,
                    OddsTansyoInfo26Umaban as U26, OddsTansyoInfo26Odds as O26,
                    OddsTansyoInfo27Umaban as U27, OddsTansyoInfo27Odds as O27
                FROM NL_O1_ODDS_TANFUKUWAKU
                WHERE idYear=@y AND idMonthDay=@md AND idJyoCD=@j AND idRaceNum=@r";

                using var cmdO1 = new SQLiteCommand(sqlO1, cn);
                cmdO1.Parameters.AddWithValue("@y", k.Year);
                cmdO1.Parameters.AddWithValue("@md", k.MonthDay);
                cmdO1.Parameters.AddWithValue("@j", k.JyoCD);
                cmdO1.Parameters.AddWithValue("@r", k.RaceNum);

                using var rdo = cmdO1.ExecuteReader();
                if (rdo.Read())
                {
                    for (var i = 0; i <= MaxEntries; i++)
                    {
                        var uma = rdo[$"U{i}"]?.ToString();
                        var oddsValue = rdo[$"O{i}"]?.ToString();
                        StoreOdds(tan, uma, oddsValue);
                    }
                }
            }

            string? horseNumberColumn = null;
            foreach (var candidate in new[] { "馬番", "Umaban", "UMABAN", RawUmabanColumn })
            {
                if (dt.Columns.Contains(candidate))
                {
                    horseNumberColumn = candidate;
                    break;
                }
            }

            if (tan.Count > 0 && horseNumberColumn != null)
            {
                foreach (DataRow row in dt.Rows)
                {
                    var key = row[horseNumberColumn]?.ToString() ?? string.Empty;
                    var normalized = key.TrimStart('0');
                    if (!string.IsNullOrEmpty(normalized) && tan.TryGetValue(normalized, out var normalizedOdd))
                    {
                        row["オッズ"] = normalizedOdd;
                    }
                    else if (!string.IsNullOrEmpty(key) && tan.TryGetValue(key, out var rawOdd))
                    {
                        row["オッズ"] = rawOdd;
                    }
                }
            }

            if (dt.Columns.Contains(RawUmabanColumn)) dt.Columns.Remove(RawUmabanColumn);
            // 脚質・成績データの処理
            foreach (DataRow row in dt.Rows)
            {
                // 脚質の変換
                if (dt.Columns.Contains("脚質"))
                {
                    var kyakusitu = row["脚質"]?.ToString() ?? "";
                    row["脚質"] = kyakusitu switch
                    {
                        "1" => "逃",
                        "2" => "先",
                        "3" => "差",
                        "4" => "追",
                        _ => kyakusitu
                    };
                }
                
                // 単勝率・複勝率のフォーマット
                if (dt.Columns.Contains("単勝率") && dt.Columns.Contains("複勝率"))
                {
                    var winRate = row["win_rate"]?.ToString() ?? "";
                    var placeRate = row["place_rate"]?.ToString() ?? "";
                    var totalRaces = row["total_races"]?.ToString() ?? "";
                    
                    if (!string.IsNullOrEmpty(winRate) && !string.IsNullOrEmpty(placeRate) && !string.IsNullOrEmpty(totalRaces))
                    {
                        if (double.TryParse(winRate, out var win) && double.TryParse(placeRate, out var place) && int.TryParse(totalRaces, out var races))
                        {
                            row["単勝率"] = $"{win:F1}%";
                            row["複勝率"] = $"{place:F1}%";
                        }
                        else
                        {
                            row["単勝率"] = "-";
                            row["複勝率"] = "-";
                        }
                    }
                    else
                    {
                        row["単勝率"] = "-";
                        row["複勝率"] = "-";
                    }
                }
                
                // 前走成績の変換（血統番号から過去のレース履歴を検索）
                if (dt.Columns.Contains("前走"))
                {
                    var kettoNum = row["KettoNum"]?.ToString() ?? "";
                    var previousResult = GetPreviousRaceResult(cn, kettoNum, k.Year, k.MonthDay);
                    row["前走"] = previousResult;
                }
                
                // 着別度数のフォーマット（1-0-0-0-0 形式、ゼロ詰めなし）
                if (dt.Columns.Contains("ichaku") && dt.Columns.Contains("nichaku") && dt.Columns.Contains("sanchaku") && 
                    dt.Columns.Contains("yonchaku") && dt.Columns.Contains("gochaku"))
                {
                    int v1 = int.TryParse(row["ichaku"]?.ToString(), out var t1) ? t1 : 0;
                    int v2 = int.TryParse(row["nichaku"]?.ToString(), out var t2) ? t2 : 0;
                    int v3 = int.TryParse(row["sanchaku"]?.ToString(), out var t3) ? t3 : 0;
                    int v4 = int.TryParse(row["yonchaku"]?.ToString(), out var t4) ? t4 : 0;
                    int v5 = int.TryParse(row["gochaku"]?.ToString(), out var t5) ? t5 : 0;
                    if (!dt.Columns.Contains("着別度数")) dt.Columns.Add("着別度数", typeof(string));
                    row["着別度数"] = $"{v1}-{v2}-{v3}-{v4}-{v5}";
                }
            }

            // 馬評価列を追加（簡易: オッズに基づく閾値）
            if (!dt.Columns.Contains("馬評価")) dt.Columns.Add("馬評価", typeof(string));
            foreach (DataRow row in dt.Rows)
            {
                var o = row.Table.Columns.Contains("オッズ") ? (row["オッズ"]?.ToString() ?? "") : "";
                if (double.TryParse(o, out var v))
                {
                    row["馬評価"] = v <= 3.0 ? "S" : v <= 5.0 ? "A" : v <= 10.0 ? "B" : "C";
                }
                else
                {
                    row["馬評価"] = "-";
                }
            }

            // 不要な中間列を削除
            if (dt.Columns.Contains("ichaku")) dt.Columns.Remove("ichaku");
            if (dt.Columns.Contains("nichaku")) dt.Columns.Remove("nichaku");
            if (dt.Columns.Contains("sanchaku")) dt.Columns.Remove("sanchaku");
            if (dt.Columns.Contains("yonchaku")) dt.Columns.Remove("yonchaku");
            if (dt.Columns.Contains("gochaku")) dt.Columns.Remove("gochaku");

            // 馬評価列を追加（予測テーブルから取得）
            if (!dt.Columns.Contains("馬評価")) dt.Columns.Add("馬評価", typeof(string));
            foreach (DataRow row in dt.Rows)
            {
                var rankGrade = row.Table.Columns.Contains("RankGrade") ? (row["RankGrade"]?.ToString() ?? "E") : "E";
                row["馬評価"] = rankGrade;
            }
            
            // 列順: 枠番, 馬番, 馬評価, 馬名, 騎手, 斤量, オッズ, 単勝率, 複勝率, 調教師, 馬主, 母父, 脚質, 前走, 着別度数
            if (dt.Columns.Contains("馬評価")) dt.Columns["馬評価"]?.SetOrdinal(Math.Min(dt.Columns.Count - 1, 2));
            if (dt.Columns.Contains("オッズ")) dt.Columns["オッズ"]?.SetOrdinal(Math.Min(dt.Columns.Count - 1, 6));
            if (dt.Columns.Contains("単勝率")) dt.Columns["単勝率"]?.SetOrdinal(Math.Min(dt.Columns.Count - 1, 7));
            if (dt.Columns.Contains("複勝率")) dt.Columns["複勝率"]?.SetOrdinal(Math.Min(dt.Columns.Count - 1, 8));
            if (dt.Columns.Contains("調教師")) dt.Columns["調教師"]?.SetOrdinal(Math.Min(dt.Columns.Count - 1, 9));
            if (dt.Columns.Contains("馬主")) dt.Columns["馬主"]?.SetOrdinal(Math.Min(dt.Columns.Count - 1, 10));
            if (dt.Columns.Contains("母父")) dt.Columns["母父"]?.SetOrdinal(Math.Min(dt.Columns.Count - 1, 11));
            if (dt.Columns.Contains("脚質")) dt.Columns["脚質"]?.SetOrdinal(Math.Min(dt.Columns.Count - 1, 12));
            if (dt.Columns.Contains("前走")) dt.Columns["前走"]?.SetOrdinal(Math.Min(dt.Columns.Count - 1, 13));
            if (dt.Columns.Contains("着別度数")) dt.Columns["着別度数"]?.SetOrdinal(Math.Min(dt.Columns.Count - 1, 14));

                        // v_prev12_nl から前走欄を補完（ビューが存在する場合のみ）
            try
            {
                string prevCol = dt.Columns.Contains("前走") ? "前走" :
                                  dt.Columns.Cast<DataColumn>().Select(c => c.ColumnName)
                                      .FirstOrDefault(n => n.Contains("前") || n.Contains("O")) ?? string.Empty;
                if (!string.IsNullOrEmpty(prevCol))
                {
                    using var cmdPrev2 = new SQLiteCommand(@"SELECT
                            Year as prev1_year, MonthDay as prev1_monthday, JyoCD as prev1_jyo, RaceNum as prev1_race,
                            KakuteiJyuni as prev1_finish, DochakuTosu as prev1_field_size,
                            Jyuni1c as prev1_corner1, Jyuni2c as prev1_corner2, Jyuni3c as prev1_corner3, Jyuni4c as prev1_corner4
                          FROM N_UMA_RACE
                          WHERE KettoNum=@k
                          AND (Year < @y OR (Year = @y AND MonthDay < @md))
                          ORDER BY Year DESC, MonthDay DESC
                          LIMIT 1", cn);
                    foreach (DataRow row2 in dt.Rows)
                    {
                        var kNum = row2["KettoNum"]?.ToString() ?? string.Empty;
                        string text = "データなし";
                        if (!string.IsNullOrEmpty(kNum))
                        {
                            cmdPrev2.Parameters.Clear();
                            cmdPrev2.Parameters.AddWithValue("@y", k.Year);
                            cmdPrev2.Parameters.AddWithValue("@md", k.MonthDay);
                            cmdPrev2.Parameters.AddWithValue("@j", k.JyoCD);
                            cmdPrev2.Parameters.AddWithValue("@r", k.RaceNum);
                            cmdPrev2.Parameters.AddWithValue("@k", kNum);
                            using var rdp2 = cmdPrev2.ExecuteReader();
                            if (rdp2.Read())
                            {
                                string py   = rdp2[0]?.ToString() ?? "";
                                string pmd  = rdp2[1]?.ToString() ?? "";
                                string pj   = rdp2[2]?.ToString() ?? "";
                                string pr   = rdp2[3]?.ToString() ?? "";
                                string fin  = rdp2[4]?.ToString() ?? "";
                                string head = rdp2[5]?.ToString() ?? "";
                                if (string.IsNullOrEmpty(head) || head == "0")
                                {
                                    using var cnt = new SQLiteCommand(@"SELECT COUNT(*) FROM N_UMA_RACE WHERE Year=@py AND MonthDay=@pmd AND JyoCD=@pj AND RaceNum=@pr", cn);
                                    cnt.Parameters.AddWithValue("@py", py);
                                    cnt.Parameters.AddWithValue("@pmd", pmd);
                                    cnt.Parameters.AddWithValue("@pj", pj);
                                    cnt.Parameters.AddWithValue("@pr", pr);
                                    head = Convert.ToString(cnt.ExecuteScalar() ?? "0") ?? "0";
                                }
                                if (!string.IsNullOrEmpty(py))
                                {
                                    var date = py + pmd;
                                    var finTxt = InterpretKakuteiChakujun(fin);
                                    text = $"{date} {pj} {pr}R {finTxt}/{head}";
                                }
                            }
                        }
                        row2[prevCol] = text;
                    }
                }
            }
            catch
            {
                // ビューが無い場合は従来の値を使用
            }

            grid.DataSource = dt;

            // 上部ラベルにレース概要（指定フォーマット）
            string nameText = "";
            string distText = "";
            string trackText = "";
            string classText = "";
            string timeText = "";
            string kaijiText = "";
            string nichijiText = "";
            using (var cmdTime = new SQLiteCommand($"SELECT {exprName} AS N, {exprDist} AS D, {exprTrack} AS T, {exprClass} AS C, {exprTime} AS H FROM N_RACE WHERE Year=@y AND MonthDay=@md AND JyoCD=@j AND RaceNum=@r", cn))
            {
                cmdTime.Parameters.AddWithValue("@y", k.Year);
                cmdTime.Parameters.AddWithValue("@md", k.MonthDay);
                cmdTime.Parameters.AddWithValue("@j", k.JyoCD);
                cmdTime.Parameters.AddWithValue("@r", k.RaceNum);
                using var rd = cmdTime.ExecuteReader();
                if (rd.Read())
                {
                    nameText  = rd["N"]?.ToString() ?? "";
                    distText  = rd["D"]?.ToString() ?? "";
                    trackText = rd["T"]?.ToString() ?? "";
                    classText = rd["C"]?.ToString() ?? "";
                    timeText  = rd["H"]?.ToString() ?? "";
                }
            }
            // Kaiji/Nichiji があれば取得
            string exprKaiji = CoalesceExisting(cn, "N_RACE", "Kaiji");
            string exprNichiji = CoalesceExisting(cn, "N_RACE", "Nichiji");
            if (exprKaiji != "NULL" || exprNichiji != "NULL")
            {
                using var cmdKN = new SQLiteCommand($"SELECT {exprKaiji} AS KJ, {exprNichiji} AS NJ FROM N_RACE WHERE Year=@y AND MonthDay=@md AND JyoCD=@j AND RaceNum=@r", cn);
                cmdKN.Parameters.AddWithValue("@y", k.Year);
                cmdKN.Parameters.AddWithValue("@md", k.MonthDay);
                cmdKN.Parameters.AddWithValue("@j", k.JyoCD);
                cmdKN.Parameters.AddWithValue("@r", k.RaceNum);
                using var rd2 = cmdKN.ExecuteReader();
                if (rd2.Read())
                {
                    kaijiText = rd2["KJ"]?.ToString() ?? "";
                    nichijiText = rd2["NJ"]?.ToString() ?? "";
                }
            }

            // 日付（yyyy年MM月dd日）
            string mm = (k.MonthDay?.Length >= 2) ? k.MonthDay.Substring(0, 2) : "";
            string dd = (k.MonthDay?.Length >= 4) ? k.MonthDay.Substring(2, 2) : "";
            var dateText = $"{k.Year}年{mm}月{dd}日";

            // 発送時刻 HH：MM（全角コロン表記）
            string hhmm = timeText;
            if (!string.IsNullOrWhiteSpace(timeText))
            {
                var t = timeText.Replace(":", "");
                if (t.Length >= 4)
                {
                    hhmm = t.Substring(0, 2) + "：" + t.Substring(2, 2);
                }
            }

            var jName = jyoMap.TryGetValue(k.JyoCD, out var nm2) ? nm2 : k.JyoCD;
            var line1 = $"{dateText}　第{kaijiText}回{jName}競馬　{nichijiText}日目　発送時刻　{hhmm}".Trim();
            var line2 = $"{k.RaceNum}R　（{nameText}）".Trim();
            var line3 = $"（{TranslateTrack(trackText)}）{distText}ｍ".Trim();
            lblSummary.Text = line1 + "\r\n" + line2 + "\r\n" + line3;

            // 列幅（ピクセル固定）: 枠番/馬番小、馬名広、騎手中、斤量小、オッズ中、単勝率/複勝率小、調教師/馬主やや広め
            int col = 0;
            if (grid.Columns.Count > col) { var c = grid.Columns[col++]!; c.AutoSizeMode = DataGridViewAutoSizeColumnMode.None; c.Width = 50; } // 枠番
            if (grid.Columns.Count > col) { var c = grid.Columns[col++]!; c.AutoSizeMode = DataGridViewAutoSizeColumnMode.None; c.Width = 50; } // 馬番
            if (grid.Columns.Count > col) { var c = grid.Columns[col++]!; c.AutoSizeMode = DataGridViewAutoSizeColumnMode.None; c.Width = 60; }  // 馬評価
            if (grid.Columns.Count > col) { var c = grid.Columns[col++]!; c.AutoSizeMode = DataGridViewAutoSizeColumnMode.None; c.Width = 280; } // 馬名
            if (grid.Columns.Count > col) { var c = grid.Columns[col++]!; c.AutoSizeMode = DataGridViewAutoSizeColumnMode.None; c.Width = 160; } // 騎手
            if (grid.Columns.Count > col) { var c = grid.Columns[col++]!; c.AutoSizeMode = DataGridViewAutoSizeColumnMode.None; c.Width = 60; }  // 斤量
            if (grid.Columns.Count > col && grid.Columns[col].Name == "オッズ") { var c = grid.Columns[col++]!; c.AutoSizeMode = DataGridViewAutoSizeColumnMode.None; c.Width = 80; } // オッズ
            if (grid.Columns.Count > col && grid.Columns[col].Name == "単勝率") { var c = grid.Columns[col++]!; c.AutoSizeMode = DataGridViewAutoSizeColumnMode.None; c.Width = 70; } // 単勝率
            if (grid.Columns.Count > col && grid.Columns[col].Name == "複勝率") { var c = grid.Columns[col++]!; c.AutoSizeMode = DataGridViewAutoSizeColumnMode.None; c.Width = 70; } // 複勝率
            if (grid.Columns.Count > col) { var c = grid.Columns[col++]!; c.AutoSizeMode = DataGridViewAutoSizeColumnMode.None; c.Width = 160; } // 調教師
            if (grid.Columns.Count > col) { var c = grid.Columns[col++]!; c.AutoSizeMode = DataGridViewAutoSizeColumnMode.None; c.Width = 180; } // 馬主

            var jName2 = jyoMap.TryGetValue(k.JyoCD, out var nm) ? nm : k.JyoCD;
            lbl.Text = $"{k.Year}-{k.MonthDay} {jName2} {k.RaceNum}R：{dt.Rows.Count}頭";
        }

        private readonly record struct RaceKey(string Year, string MonthDay, string JyoCD, string RaceNum);


        private static string GetPreviousRaceResult(SQLiteConnection cn, string kettoNum, string currentYear, string currentMonthDay)
        {
            if (string.IsNullOrEmpty(kettoNum)) return "データなし";

            try
            {
                // 過去のレース結果を検索（現在のレースより前）
                using var cmd = new SQLiteCommand(@"
                    SELECT 
                        Year,
                        MonthDay,
                        JyoCD,
                        RaceNum,
                        Umaban,
                        ChakusaCD,
                        Time,
                        DochakuTosu,
                        KakuteiJyuni
                    FROM N_UMA_RACE 
                    WHERE KettoNum = @kettoNum 
                    AND (Year < @currentYear OR (Year = @currentYear AND MonthDay < @currentMonthDay))
                    ORDER BY Year DESC, MonthDay DESC, JyoCD DESC, RaceNum DESC
                    LIMIT 1", cn);

                cmd.Parameters.AddWithValue("@kettoNum", kettoNum);
                cmd.Parameters.AddWithValue("@currentYear", currentYear);
                cmd.Parameters.AddWithValue("@currentMonthDay", currentMonthDay);

                using var reader = cmd.ExecuteReader();
                if (reader.Read())
                {
                    var kakuteiChakujun = reader["KakuteiJyuni"]?.ToString() ?? "";
                    var dochakuTosu = reader["DochakuTosu"]?.ToString() ?? "";
                    var raceYear = reader["Year"]?.ToString() ?? "";
                    var raceMonthDay = reader["MonthDay"]?.ToString() ?? "";
                    var raceJyoCD = reader["JyoCD"]?.ToString() ?? "";
                    var raceNum = reader["RaceNum"]?.ToString() ?? "";
                    
                    using (var countCmd = new SQLiteCommand(@"
                        SELECT COUNT(*) FROM N_UMA_RACE 
                        WHERE Year = @year AND MonthDay = @monthDay AND JyoCD = @jyoCD AND RaceNum = @raceNum", cn))
                    {
                        countCmd.Parameters.AddWithValue("@year", raceYear);
                        countCmd.Parameters.AddWithValue("@monthDay", raceMonthDay);
                        countCmd.Parameters.AddWithValue("@jyoCD", raceJyoCD);
                        countCmd.Parameters.AddWithValue("@raceNum", raceNum);
                        var totalHorses = Convert.ToInt32(countCmd.ExecuteScalar() ?? 0);
                        return FormatPrevResult(kakuteiChakujun, totalHorses);
                    }
                }
                else
                {
                    return "データなし";
                }
            }
            catch (Exception ex)
            {
                return $"エラー: {ex.Message}";
            }
        }

        // 互換用オーバーロード（JyoCD, RaceNum は使用せず無視する）
        private static string GetPreviousRaceResult(SQLiteConnection cn, string kettoNum, string currentYear, string currentMonthDay, string jyoCD, string raceNum)
        {
            return GetPreviousRaceResult(cn, kettoNum, currentYear, currentMonthDay);
        }
        private static string InterpretKakuteiChakujun(string kakuteiChakujun)
        {
            if (string.IsNullOrEmpty(kakuteiChakujun) || kakuteiChakujun == "0")
                return "-"; // 不明は「-」

            if (int.TryParse(kakuteiChakujun, out var num) && num > 0)
                return $"{num}着";

            return kakuteiChakujun switch
            {
                "H" => "取消",
                "K" => "除外",
                "A" or "B" or "C" or "D" => "失格",
                _ => "-"
            };
        }


        // 着別度数和確定順位で表示するフォーマッタ
        private static string FormatPrevResult(string kakuteiJyuniRaw, int totalHorses)
        {
            if (string.IsNullOrWhiteSpace(kakuteiJyuniRaw)) return "-";

            // 先頭ゼロを許容（01 など）
            if (int.TryParse(kakuteiJyuniRaw, out var n))
            {
                if (n <= 0) return "-";
                return $"{n}着({kakuteiJyuniRaw})/{totalHorses}頭中";
            }

            // 記号コード
            return kakuteiJyuniRaw switch
            {
                "H" => "除外",
                "K" => "取消",
                "A" or "B" or "C" or "D" => "除外",
                _ => "-"
            };
        }

        private static string InterpretChakusaCD(string chakusaCD)
        {
            if (string.IsNullOrEmpty(chakusaCD))
                return "データなし";

            // 文字の場合（除外・取消）
            if (chakusaCD.Length == 1 && "HKABCD".Contains(chakusaCD))
            {
                return chakusaCD switch
                {
                    "H" => "除外",
                    "K" => "取消",
                    "A" => "除外",
                    "B" => "除外",
                    "C" => "除外",
                    "D" => "除外",
                    _ => chakusaCD
                };
            }

            // 数字の場合
            if (chakusaCD.All(char.IsDigit))
            {
                if (chakusaCD.Length == 1)
                {
                    // 1桁の場合
                    return $"{chakusaCD}着";
                }
                else if (chakusaCD.Length >= 2)
                {
                    // 2桁以上の場合、最初の桁を着順として解釈
                    var firstDigit = chakusaCD[0];
                    if (firstDigit >= '1' && firstDigit <= '9')
                    {
                        return $"{firstDigit}着";
                    }
                }
            }

            return chakusaCD;
        }

        private void Grid_CellDoubleClick(object? sender, DataGridViewCellEventArgs e)
        {
            try
            {
                if (e.RowIndex < 0 || grid.DataSource is not DataTable dt || e.RowIndex >= dt.Rows.Count)
                    return;

                var row = dt.Rows[e.RowIndex];
                var kettoNum = row["KettoNum"]?.ToString() ?? "";
                var horseName = row["馬名"]?.ToString() ?? "";

                if (string.IsNullOrEmpty(kettoNum) || string.IsNullOrEmpty(horseName))
                {
                    MessageBox.Show("馬の情報が不足しています。", "エラー", 
                        MessageBoxButtons.OK, MessageBoxIcon.Warning);
                    return;
                }

                // 馬詳細フォームを開く（ecore.dbのパスを使用）
                var horseDetailForm = new HorseDetailForm(_dbPath, kettoNum, horseName);
                horseDetailForm.Show();
            }
            catch (Exception ex)
            {
                MessageBox.Show($"馬詳細画面を開く際にエラーが発生しました: {ex.Message}", "エラー", 
                    MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }
    }
}

