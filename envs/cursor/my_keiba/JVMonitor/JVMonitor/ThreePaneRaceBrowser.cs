using System;
using System.Collections.Generic;
using System.Data;
using System.Data.SQLite;
using System.Drawing;
using System.Linq;
using System.Windows.Forms;

namespace JVMonitor
{
    public sealed class ThreePaneRaceBrowser : Form
    {
        readonly string _dbPath;

        SplitContainer scLeftRight;   // 左(開催日) / 右(開催場+出馬表)
        SplitContainer scMidRight;    // 中(開催場/レース) / 右(出馬表)
        ListView lvDays;              // 開催日
        TreeView tvMeetings;          // 開催場(親)→レース(子)
        DataGridView grid;            // 出馬表
        StatusStrip status; ToolStripStatusLabel lbl;

        readonly Dictionary<string,string> jyoMap = new()
        {
            {"01","札幌"},{"02","函館"},{"03","福島"},{"04","新潟"},{"05","東京"},
            {"06","中山"},{"07","中京"},{"08","京都"},{"09","阪神"},{"10","小倉"}
        };

        public ThreePaneRaceBrowser(string dbPath)
        {
            _dbPath = dbPath;

            Text = "番組ブラウザ（3ペイン）";
            Width = 1200; Height = 750;

            // レイアウト（左右分割→さらに右側を左右分割）
            scLeftRight = new SplitContainer { Dock = DockStyle.Fill, Orientation = Orientation.Vertical, SplitterDistance = 240 };
            scMidRight  = new SplitContainer { Dock = DockStyle.Fill, Orientation = Orientation.Vertical, SplitterDistance = 420 };

            // 左：開催日
            lvDays = new ListView { Dock = DockStyle.Fill, View = View.Details, FullRowSelect = true };
            lvDays.Columns.Add("開催日", 180);
            lvDays.ItemActivate += (s,e) => LoadMeetingsOfSelectedDay();

            // 中：開催場→レース
            tvMeetings = new TreeView { Dock = DockStyle.Fill };
            tvMeetings.AfterSelect += (s,e) => { if (e.Node?.Tag is RaceKey rk) LoadEntries(rk); };

            // 右：出馬表
            grid = new DataGridView {
                Dock = DockStyle.Fill, ReadOnly = true,
                AllowUserToAddRows = false,
                AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.AllCells
            };

            // ステータスバー
            status = new StatusStrip();
            lbl = new ToolStripStatusLabel("準備中…");
            status.Items.Add(lbl);

            // 配置
            scLeftRight.Panel1.Controls.Add(lvDays);
            scMidRight.Panel1.Controls.Add(tvMeetings);
            scMidRight.Panel2.Controls.Add(grid);
            scLeftRight.Panel2.Controls.Add(scMidRight);
            Controls.Add(scLeftRight);
            Controls.Add(status);

            Shown += (_,__) => LoadRecentDays();
        }

        // ---------- DBユーティリティ ----------
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
        static string Pick(SQLiteConnection cn, string table, params string[] candidates)
            => candidates.FirstOrDefault(c => HasCol(cn, table, c)) ?? candidates[0];

        static string BuildRaceNameExpr(SQLiteConnection cn)
        {
            var nameCols = new[] { "RaceName", "RaceNameJ", "Racename", "レース名" };
            var hondai = HasCol(cn, "NL_RA_RACE", "RaceInfoHondai");
            var fukudai = HasCol(cn, "NL_RA_RACE", "RaceInfoFukudai");
            if (hondai && fukudai) return "COALESCE(RaceInfoHondai || ' ' || RaceInfoFukudai, RaceInfoHondai)";
            if (hondai) return "RaceInfoHondai";
            var first = nameCols.FirstOrDefault(c => HasCol(cn, "NL_RA_RACE", c));
            return first ?? "CAST(idRaceNum AS TEXT)";
        }

        // ---------- 左ペイン：開催日 ----------
        void LoadRecentDays()
        {
            lvDays.Items.Clear();
            using var cn = Open();
            using var cmd = new SQLiteCommand(
                "SELECT DISTINCT idYear, idMonthDay FROM NL_RA_RACE " +
                "ORDER BY idYear DESC, idMonthDay DESC LIMIT 365", cn);
            using var rd = cmd.ExecuteReader();
            while (rd.Read())
            {
                var y = rd["idYear"]?.ToString();
                var md = rd["idMonthDay"]?.ToString();
                if (string.IsNullOrEmpty(y) || string.IsNullOrEmpty(md) || md.Length < 4) continue;
                var dt = DateTime.Parse($"{y}-{md[..2]}-{md[2..]}");
                var it = new ListViewItem(dt.ToString("yyyy/MM/dd")) { Tag = (y, md) };
                lvDays.Items.Add(it);
            }
            if (lvDays.Items.Count > 0) { lvDays.Items[0].Selected = true; LoadMeetingsOfSelectedDay(); }
            lbl.Text = $"開催日: {lvDays.Items.Count} 件";
        }

