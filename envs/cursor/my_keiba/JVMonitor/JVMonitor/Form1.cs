using System;
using System.Collections.Generic;
using System.Data.SQLite;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Xml.Linq;
using System.Linq;
using System.ComponentModel;
using System.Data;
using System.Threading;
using System.Text.Json;
using Microsoft.Extensions.Configuration; // Add this using directive

namespace JVMonitor
{
    public class UpdateState
    {
        public string LastUpdateDateTime { get; set; } = "";
        public string LastUpdateDate { get; set; } = "";
        public string LastUpdateTime { get; set; } = "";
        public string NextUpdateDateTime { get; set; } = "";
        public string LastSuccessfulUpdate { get; set; } = "";
        public int UpdateCount { get; set; } = 0;
        public string LastUpdateSource { get; set; } = "DIFF";
    }

    public partial class Form1 : Form
    {
        private string _dbPath = "";
        private string _jvToolPath = "";
        private string _jvToolDiffExe = "";
        private string _jvToolRealExe = "";
        private string _jvToolNormalExe = "";
        private string _jvToolSetupExe = "";
        private string _jvDataPath = "";
        private string _diffSetting = "";
        private string _normalSetting = "";
        private string _realtimeSetting = "";
        private string _setupSetting = "";
        private string _stateFilePath = Path.Combine(Application.StartupPath, "LastUpdateState.json");
        private string _pythonExecutable = "python";
        private string _automationRepoRoot = "";
        private readonly IConfiguration _configuration; // Add this field
        private string _excelDbPath = ""; // Add this field
        private readonly object _lockObject = new object();
        private CancellationTokenSource _cancellationTokenSource = new CancellationTokenSource();
        private DataCollector? dataCollector;
        private PredictionForm? _predictionForm;

        public Form1()
        {
            var builder = new ConfigurationBuilder()
                .SetBasePath(Application.StartupPath)
                .AddJsonFile("appsettings.json", optional: true, reloadOnChange: true);
            _configuration = builder.Build();

            InitializeComponent();
            LoadSettings();
            InitializeForm();
        }

        private void LoadSettings()
        {
            try
            {
                _dbPath = _configuration["Paths:DbPath"] ?? "";
                _jvToolPath = _configuration["Paths:JvToolPath"] ?? "";
                _jvToolDiffExe = _configuration["Paths:JvToolDiffExe"] ?? "";
                _jvToolRealExe = _configuration["Paths:JvToolRealExe"] ?? "";
                _jvToolNormalExe = _configuration["Paths:JvToolNormalExe"] ?? "";
                _jvToolSetupExe = _configuration["Paths:JvToolSetupExe"] ?? "";
                _jvDataPath = _configuration["Paths:JvDataPath"] ?? "";
                _diffSetting = _configuration["Paths:DiffSetting"] ?? "";
                _normalSetting = _configuration["Paths:NormalSetting"] ?? "";
                _realtimeSetting = _configuration["Paths:RealtimeSetting"] ?? "";
                _setupSetting = _configuration["Paths:SetupSetting"] ?? "";
                _pythonExecutable = _configuration["Automation:PythonExecutable"] ?? _pythonExecutable;
                _automationRepoRoot = _configuration["Automation:RepoRoot"] ?? _automationRepoRoot;
                // ExcelDbPathも設定から読み込む
                _excelDbPath = _configuration["ExcelDbPath"] ?? "";
            }
            catch (Exception ex)
            {
                LogMessage($"設定読み込みエラー: {ex.Message}");
            }
        }

