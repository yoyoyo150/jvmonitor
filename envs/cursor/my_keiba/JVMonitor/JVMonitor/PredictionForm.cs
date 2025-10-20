using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace JVMonitor
{
    public partial class PredictionForm : Form
    {
        private readonly string _pythonExe;
        private readonly string _repoRoot;
        private readonly GroupBox _summaryGroupBox;
        private readonly ListView _summaryListView;
        private string? _latestEvaluationReport;

        private static readonly (string Key, string Label)[] EvaluationMetricOrder =
        {
            ("total_predictions", "予測総数"),
            ("invest_selections", "投資候補数"),
            ("joined_results", "結果突合数"),
            ("win_hits", "単勝的中数"),
            ("win_hit_rate", "単勝的中率"),
            ("win_roi", "単勝ROI"),
            ("place_hits", "複勝的中数"),
            ("place_hit_rate", "複勝的中率")
        };

        public PredictionForm(string? pythonExecutable = null, string? repositoryRoot = null)
        {
            InitializeComponent();

            _pythonExe = ResolvePythonExecutable(pythonExecutable);
            _repoRoot = ResolveRepositoryRoot(repositoryRoot);

            _summaryListView = CreateSummaryListView();
            _summaryGroupBox = new GroupBox
            {
                Dock = DockStyle.Fill,
                Text = "評価サマリー"
            };
            _summaryGroupBox.Controls.Add(_summaryListView);
            ConfigureLayoutWithSummary();
            ResetEvaluationSummary();

            dtPredictionDate.Value = DateTime.Today;
            dtRangeFrom.Value = DateTime.Today;
            dtRangeTo.Value = DateTime.Today;
            if (cmbScenario.Items.Count > 0)
            {
                cmbScenario.SelectedIndex = 0;
            }

            AppendLog($"Python実行ファイル: {_pythonExe}");
            AppendLog($"作業ディレクトリ: {_repoRoot}");
            AppendLog("※ ランク判定の閾値は ml/config/rank_rules.json で調整してください。");
        }

        private static string ResolvePythonExecutable(string? candidate)
        {
            if (!string.IsNullOrWhiteSpace(candidate))
            {
                return candidate;
            }

            var envPython = Environment.GetEnvironmentVariable("PYTHON");
            if (!string.IsNullOrWhiteSpace(envPython))
            {
                return envPython;
            }

            return "python";
        }

        private static string ResolveRepositoryRoot(string? candidate)
        {
            if (!string.IsNullOrWhiteSpace(candidate))
            {
                var path = Path.GetFullPath(candidate);
                if (Directory.Exists(path))
                {
                    return path;
                }
            }

            var current = Application.StartupPath;
            while (!string.IsNullOrEmpty(current))
            {
                var mlDir = Path.Combine(current, "ml");
                if (Directory.Exists(mlDir))
                {
                    return current;
                }
                var parent = Path.GetDirectoryName(current);
                if (string.IsNullOrEmpty(parent) || string.Equals(parent, current, StringComparison.OrdinalIgnoreCase))
                {
                    break;
                }
                current = parent;
            }

            return Application.StartupPath;
        }

        private ListView CreateSummaryListView()
        {
            var listView = new ListView
            {
                Dock = DockStyle.Fill,
                View = View.Details,
                FullRowSelect = true,
                GridLines = true,
                HideSelection = false,
                HeaderStyle = ColumnHeaderStyle.Nonclickable,
                UseCompatibleStateImageBehavior = false
            };

            listView.Columns.Add("指標", 220);
            listView.Columns.Add("値", 140);
            return listView;
        }

        private void ConfigureLayoutWithSummary()
        {
            tableLayoutPanel.SuspendLayout();
            try
            {
                tableLayoutPanel.Controls.Remove(txtLog);
                tableLayoutPanel.RowStyles.Clear();
                tableLayoutPanel.RowCount = 3;
                tableLayoutPanel.RowStyles.Add(new RowStyle(SizeType.Absolute, 220F));
                tableLayoutPanel.RowStyles.Add(new RowStyle(SizeType.Absolute, 160F));
                tableLayoutPanel.RowStyles.Add(new RowStyle(SizeType.Percent, 100F));
                tableLayoutPanel.Controls.Add(_summaryGroupBox, 0, 1);
                tableLayoutPanel.Controls.Add(txtLog, 0, 2);
            }
            finally
            {
                tableLayoutPanel.ResumeLayout();
            }
        }

        private void ResetEvaluationSummary()
        {
            _summaryListView.BeginUpdate();
            try
            {
                _summaryListView.Items.Clear();
                foreach (var (_, label) in EvaluationMetricOrder)
                {
                    var item = new ListViewItem(label);
                    item.SubItems.Add("-");
                    _summaryListView.Items.Add(item);
                }
            }
            finally
            {
                _summaryListView.EndUpdate();
            }
        }

        private void AppendLog(string message)
        {
            var builder = new StringBuilder();
            builder.AppendLine($"[{DateTime.Now:HH:mm:ss}] {message}");
            txtLog.AppendText(builder.ToString());
        }

        private void SetUiEnabled(bool enabled)
        {
            btnRunPre.Enabled = enabled;
            btnRunLive.Enabled = enabled;
            btnEvaluate.Enabled = enabled;
            dtPredictionDate.Enabled = enabled;
            cmbScenario.Enabled = enabled;
            dtRangeFrom.Enabled = enabled;
            dtRangeTo.Enabled = enabled;
            btnRangePredict.Enabled = enabled;
            btnRangeEvaluate.Enabled = enabled;
        }

        private async Task<(int ExitCode, string StdOut, string StdErr)> ExecutePythonModuleAsync(string module, IEnumerable<string> arguments)
        {
            var argumentList = arguments?.ToList() ?? new List<string>();
            if (string.IsNullOrWhiteSpace(module))
            {
                throw new ArgumentException("Module name must be provided.", nameof(module));
            }

            if (!Directory.Exists(_repoRoot))
            {
                throw new DirectoryNotFoundException($"Working directory not found: {_repoRoot}");
            }

            var startInfo = new ProcessStartInfo
            {
                FileName = _pythonExe,
                WorkingDirectory = _repoRoot,
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true,
                StandardOutputEncoding = Encoding.UTF8,
                StandardErrorEncoding = Encoding.UTF8
            };

            startInfo.ArgumentList.Add("-m");
            startInfo.ArgumentList.Add(module);
            foreach (var argument in argumentList)
            {
                startInfo.ArgumentList.Add(argument);
            }

            startInfo.Environment.TryAdd("PYTHONIOENCODING", "utf-8");
            startInfo.Environment.TryAdd("PYTHONUNBUFFERED", "1");

            using var process = new Process { StartInfo = startInfo };
            process.Start();

            var stdoutTask = process.StandardOutput.ReadToEndAsync();
            var stderrTask = process.StandardError.ReadToEndAsync();

            await Task.WhenAll(stdoutTask, stderrTask, process.WaitForExitAsync());

            return (process.ExitCode, stdoutTask.Result, stderrTask.Result);
        }




        private static string QuoteArgument(string argument)
        {
            if (argument == null)
            {
                return "\"\"";
            }

            if (argument.Length == 0)
            {
                return "\"\"";
            }

            if (argument.IndexOfAny(new[] { ' ', '\t', '"' }) == -1)
            {
                return argument;
            }

            var escaped = argument.Replace("\\", "\\\\").Replace("\"", "\\\"");
            return $"\"{escaped}\"";
        }

        private string FormatCommandForLog(string module, IEnumerable<string> arguments)
        {
            var tokens = new List<string> { "python", "-m", module };
            tokens.AddRange(arguments.Select(QuoteArgument));
            return string.Join(" ", tokens);
        }

        private static string CreateTempFilePath(string prefix, string extension)
        {
            var safeExtension = extension.StartsWith(".") ? extension : $".{extension}";
            return Path.Combine(Path.GetTempPath(), $"{prefix}_{Guid.NewGuid():N}{safeExtension}");
        }

        private void UpdateEvaluationSummary(JsonElement metricsElement)
        {
            if (metricsElement.ValueKind != JsonValueKind.Object)
            {
                return;
            }

            var metricLookup = metricsElement.EnumerateObject().ToDictionary(p => p.Name, p => p.Value);
            _summaryListView.BeginUpdate();
            try
            {
                _summaryListView.Items.Clear();
                foreach (var (key, label) in EvaluationMetricOrder)
                {
                    metricLookup.TryGetValue(key, out var valueElement);
                    var item = new ListViewItem(label);
                    item.SubItems.Add(FormatMetricValue(key, valueElement));
                    _summaryListView.Items.Add(item);
                }
            }
            finally
            {
                _summaryListView.EndUpdate();
            }
        }

        private static string FormatMetricValue(string key, JsonElement element)
        {
            if (element.ValueKind == JsonValueKind.Null || element.ValueKind == JsonValueKind.Undefined)
            {
                return "-";
            }

            if (element.ValueKind == JsonValueKind.Number)
            {
                if (element.TryGetDecimal(out var decimalValue))
                {
                    if (key.EndsWith("_rate", StringComparison.OrdinalIgnoreCase) || key.EndsWith("_roi", StringComparison.OrdinalIgnoreCase))
                    {
                        return decimalValue.ToString("P1", CultureInfo.InvariantCulture);
                    }

                    if (decimalValue == Math.Floor(decimalValue))
                    {
                        return decimalValue.ToString("0", CultureInfo.InvariantCulture);
                    }

                    return decimalValue.ToString("0.###", CultureInfo.InvariantCulture);
                }

                return element.ToString();
            }

            if (element.ValueKind == JsonValueKind.String)
            {
                var str = element.GetString();
                return string.IsNullOrWhiteSpace(str) ? "-" : str;
            }

            if (element.ValueKind == JsonValueKind.True || element.ValueKind == JsonValueKind.False)
            {
                return element.GetBoolean() ? "true" : "false";
            }

            return element.ToString();
        }

        private void EnsureScenarioOption(string scenario)
        {
            if (string.IsNullOrWhiteSpace(scenario))
            {
                return;
            }

            var index = cmbScenario.FindStringExact(scenario);
            if (index >= 0)
            {
                cmbScenario.SelectedIndex = index;
                return;
            }

            cmbScenario.Items.Add(scenario);
            cmbScenario.SelectedItem = scenario;
        }

        private void AppendProcessOutput(string content, bool isError)
        {
            if (string.IsNullOrWhiteSpace(content))
            {
                return;
            }

            var lines = content.Replace("\r\n", "\n").Replace('\r', '\n').Split('\n');
            var tag = isError ? "[stderr]" : "[stdout]";
            foreach (var line in lines)
            {
                if (string.IsNullOrWhiteSpace(line))
                {
                    continue;
                }
                AppendLog($"{tag} {line.TrimEnd()}");
            }
        }

        private List<string> BuildPredictionArguments(DateTime targetDate, string scenario)
        {
            return new List<string>
            {
                "--date", targetDate.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture),
                "--scenario", scenario
            };
        }

        private static List<string> BuildEvaluationArguments(DateTime startDate, DateTime endDate, string scenario, string outputPath)
        {
            return new List<string>
            {
                "--date-from", startDate.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture),
                "--date-to", endDate.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture),
                "--scenario", scenario,
                "--output-json", outputPath
            };
        }

        private void RefreshEvaluationSummaryFromFile(string jsonPath)
        {
            if (string.IsNullOrWhiteSpace(jsonPath))
            {
                return;
            }

            if (!File.Exists(jsonPath))
            {
                AppendLog($"[警告] 評価レポートが見つかりません: {jsonPath}");
                return;
            }

            try
            {
                using var stream = File.OpenRead(jsonPath);
                using var document = JsonDocument.Parse(stream);
                UpdateEvaluationSummary(document.RootElement);
                _latestEvaluationReport = jsonPath;
                AppendLog($"評価サマリーを読み込みました: {jsonPath}");
            }
            catch (Exception ex)
            {
                AppendLog($"評価JSONの解析に失敗しました: {ex.Message}");
            }
        }

        private async Task RunPredictionAsync(string scenario)
        {
            SetUiEnabled(false);
            try
            {
                var normalizedScenario = (scenario ?? "PRE").Trim().ToUpperInvariant();
                EnsureScenarioOption(normalizedScenario);

                var targetDate = dtPredictionDate.Value.Date;
                var arguments = BuildPredictionArguments(targetDate, normalizedScenario);

                AppendLog($"単日予測: {targetDate:yyyy-MM-dd} -> {FormatCommandForLog("ml.predict_today", arguments)}");

                var result = await ExecutePythonModuleAsync("ml.predict_today", arguments);
                AppendProcessOutput(result.StdOut, false);
                AppendProcessOutput(result.StdErr, true);
                AppendLog($"終了コード: {result.ExitCode}");
            }
            catch (Exception ex)
            {
                AppendLog($"予測実行失敗: {ex.Message}");
            }
            finally
            {
                SetUiEnabled(true);
            }
        }

        private async Task RunEvaluationAsync()
        {
            SetUiEnabled(false);
            try
            {
                var scenario = (cmbScenario.SelectedItem?.ToString() ?? "PRE").Trim().ToUpperInvariant();
                EnsureScenarioOption(scenario);

                var date = dtPredictionDate.Value.Date;
                var jsonPath = CreateTempFilePath("prediction_eval", "json");

                var arguments = BuildEvaluationArguments(date, date, scenario, jsonPath);

                AppendLog($"単日評価: {FormatCommandForLog("ml.evaluation.evaluate_predictions", arguments)}");

                var result = await ExecutePythonModuleAsync("ml.evaluation.evaluate_predictions", arguments);
                AppendProcessOutput(result.StdOut, false);
                AppendProcessOutput(result.StdErr, true);
                AppendLog($"終了コード: {result.ExitCode}");

                if (result.ExitCode == 0)
                {
                    RefreshEvaluationSummaryFromFile(jsonPath);
                }
            }
            catch (Exception ex)
            {
                AppendLog($"評価実行失敗: {ex.Message}");
            }
            finally
            {
                SetUiEnabled(true);
            }
        }

        private async Task RunPredictionRangeAsync()
        {
            var startDate = dtRangeFrom.Value.Date;
            var endDate = dtRangeTo.Value.Date;
            if (startDate > endDate)
            {
                AppendLog("[警告] 期間指定が不正です（開始日が終了日より後です）。");
                return;
            }

            SetUiEnabled(false);
            try
            {
                var scenario = (cmbScenario.SelectedItem?.ToString() ?? "PRE").Trim().ToUpperInvariant();
                EnsureScenarioOption(scenario);

                var totalDays = (endDate - startDate).Days + 1;
                AppendLog($"期間予測開始: {startDate:yyyy-MM-dd} ～ {endDate:yyyy-MM-dd}（{totalDays}日）");

                var failures = 0;
                for (var current = startDate; current <= endDate; current = current.AddDays(1))
                {
                    var arguments = BuildPredictionArguments(current, scenario);
                    AppendLog($"  ▶ {current:yyyy-MM-dd}: {FormatCommandForLog("ml.predict_today", arguments)}");

                    var result = await ExecutePythonModuleAsync("ml.predict_today", arguments);
                    AppendProcessOutput(result.StdOut, false);
                    AppendProcessOutput(result.StdErr, true);
                    AppendLog($"  終了コード: {result.ExitCode}");

                    if (result.ExitCode != 0)
                    {
                        failures++;
                    }
                }

                AppendLog($"期間予測完了: 成功 {totalDays - failures} / {totalDays} 日");
                dtPredictionDate.Value = endDate;
            }
            catch (Exception ex)
            {
                AppendLog($"期間予測失敗: {ex.Message}");
            }
            finally
            {
                SetUiEnabled(true);
            }
        }

        private async Task RunEvaluationRangeAsync()
        {
            var startDate = dtRangeFrom.Value.Date;
            var endDate = dtRangeTo.Value.Date;
            if (startDate > endDate)
            {
                AppendLog("[警告] 期間指定が不正です（開始日が終了日より後です）。");
                return;
            }

            SetUiEnabled(false);
            try
            {
                var scenario = (cmbScenario.SelectedItem?.ToString() ?? "PRE").Trim().ToUpperInvariant();
                EnsureScenarioOption(scenario);

                var jsonPath = CreateTempFilePath($"prediction_eval_{startDate:yyyyMMdd}_{endDate:yyyyMMdd}", "json");
                var arguments = BuildEvaluationArguments(startDate, endDate, scenario, jsonPath);

                AppendLog($"期間評価: {FormatCommandForLog("ml.evaluation.evaluate_predictions", arguments)}");

                var result = await ExecutePythonModuleAsync("ml.evaluation.evaluate_predictions", arguments);
                AppendProcessOutput(result.StdOut, false);
                AppendProcessOutput(result.StdErr, true);
                AppendLog($"終了コード: {result.ExitCode}");

                if (result.ExitCode == 0)
                {
                    RefreshEvaluationSummaryFromFile(jsonPath);
                }
            }
            catch (Exception ex)
            {
                AppendLog($"期間評価失敗: {ex.Message}");
            }
            finally
            {
                SetUiEnabled(true);
            }
        }

        private async void btnRunPre_Click(object sender, EventArgs e)
        {
            await RunPredictionAsync("PRE");
        }

        private async void btnRunLive_Click(object sender, EventArgs e)
        {
            await RunPredictionAsync("LIVE");
        }

        private async void btnEvaluate_Click(object sender, EventArgs e)
        {
            await RunEvaluationAsync();
        }

        private async void btnRangePredict_Click(object sender, EventArgs e)
        {
            await RunPredictionRangeAsync();
        }

        private async void btnRangeEvaluate_Click(object sender, EventArgs e)
        {
            await RunEvaluationRangeAsync();
        }
    }
}