        // ---------- 中ペイン：開催場→レース ----------
        void LoadMeetingsOfSelectedDay()
        {
            tvMeetings.BeginUpdate();
            tvMeetings.Nodes.Clear();
            grid.DataSource = null;
            if (lvDays.SelectedItems.Count == 0) { tvMeetings.EndUpdate(); return; }
            var (y, md) = ((string y, string md))lvDays.SelectedItems[0].Tag;

            using var cn = Open();
            // レース名式（環境差対応）
            var raceNameExpr = BuildRaceNameExpr(cn);
            bool hasTime = HasCol(cn, "NL_RA_RACE", "HassoTime");

            // 開催場ごとにノード生成
            using var cmdJ = new SQLiteCommand(
                "SELECT DISTINCT idJyoCD FROM NL_RA_RACE WHERE idYear=@y AND idMonthDay=@md ORDER BY idJyoCD", cn);
            cmdJ.Parameters.AddWithValue("@y", y); cmdJ.Parameters.AddWithValue("@md", md);
            using var rdJ = cmdJ.ExecuteReader();
            while (rdJ.Read())
            {
                var j = rdJ["idJyoCD"]?.ToString() ?? "";
                var jName = jyoMap.TryGetValue(j, out var nm) ? nm : j;
                var parent = new TreeNode($"{jName}（{j}）") { Tag = (y, md, j) };
                tvMeetings.Nodes.Add(parent);

                using var cmdR = new SQLiteCommand(
                    $"SELECT idRaceNum, {raceNameExpr} AS RN" +
                    (hasTime ? ", HassoTime" : "") +
                    " FROM NL_RA_RACE WHERE idYear=@y AND idMonthDay=@md AND idJyoCD=@j ORDER BY CAST(idRaceNum AS INTEGER)", cn);
                cmdR.Parameters.AddWithValue("@y", y);
                cmdR.Parameters.AddWithValue("@md", md);
                cmdR.Parameters.AddWithValue("@j", j);

                using var rdR = cmdR.ExecuteReader();
                while (rdR.Read())
                {
                    var r = rdR["idRaceNum"]?.ToString() ?? "";
                    var nm2 = rdR["RN"]?.ToString() ?? "";
                    var tm = hasTime ? $" [{rdR["HassoTime"]}]" : "";
                    var child = new TreeNode($"{r}R {nm2}{tm}") { Tag = new RaceKey(y, md, j, r) };
                    parent.Nodes.Add(child);
                }
                parent.Expand();
            }
            tvMeetings.EndUpdate();
            lbl.Text = $"{y}/{md}: 場 {tvMeetings.Nodes.Count}";
        }

        // ---------- 右ペイン：出馬表 ----------
        void LoadEntries(RaceKey k)
        {
            using var cn = Open();

            var colU = Pick(cn, "NL_SE_RACE_UMA", "Umaban","UMABAN","馬番");
            var colN = Pick(cn, "NL_SE_RACE_UMA", "Bamei","UmaName","UMANAME","馬名");
            var colK = Pick(cn, "NL_SE_RACE_UMA", "KisyuName","KisyuNM","KISYUNM","騎手名","騎手");
            var colF = Pick(cn, "NL_SE_RACE_UMA", "BurdenWeight","Futan","斤量");

            var sql = $"SELECT {colU} AS 馬番, {colN} AS 馬名, {colK} AS 騎手, {colF} AS 斤量 " +
                      "FROM NL_SE_RACE_UMA " +
                      "WHERE idYear=@y AND idMonthDay=@md AND idJyoCD=@j AND idRaceNum=@r " +
                      $"ORDER BY CAST({colU} AS INTEGER)";

            using var da = new SQLiteDataAdapter(sql, cn);
            da.SelectCommand.Parameters.AddWithValue("@y",  k.Year);
            da.SelectCommand.Parameters.AddWithValue("@md", k.MonthDay);
            da.SelectCommand.Parameters.AddWithValue("@j",  k.Jyo);
            da.SelectCommand.Parameters.AddWithValue("@r",  k.Race);
            var dt = new DataTable();
            da.Fill(dt);
            grid.DataSource = dt;

            var jName = jyoMap.TryGetValue(k.Jyo, out var nm) ? nm : k.Jyo;
            lbl.Text = $"{k.Year}-{k.MonthDay} {jName} {k.Race}R：{dt.Rows.Count}頭";
        }

        readonly record struct RaceKey(string Year, string MonthDay, string Jyo, string Race);
    }
}