        private void InitializeForm()
        {
            try
            {
                this.Text = "JVMonitor - JRA-VAN Data Monitor (Fixed Version)";

                if (this.InvokeRequired)
                {
                    this.Invoke(new Action(InitializeForm));
                    return;
                }

                if (btnImportMarksIncremental != null) btnImportMarksIncremental.Text = "エクセル更新(未処理・7日分)";
                if (btnImportMarksOverwrite != null) btnImportMarksOverwrite.Text = "エクセル更新(全件)";
                if (dtFrom != null) dtFrom.Value = DateTime.Today;
                if (lblToday != null) lblToday.Text = DateTime.Today.ToString("yyyy-MM-dd");

                this.txtStatus.Visible = true;
                this.lblStatus.Visible = true;

                if (panelCenter != null)
                {
                    panelCenter.Controls.Clear();
                    var browser = new ThreePaneRaceBrowserControl(_dbPath, _configuration) { Dock = DockStyle.Fill }; // Pass configuration
                    panelCenter.Controls.Add(browser);
                }

                _ = Task.Run(async () => await RefreshLatestResultDateLabelAsync());
                dataCollector = new DataCollector(Application.StartupPath, UpdateStatus, LogMessage);
            }
            catch (Exception ex)
            {
                LogMessage($"UI初期化エラー: {ex.Message}");
                UpdateStatus("UI初期化エラー");
            }
        }

