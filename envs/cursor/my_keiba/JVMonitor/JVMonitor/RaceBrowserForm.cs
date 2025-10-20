using System;
using System.Collections.Generic;
using System.Data;
using System.Data.SQLite;
using System.Linq;
using System.Windows.Forms;

namespace JVMonitor
{
    public partial class RaceBrowserForm : Form
    {
        private readonly string _dbPath;
        private readonly string _kaisaiDate; // yyyyMMdd
        private readonly string[] _venues;   // ex. ["01","06"]

        public RaceBrowserForm(string dbPath, DateTime kaisai, string[] venues)
        {
            InitializeComponent();
            _dbPath = dbPath;
            _kaisaiDate = kaisai.ToString("yyyyMMdd");
            _venues = venues;
            LoadRaces();
        }

        private static string JyoName(string cd)
        {
            return cd switch
            {
                "01" => "札幌",
                "02" => "函館",
                "03" => "福島",
                "04" => "新潟",
                "05" => "東京",
                "06" => "中山",
                "07" => "中京",
                "08" => "京都",
                "09" => "阪神",
                "10" => "小倉",
                _ => cd
            };
        }

        private void LoadRaces()
        {
            using var cn = new SQLiteConnection($"Data Source={_dbPath};Version=3;");
            cn.Open();
            var inClause = string.Join(",", _venues.Select(v => "'" + v + "'"));
            var sql = $@"
SELECT idJyoCD, idRaceNum, 
       COALESCE(RaceInfoRyakusyo10, RaceInfoHondai) AS RaceName,
       CASE TrackCD WHEN '10' THEN '芝' WHEN '20' THEN 'ダ' ELSE TrackCD END AS Track,
       Kyori AS Distance,
       HassoTime
FROM NL_RA_RACE
WHERE idYear = substr('{_kaisaiDate}',1,4)
  AND idMonthDay = substr('{_kaisaiDate}',5,4)
  AND idJyoCD IN ({inClause})
ORDER BY idJyoCD, CAST(idRaceNum AS INTEGER);
";
            var da = new SQLiteDataAdapter(sql, cn);
            var dt = new DataTable();
            da.Fill(dt);
            // 表示用に日本語列へ差し替え
            var display = new DataTable();
            display.Columns.Add("場");
            display.Columns.Add("R");
            display.Columns.Add("レース名");
            display.Columns.Add("コース");
            display.Columns.Add("距離(m)");
            display.Columns.Add("発走");
            foreach (DataRow r in dt.Rows)
            {
                display.Rows.Add(JyoName(r["idJyoCD"].ToString() ?? ""), r["idRaceNum"], r["RaceName"], r["Track"], r["Distance"], r["HassoTime"]);
            }
            gridRaces.DataSource = display;
        }

        private void gridRaces_SelectionChanged(object sender, EventArgs e)
        {
            if (gridRaces.CurrentRow == null) return;
            var jyoName = gridRaces.CurrentRow.Cells["場"].Value?.ToString() ?? "";
            // 逆引きコード
            var jyo = new Dictionary<string, string>{{"札幌","01"},{"函館","02"},{"福島","03"},{"新潟","04"},{"東京","05"},{"中山","06"},{"中京","07"},{"京都","08"},{"阪神","09"},{"小倉","10"}};
            var cd = jyo.ContainsKey(jyoName) ? jyo[jyoName] : jyoName;
            var r = gridRaces.CurrentRow.Cells["R"].Value?.ToString() ?? "";
            LoadEntries(cd, r);
        }

        private HashSet<string> GetColumns(SQLiteConnection cn, string table)
        {
            using var cmd = new SQLiteCommand($"PRAGMA table_info({table})", cn);
            using var rd = cmd.ExecuteReader();
            var set = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            while (rd.Read()) set.Add(rd[1].ToString() ?? "");
            return set;
        }

        private void LoadEntries(string jyo, string race)
        {
            using var cn = new SQLiteConnection($"Data Source={_dbPath};Version=3;");
            cn.Open();
            var cols = GetColumns(cn, "NL_SE_RACE_UMA");
            string selWaku = cols.Contains("WakuNum") ? "WakuNum AS 枠" : "'' AS 枠";
            string selUma = cols.Contains("Bamei") ? "Bamei AS 馬名" : (cols.Contains("UmaName") ? "UmaName AS 馬名" : "'' AS 馬名");
            string selJockey = cols.Contains("KisyuName") ? "KisyuName AS 騎手" : (cols.Contains("KisyuNM") ? "KisyuNM AS 騎手" : "'' AS 騎手");
            string selWeight = cols.Contains("BurdenWeight") ? "BurdenWeight AS 斤量" : (cols.Contains("Futan") ? "Futan AS 斤量" : "'' AS 斤量");
            string selBody = cols.Contains("Bataijyu") ? "Bataijyu AS 馬体重" : "'' AS 馬体重";
            string selZogen = (cols.Contains("Zogen") && cols.Contains("ZogenFugo")) ? "(ZogenFugo || Zogen) AS 増減" : "'' AS 増減";

            var sql = $@"
SELECT 
   {selWaku}, Umaban AS 馬番, {selUma}, {selJockey}, {selWeight}, {selBody}, {selZogen}
FROM NL_SE_RACE_UMA
WHERE idYear = substr('{_kaisaiDate}',1,4)
  AND idMonthDay = substr('{_kaisaiDate}',5,4)
  AND idJyoCD = @j
  AND idRaceNum = @r
ORDER BY CAST(Umaban AS INTEGER);
";
            var da = new SQLiteDataAdapter(sql, cn);
            da.SelectCommand.Parameters.AddWithValue("@j", jyo);
            da.SelectCommand.Parameters.AddWithValue("@r", race);
            var dt = new DataTable();
            da.Fill(dt);
            gridEntries.DataSource = dt;
        }
    }
}