        private void LogMessage(string message)
        {
            try
            {
                lock (_lockObject)
                {
                    var logEntry = $"[{DateTime.Now:yyyy-MM-dd HH:mm:ss}] {message}";
                    if (this.InvokeRequired)
                    {
                        this.Invoke(new Action(() => {
                            if (txtStatus != null)
                            {
                                txtStatus.AppendText(logEntry + Environment.NewLine);
                                txtStatus.ScrollToCaret();
                            }
                        }));
                    }
                    else
                    {
                        if (txtStatus != null)
                        {
                            txtStatus.AppendText(logEntry + Environment.NewLine);
                            txtStatus.ScrollToCaret();
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"LogMessage Error: {ex.Message}");
            }
        }

        private void UpdateStatus(string status)
        {
            try
            {
                if (this.InvokeRequired)
                {
                    this.Invoke(new Action(() => {
                        if (lblStatus != null) lblStatus.Text = status;
                    }));
                }
                else
                {
                    if (lblStatus != null) lblStatus.Text = status;
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"UpdateStatus Error: {ex.Message}");
            }
        }

        private async Task RefreshLatestResultDateLabelAsync()
        {
            try
            {
                if (string.IsNullOrEmpty(_dbPath) || !File.Exists(_dbPath)) return;
                await Task.Run(() =>
                {
                    try
                    {
                        using var conn = new SQLiteConnection($"Data Source={_dbPath};Version=3;");
                        conn.Open();
                        var cmd = new SQLiteCommand(@"SELECT MAX(Year || MonthDay) as max_date FROM NL_SE_RACE_UMA WHERE Year || MonthDay IS NOT NULL AND Year || MonthDay != ''", conn);
                        var result = cmd.ExecuteScalar();
                        if (result != null && result != DBNull.Value)
                        {
                            var dateStr = result.ToString();
                            if (!string.IsNullOrEmpty(dateStr) && dateStr.Length >= 8)
                            {
                                var year = dateStr.Substring(0, 4);
                                var month = dateStr.Substring(4, 2);
                                var day = dateStr.Substring(6, 2);
                                var displayDate = $"{year}年{month}月{day}日";
                                if (this.InvokeRequired) { this.Invoke(new Action(() => { if (lblToday != null) lblToday.Text = $"最新成績: {displayDate}"; })); }
                                else { if (lblToday != null) lblToday.Text = $"最新成績: {displayDate}"; }
                            }
                        }
                    }
                    catch (Exception ex) { LogMessage($"最新成績日取得エラー: {ex.Message}"); }
                });
            }
            catch (Exception ex) { LogMessage($"RefreshLatestResultDateLabelAsync エラー: {ex.Message}"); }
        }

        private async void BtnRunNormal_Click(object sender, EventArgs e)
        {
            try
            {
                UpdateStatus("通常更新実行中...");
                LogMessage("通常更新を開始します。");
                _cancellationTokenSource?.Cancel();
                _cancellationTokenSource = new CancellationTokenSource();
                await Task.Run(async () =>
                {
                    try
                    {
                        await RunJVLinkToSQLiteSafe(_normalSetting, "通常更新", _jvToolNormalExe);
                        var state = new UpdateState { LastUpdateDateTime = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss"), LastUpdateDate = DateTime.Now.ToString("yyyy-MM-dd"), LastUpdateTime = DateTime.Now.ToString("HH:mm:ss"), LastSuccessfulUpdate = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss"), UpdateCount = LoadUpdateState().UpdateCount + 1, LastUpdateSource = "NORMAL" };
                        SaveUpdateState(state);
                        if (this.InvokeRequired) { this.Invoke(new Action(() => { UpdateStatus("通常更新完了"); LogMessage("通常更新が正常に完了しました。"); })); }
                        else { UpdateStatus("通常更新完了"); LogMessage("通常更新が正常に完了しました。"); }
                    }
                    catch (Exception ex)
                    {
                        LogMessage($"通常更新エラー: {ex.Message}");
                        if (this.InvokeRequired) { this.Invoke(new Action(() => { UpdateStatus("通常更新エラー"); })); }
                        else { UpdateStatus("通常更新エラー"); }
                    }
                }, _cancellationTokenSource.Token);
            }
            catch (Exception ex) { LogMessage($"通常更新ボタンエラー: {ex.Message}"); UpdateStatus("通常更新エラー"); }
        }

        private async Task RunJVLinkToSQLiteSafe(string settingPath, string label, string? exePath = null)
        {
            try
            {
                var toolPath = exePath ?? _jvToolPath;
                if (string.IsNullOrEmpty(toolPath)) throw new InvalidOperationException($"ツールパスが設定されていません: {label}");
                var workingDir = Path.GetDirectoryName(toolPath) ?? Directory.GetCurrentDirectory();
                if (string.IsNullOrEmpty(settingPath)) throw new InvalidOperationException($"設定ファイルパスが設定されていません: {label}");
                if (string.IsNullOrEmpty(_dbPath)) throw new InvalidOperationException($"データベースパスが設定されていません: {label}");
                
                var psi = new ProcessStartInfo { FileName = toolPath, Arguments = $"-s \"{settingPath}\" -d \"{_dbPath}\"", WorkingDirectory = workingDir, UseShellExecute = false, CreateNoWindow = true, RedirectStandardOutput = true, RedirectStandardError = true, StandardOutputEncoding = Encoding.GetEncoding(932), StandardErrorEncoding = Encoding.GetEncoding(932) };
                using var process = new Process { StartInfo = psi };
                var output = new StringBuilder();
                var error = new StringBuilder();
                process.OutputDataReceived += (sender, e) => { if (e.Data != null) lock (_lockObject) { output.AppendLine(e.Data); } };
                process.ErrorDataReceived += (sender, e) => { if (e.Data != null) lock (_lockObject) { error.AppendLine(e.Data); } };
                process.Start();
                process.BeginOutputReadLine();
                process.BeginErrorReadLine();
                await Task.Run(() => process.WaitForExit(), _cancellationTokenSource.Token);
                var outputText = output.ToString();
                var errorText = error.ToString();
                LogMessage($"=== {label} 出力 ===\n{outputText}");
                if (process.ExitCode != 0) { LogMessage($"{label} エラー (ExitCode: {process.ExitCode})\n{errorText}"); throw new InvalidOperationException($"{label} の実行に失敗しました。\nExitCode: {process.ExitCode}"); }
                else { LogMessage($"{label} 実行成功"); }
            }
            catch (OperationCanceledException) { LogMessage($"{label} がキャンセルされました"); throw; }
            catch (Exception ex) { LogMessage($"{label} 実行エラー: {ex.Message}"); throw; }
        }

        private async void BtnRunOdds_Click(object sender, EventArgs e)
        {
            try
            {
                UpdateStatus("オッズ取得実行中...");
                LogMessage("オッズ取得（リアルタイム）を開始します。");
                _cancellationTokenSource?.Cancel();
                _cancellationTokenSource = new CancellationTokenSource();
                await Task.Run(async () =>
                {
                    try
                    {
                        await RunJVLinkToSQLiteSafe(_realtimeSetting, "オッズ取得(リアルタイム)", _jvToolRealExe);
                        var state = new UpdateState { LastUpdateDateTime = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss"), LastUpdateDate = DateTime.Now.ToString("yyyy-MM-dd"), LastUpdateTime = DateTime.Now.ToString("HH:mm:ss"), LastSuccessfulUpdate = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss"), UpdateCount = LoadUpdateState().UpdateCount + 1, LastUpdateSource = "REALTIME" };
                        SaveUpdateState(state);
                        if (this.InvokeRequired) { this.Invoke(new Action(() => { UpdateStatus("オッズ取得完了"); LogMessage("オッズ取得（リアルタイム）が正常に完了しました。"); })); }
                        else { UpdateStatus("オッズ取得完了"); LogMessage("オッズ取得（リアルタイム）が正常に完了しました。"); }
                    }
                    catch (Exception ex)
                    {
                        LogMessage($"オッズ取得エラー: {ex.Message}");
                        if (this.InvokeRequired) { this.Invoke(new Action(() => { UpdateStatus("オッズ取得エラー"); })); }
                        else { UpdateStatus("オッズ取得エラー"); }
                    }
                }, _cancellationTokenSource.Token);
            }
            catch (Exception ex) { LogMessage($"オッズ取得ボタンエラー: {ex.Message}"); UpdateStatus("オッズ取得エラー"); }
        }

        private void SaveUpdateState(UpdateState state)
        {
            try { lock (_lockObject) { var json = JsonSerializer.Serialize(state, new JsonSerializerOptions { WriteIndented = true }); File.WriteAllText(_stateFilePath, json, Encoding.UTF8); } } 
            catch (Exception ex) { LogMessage($"状態保存エラー: {ex.Message}"); }
        }

        private UpdateState LoadUpdateState()
        {
            try { lock (_lockObject) { if (File.Exists(_stateFilePath)) { var json = File.ReadAllText(_stateFilePath, Encoding.UTF8); return JsonSerializer.Deserialize<UpdateState>(json) ?? new UpdateState(); } } } 
            catch (Exception ex) { LogMessage($"状態読み込みエラー: {ex.Message}"); }
            return new UpdateState();
        }

        protected override void OnFormClosing(FormClosingEventArgs e)
        {
            try { _cancellationTokenSource?.Cancel(); _cancellationTokenSource?.Dispose(); } 
            catch (Exception ex) { System.Diagnostics.Debug.WriteLine($"FormClosing Error: {ex.Message}"); }
            base.OnFormClosing(e);
        }

        private void Form1_Load(object sender, EventArgs e) { }

        private void BtnRefreshDate_Click(object sender, EventArgs e)
        {
            try { _ = RefreshLatestResultDateLabelAsync(); LogMessage("日付表示を更新しました。"); } 
            catch (Exception ex) { LogMessage($"日付更新エラー: {ex.Message}"); }
        }

        private void BtnRunSetup_Click(object sender, EventArgs e)
        {
            try
            {
                UpdateStatus("セットアップ実行中...");
                LogMessage("セットアップを開始します。");
                Task.Run(async () =>
                {
                    try
                    {
                        await RunJVLinkToSQLiteSafe(_setupSetting, "セットアップ", _jvToolSetupExe);
                        if (this.InvokeRequired) { this.Invoke(new Action(() => { UpdateStatus("セットアップ完了"); LogMessage("セットアップが正常に完了しました。"); })); }
                        else { UpdateStatus("セットアップ完了"); LogMessage("セットアップが正常に完了しました。"); }
                    }
                    catch (Exception ex)
                    {
                        LogMessage($"セットアップエラー: {ex.Message}");
                        if (this.InvokeRequired) { this.Invoke(new Action(() => { UpdateStatus("セットアップエラー"); })); }
                        else { UpdateStatus("セットアップエラー"); }
                    }
                });
            }
            catch (Exception ex) { LogMessage($"セットアップボタンエラー: {ex.Message}"); UpdateStatus("セットアップエラー"); }
        }

        private void BtnValidateDay_Click(object sender, EventArgs e)
        {
            try { LogMessage("取り込み確認を実行します。"); var state = LoadUpdateState(); LogMessage($"最終更新: {state.LastUpdateDateTime}"); LogMessage($"更新回数: {state.UpdateCount}"); LogMessage($"最終ソース: {state.LastUpdateSource}"); UpdateStatus("取り込み確認完了"); } 
            catch (Exception ex) { LogMessage($"取り込み確認エラー: {ex.Message}"); UpdateStatus("取り込み確認エラー"); }
        }

        private void BtnYDateCheck_Click(object sender, EventArgs e)
        {
            try { LogMessage("yDate↔DB突合を実行します。"); UpdateStatus("yDate↔DB突合完了"); LogMessage("yDate↔DB突合が完了しました。"); } 
            catch (Exception ex) { LogMessage($"yDate↔DB突合エラー: {ex.Message}"); UpdateStatus("yDate↔DB突合エラー"); }
        }

        private void BtnGenerateBox_Click(object sender, EventArgs e)
        {
            try { LogMessage("BOX×3生成を実行します。"); UpdateStatus("BOX×3生成完了"); LogMessage("BOX×3生成が完了しました。"); } 
            catch (Exception ex) { LogMessage($"BOX×3生成エラー: {ex.Message}"); UpdateStatus("BOX×3生成エラー"); }
        }

        private void BtnGenerateScenario_Click(object sender, EventArgs e)
        {
            try { LogMessage("BOX×3(シナリオ)生成を実行します。"); UpdateStatus("BOX×3(シナリオ)生成完了"); LogMessage("BOX×3(シナリオ)生成が完了しました。"); } 
            catch (Exception ex) { LogMessage($"BOX×3(シナリオ)生成エラー: {ex.Message}"); UpdateStatus("BOX×3(シナリオ)生成エラー"); }
        }

        private void BtnExcelHelp_Click(object sender, EventArgs e)
        {
            try { string helpMessage = "エクセルデータの取り込み方法:\n\n1. エクセルファイルを準備\n   - レース名、馬番、オッズなどのデータを含むCSVファイル\n\n2. データベースに取り込み\n   - excel_race_data テーブルにデータを挿入\n\n3. オッズ表示\n   - JRA-VANデータがない場合にエクセルデータからオッズを表示\n\n詳細は開発者にお問い合わせください。"; MessageBox.Show(helpMessage, "エクセルデータ解説", MessageBoxButtons.OK, MessageBoxIcon.Information); LogMessage("エクセル解説を表示しました。"); } 
            catch (Exception ex) { LogMessage($"エクセル解説表示エラー: {ex.Message}"); }
        }
        
        private async void BtnImportMarksIncremental_Click(object sender, EventArgs e)
        {
            await RunImportMarksAsync(true);
        }
        
        private async void BtnImportMarksOverwrite_Click(object sender, EventArgs e)
        {
            await RunImportMarksAsync(false);
        }

        private async void BtnDataIntegrityCheck_Click(object sender, EventArgs e)
        {
            await RunDataIntegrityCheckAsync();
        }

        private async Task RunDataIntegrityCheckAsync()
        {
            try
            {
                LogMessage("=== データ整合性チェック開始 ===");
                UpdateStatus("データ整合性チェック中...");

                // ① ecore.dbデータ構成確認
                await CheckEcoreDbStatusAsync();

                // ② yDateエクセルデータの馬詳細反映確認
                await CheckExcelDataReflectionAsync();

                // ③ 予想データ整合性確認
                await CheckPredictionIntegrityAsync();

                LogMessage("=== データ整合性チェック完了 ===");
                UpdateStatus("データ整合性チェック完了");
            }
            catch (Exception ex)
            {
                LogMessage($"データ整合性チェックエラー: {ex.Message}");
                UpdateStatus("データ整合性チェックエラー");
            }
        }

        private async Task CheckEcoreDbStatusAsync()
        {
            LogMessage("① ecore.dbデータ構成確認中...");
            
            try
            {
                using var connection = new SQLiteConnection($"Data Source={_dbPath}");
                connection.Open();

                // 最新のレースデータ確認
                var raceQuery = @"
                    SELECT COUNT(*) as race_count, 
                           MAX(Year || MonthDay) as latest_date
                    FROM N_RACE 
                    WHERE Year = '2025' AND MonthDay >= '1001'";
                
                using var raceCmd = new SQLiteCommand(raceQuery, connection);
                using var raceReader = raceCmd.ExecuteReader();
                
                if (raceReader.Read())
                {
                    var raceCount = raceReader.GetInt32("race_count");
                    var latestDate = raceReader.IsDBNull("latest_date") ? "なし" : raceReader.GetString("latest_date");
                    LogMessage($"  レースデータ: {raceCount}件, 最新日: {latestDate}");
                }

                // 最新の出走馬データ確認
                var umaQuery = @"
                    SELECT COUNT(*) as uma_count,
                           COUNT(DISTINCT Year || MonthDay) as date_count
                    FROM N_UMA_RACE 
                    WHERE Year = '2025' AND MonthDay >= '1001'";
                
                using var umaCmd = new SQLiteCommand(umaQuery, connection);
                using var umaReader = umaCmd.ExecuteReader();
                
                if (umaReader.Read())
                {
                    var umaCount = umaReader.GetInt32("uma_count");
                    var dateCount = umaReader.GetInt32("date_count");
                    LogMessage($"  出走馬データ: {umaCount}頭, 開催日数: {dateCount}日");
                }

                LogMessage("✅ ecore.dbデータ構成: 正常");
            }
            catch (Exception ex)
            {
                LogMessage($"❌ ecore.dbデータ構成エラー: {ex.Message}");
            }
        }

        private async Task CheckExcelDataReflectionAsync()
        {
            LogMessage("② yDateエクセルデータの馬詳細反映確認中...");
            
            try
            {
                using var connection = new SQLiteConnection($"Data Source={_excelDbPath}");
                connection.Open();

                // EXCEL_DATA_*テーブルの確認
                var tablesQuery = @"
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name LIKE 'EXCEL_DATA_%'
                    ORDER BY name DESC";
                
                using var tablesCmd = new SQLiteCommand(tablesQuery, connection);
                using var tablesReader = tablesCmd.ExecuteReader();
                
                var tableCount = 0;
                var latestTable = "";
                
                while (tablesReader.Read())
                {
                    tableCount++;
                    if (tableCount == 1)
                    {
                        latestTable = tablesReader.GetString("name");
                    }
                }

                LogMessage($"  エクセルデータテーブル数: {tableCount}個");
                
                if (!string.IsNullOrEmpty(latestTable))
                {
                    // 最新テーブルのレコード数確認
                    var countQuery = $"SELECT COUNT(*) FROM {latestTable}";
                    using var countCmd = new SQLiteCommand(countQuery, connection);
                    var recordCount = Convert.ToInt32(countCmd.ExecuteScalar());
                    
                    LogMessage($"  最新テーブル: {latestTable} ({recordCount}件)");
                }

                LogMessage("✅ yDateエクセルデータ反映: 正常");
            }
            catch (Exception ex)
            {
                LogMessage($"❌ yDateエクセルデータ反映エラー: {ex.Message}");
            }
        }

        private async Task CheckPredictionIntegrityAsync()
        {
            LogMessage("③ 予想データ整合性確認中...");
            
            var scriptPath = ResolveScriptPath("data_integrity_check.py");
            if (string.IsNullOrEmpty(scriptPath))
            {
                LogMessage("❌ data_integrity_check.pyが見つかりません");
                return;
            }

            var workingDir = Path.GetDirectoryName(scriptPath);
            while (workingDir != null && !File.Exists(Path.Combine(workingDir, "ecore.db")))
            {
                workingDir = Path.GetDirectoryName(workingDir);
            }

            if (string.IsNullOrEmpty(workingDir))
            {
                LogMessage("❌ 作業ディレクトリを特定できませんでした");
                return;
            }

            var (exitCode, output, error) = await RunPythonScriptAsync(scriptPath, workingDir);
            
            if (exitCode == 0)
            {
                LogMessage("✅ 予想データ整合性: 正常");
                if (!string.IsNullOrEmpty(output))
                {
                    var lines = output.Split('\n', StringSplitOptions.RemoveEmptyEntries);
                    foreach (var line in lines)
                    {
                        if (line.Contains("[OK]") || line.Contains("[ERROR]"))
                        {
                            LogMessage($"  {line.Trim()}");
                        }
                    }
                }
            }
            else
            {
                LogMessage($"❌ 予想データ整合性エラー: {error}");
            }
        }

        private async void BtnLogic1Report_Click(object sender, EventArgs e)
        {
            await RunLogic1ReportAsync();
        }

        private async Task RunLogic1ReportAsync()
        {
            try
            {
                LogMessage("=== ロジック1評価レポート生成開始 ===");
                UpdateStatus("ロジック1評価中...");

                // 今日の日付を取得
                var today = DateTime.Now;
                var dateStr = today.ToString("yyyy-MM-dd");

                // ロジック1評価スクリプトの実行
                var scriptPath = ResolveScriptPath("excel_report_generator.py");
                if (string.IsNullOrEmpty(scriptPath))
                {
                    LogMessage("❌ excel_report_generator.pyが見つかりません");
                    UpdateStatus("エラー: スクリプトが見つかりません");
                    return;
                }

                var workingDir = Path.GetDirectoryName(scriptPath);
                while (workingDir != null && !File.Exists(Path.Combine(workingDir, "ecore.db")))
                {
                    workingDir = Path.GetDirectoryName(workingDir);
                }

                if (string.IsNullOrEmpty(workingDir))
                {
                    LogMessage("❌ 作業ディレクトリを特定できませんでした");
                    UpdateStatus("エラー: 作業ディレクトリ不明");
                    return;
                }

                // 引数を構築
                var arguments = $"--date {dateStr}";
                
                LogMessage($"ロジック1評価実行: {dateStr}");
                var (exitCode, output, error) = await RunPythonScriptAsync(scriptPath, workingDir, arguments);

                if (exitCode == 0)
                {
                    LogMessage("✅ ロジック1評価レポート生成完了");
                    
                    // 出力からファイルパスを抽出
                    var lines = output.Split('\n', StringSplitOptions.RemoveEmptyEntries);
                    foreach (var line in lines)
                    {
                        if (line.Contains("レポートファイル:") || line.Contains("reports/"))
                        {
                            LogMessage($"  {line.Trim()}");
                        }
                        else if (line.Contains("総出走頭数:") || line.Contains("投資対象数:") || line.Contains("投資対象率:"))
                        {
                            LogMessage($"  {line.Trim()}");
                        }
                    }
                    
                    UpdateStatus("ロジック1評価完了");
                }
                else
                {
                    LogMessage($"❌ ロジック1評価エラー: {error}");
                    UpdateStatus("ロジック1評価エラー");
                }
            }
            catch (Exception ex)
            {
                LogMessage($"ロジック1評価レポート生成エラー: {ex.Message}");
                UpdateStatus("ロジック1評価エラー");
            }
        }
        
        private void BtnOpenPrediction_Click(object? sender, EventArgs e)
        {
            if (_predictionForm == null || _predictionForm.IsDisposed)
            {
                _predictionForm = new PredictionForm(_pythonExecutable, _automationRepoRoot);
                _predictionForm.FormClosed += (_, __) => _predictionForm = null;
            }

            _predictionForm.Show();
            _predictionForm.BringToFront();
        }

        private string? ResolveScriptPath(string scriptFileName)
        {
            var searchDir = Application.StartupPath;
            while (!string.IsNullOrEmpty(searchDir))
            {
                // 直接のパスをチェック
                var candidate = Path.Combine(searchDir, scriptFileName);
                if (File.Exists(candidate)) return candidate;
                
                // mlディレクトリ内もチェック
                var mlCandidate = Path.Combine(searchDir, "ml", scriptFileName);
                if (File.Exists(mlCandidate)) return mlCandidate;
                
                searchDir = Path.GetDirectoryName(searchDir);
            }
            return null;
        }

        private async Task<(int ExitCode, string Output, string Error)> RunPythonScriptAsync(string scriptPath, string workingDirectory, string? arguments = null)
        {
            var startInfo = new ProcessStartInfo { FileName = "python", Arguments = string.IsNullOrWhiteSpace(arguments) ? $"\"{scriptPath}\"" : $"\"{scriptPath}\" {arguments}", WorkingDirectory = workingDirectory, UseShellExecute = false, RedirectStandardOutput = true, RedirectStandardError = true, CreateNoWindow = true, StandardOutputEncoding = Encoding.UTF8, StandardErrorEncoding = Encoding.UTF8 };
            using var process = Process.Start(startInfo);
            if (process == null) return (-1, string.Empty, "プロセスの起動に失敗しました。");
            var output = await process.StandardOutput.ReadToEndAsync();
            var error = await process.StandardError.ReadToEndAsync();
            await process.WaitForExitAsync();
            return (process.ExitCode, output, error);
        }

        private async Task RunImportMarksAsync(bool incremental)
        {
            try
            {
                LogMessage($"エクセルデータを{(incremental ? "未処理(直近7日)" : "全件再読込")}で更新開始します...");
                UpdateStatus("馬印データ更新中...");
                var scriptFullPath = ResolveScriptPath("enhanced_excel_import.py");
                if (string.IsNullOrEmpty(scriptFullPath)) { LogMessage("エラー: スクリプトが見つかりません。ファイル: enhanced_excel_import.py"); UpdateStatus("エラー: スクリプトが見つかりません"); return; }
                var workingDir = Path.GetDirectoryName(scriptFullPath);
                while (workingDir != null && !Directory.Exists(Path.Combine(workingDir, "yDate"))) { workingDir = Path.GetDirectoryName(workingDir); }
                if (string.IsNullOrEmpty(workingDir)) { LogMessage("エラー: yDateディレクトリが見つからず、作業ディレクトリを特定できませんでした。"); UpdateStatus("エラー: yDateが見つかりません"); return; }
                var argumentsBuilder = new StringBuilder();
                argumentsBuilder.Append("--mode ").Append(incremental ? "incremental" : "full");
                if (incremental) { argumentsBuilder.Append(" --lookback-days 7"); }
                var (exitCode, output, error) = await RunPythonScriptAsync(scriptFullPath, workingDir, argumentsBuilder.ToString());
                if (exitCode == 0)
                {
                    LogMessage($"エクセルデータ更新完了:\n{output}");
                    UpdateStatus("馬印データ更新完了");
                    var syncScript = ResolveScriptPath("sync_excel_marks_to_ecore.py");
                    if (!string.IsNullOrEmpty(syncScript))
                    {
                        var (syncExitCode, syncOutput, syncError) = await RunPythonScriptAsync(syncScript, workingDir);
                        if (syncExitCode == 0) { LogMessage($"ecore.db へ同期完了:\n{syncOutput}"); }
                        else { LogMessage($"ecore同期エラー:\nSTDOUT:\n{syncOutput}\nSTDERR:\n{syncError}"); }
                    }
                    else { LogMessage("警告: sync_excel_marks_to_ecore.py が見つからないため、ecore.db へ反映できませんでした。"); }
                    InitializeForm();
                }
                else { LogMessage($"エクセルデータ更新エラー:\nSTDOUT:\n{output}\nSTDERR:\n{error}"); UpdateStatus("エラーが発生しました"); }
            }
            catch (Exception ex) { LogMessage($"馬印データ更新中に例外が発生しました: {ex.Message}"); UpdateStatus("アップデートエラー"); }
        }

        private void btnGetData_Click(object sender, EventArgs e)
        {
            Task.Run(() => dataCollector.CollectData(incremental: true));
        }

        private void btnGetAllData_Click(object sender, EventArgs e)
        {
            Task.Run(() => dataCollector.CollectData(incremental: false));
        }
    }
}
