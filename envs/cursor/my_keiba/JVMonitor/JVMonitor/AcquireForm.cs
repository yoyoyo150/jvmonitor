using System;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Text.Json;
using System.Windows.Forms;

namespace JVMonitor
{
    public sealed class AcquireForm : Form
    {
        TextBox tbExe = null!;
        TextBox tbDiff = null!;
        TextBox tbReal = null!;
        TextBox tbNormal = null!;
        TextBox tbSetup = null!;
        DateTimePicker dtp = null!;
        TextBox txtLog = null!;

        public AcquireForm()
        {
            Text = "取得ツール (JVLinkToSQLite ランチャー)";
            Width = 1000;
            Height = 720;
            StartPosition = FormStartPosition.CenterParent;

            var panel = new TableLayoutPanel { Dock = DockStyle.Fill, ColumnCount = 1, RowCount = 3 };
            panel.RowStyles.Add(new RowStyle(SizeType.Absolute, 180));
            panel.RowStyles.Add(new RowStyle(SizeType.Absolute, 60));
            panel.RowStyles.Add(new RowStyle(SizeType.Percent, 100));
            Controls.Add(panel);

            var top = new TableLayoutPanel { Dock = DockStyle.Fill, ColumnCount = 3, RowCount = 6, Padding = new Padding(8) };
            top.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 120));
            top.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100));
            top.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 100));
            panel.Controls.Add(top, 0, 0);

            void AddPickRow(int row, string label, out TextBox tb, EventHandler onPick)
            {
                top.Controls.Add(new Label { Text = label, AutoSize = true, Anchor = AnchorStyles.Left, Padding = new Padding(0, 6, 0, 0) }, 0, row);
                tb = new TextBox { Dock = DockStyle.Fill };
                top.Controls.Add(tb, 1, row);
                var btn = new Button { Text = "参照…", Dock = DockStyle.Fill };
                btn.Click += onPick;
                top.Controls.Add(btn, 2, row);
            }

            AddPickRow(0, "EXE", out tbExe, (s, e) => PickFile(tbExe, "EXE|*.exe"));
            AddPickRow(1, "Diff.xml", out tbDiff, (s, e) => PickFile(tbDiff, "XML|*.xml"));
            AddPickRow(2, "Realtime.xml", out tbReal, (s, e) => PickFile(tbReal, "XML|*.xml"));
            AddPickRow(3, "Normal.xml", out tbNormal, (s, e) => PickFile(tbNormal, "XML|*.xml"));
            AddPickRow(4, "Setup.xml", out tbSetup, (s, e) => PickFile(tbSetup, "XML|*.xml"));

            top.Controls.Add(new Label { Text = "開催日", AutoSize = true, Anchor = AnchorStyles.Left, Padding = new Padding(0, 6, 0, 0) }, 0, 5);
            dtp = new DateTimePicker { Format = DateTimePickerFormat.Custom, CustomFormat = "yyyy年MM月dd日", Dock = DockStyle.Left, Width = 160 };
            dtp.Value = DateTime.Today;
            top.Controls.Add(dtp, 1, 5);

            var mid = new FlowLayoutPanel { Dock = DockStyle.Fill, FlowDirection = FlowDirection.LeftToRight, Padding = new Padding(8) };
            panel.Controls.Add(mid, 0, 1);
            var btnRunDiff = new Button { Text = "差分 (DIFF/DIFN)", Width = 160 }; btnRunDiff.Click += (s, e) => RunWithTemplate(tbDiff.Text, "差分");
            var btnRunO1 = new Button { Text = "オッズ (O1)", Width = 140 }; btnRunO1.Click += (s, e) => RunWithTemplate(tbReal.Text, "オッズ(O1)");
            var btnRunNormal = new Button { Text = "通常 (RACE等)", Width = 160 }; btnRunNormal.Click += (s, e) => RunWithTemplate(tbNormal.Text, "通常");
            var btnRunSetup = new Button { Text = "セットアップ", Width = 120 }; btnRunSetup.Click += (s, e) => RunWithTemplate(tbSetup.Text, "セットアップ");
            mid.Controls.AddRange(new Control[] { btnRunDiff, btnRunO1, btnRunNormal, btnRunSetup });

            txtLog = new TextBox { Dock = DockStyle.Fill, Multiline = true, ScrollBars = ScrollBars.Vertical, ReadOnly = true, BackColor = System.Drawing.Color.White };
            panel.Controls.Add(txtLog, 0, 2);

            LoadDefaultsFromAppSettings();
        }

        void PickFile(TextBox tb, string filter)
        {
            try
            {
                using var dlg = new OpenFileDialog();
                dlg.Filter = filter;
                if (!string.IsNullOrEmpty(tb.Text))
                {
                    try { dlg.InitialDirectory = Path.GetDirectoryName(tb.Text); } catch { }
                    dlg.FileName = Path.GetFileName(tb.Text);
                }
                if (dlg.ShowDialog(this) == DialogResult.OK) tb.Text = dlg.FileName;
            }
            catch (Exception ex) { Log($"参照エラー: {ex.Message}"); }
        }

        void LoadDefaultsFromAppSettings()
        {
            try
            {
                var cfg = Path.Combine(AppContext.BaseDirectory, "appsettings.json");
                if (!File.Exists(cfg)) return;
                using var fs = File.OpenRead(cfg);
                using var doc = JsonDocument.Parse(fs);
                if (doc.RootElement.TryGetProperty("Paths", out var paths))
                {
                    tbExe.Text = paths.TryGetProperty("JvToolPath", out var v1) ? (v1.GetString() ?? tbExe.Text) : tbExe.Text;
                    tbDiff.Text = paths.TryGetProperty("DiffSetting", out var v2) ? (v2.GetString() ?? tbDiff.Text) : tbDiff.Text;
                    tbNormal.Text = paths.TryGetProperty("NormalSetting", out var v3) ? (v3.GetString() ?? tbNormal.Text) : tbNormal.Text;
                    tbReal.Text = paths.TryGetProperty("RealtimeSetting", out var v4) ? (v4.GetString() ?? tbReal.Text) : tbReal.Text;
                    tbSetup.Text = paths.TryGetProperty("SetupSetting", out var v5) ? (v5.GetString() ?? tbSetup.Text) : tbSetup.Text;
                }
            }
            catch { }
        }

        async void RunWithTemplate(string templatePath, string label)
        {
            try
            {
                if (!File.Exists(tbExe.Text)) { MessageBox.Show("EXEパスが無効です", "実行不可", MessageBoxButtons.OK, MessageBoxIcon.Warning); return; }
                if (!File.Exists(templatePath)) { MessageBox.Show($"テンプレートが見つかりません:\n{templatePath}", "実行不可", MessageBoxButtons.OK, MessageBoxIcon.Warning); return; }

                // KaisaiDateTime を開催日に置換して一時ファイルへ
                var xml = await File.ReadAllTextAsync(templatePath, Encoding.UTF8);
                var yyyyMMdd = dtp.Value.ToString("yyyy-MM-dd");
                xml = System.Text.RegularExpressions.Regex.Replace(
                    xml,
                    @"(<KaisaiDateTime>)(.*?)(</KaisaiDateTime>)",
                    $"$1{yyyyMMdd}T00:00:00+09:00$3",
                    System.Text.RegularExpressions.RegexOptions.Singleline);
                // セキュアな一時フォルダ（ユーザーの LocalAppData 配下）を使用
                var safeTempDir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "JVMonitor", "Temp");
                Directory.CreateDirectory(safeTempDir);
                var temp = Path.Combine(safeTempDir, $"jv_template_{label}_{Guid.NewGuid():N}.xml");
                await File.WriteAllTextAsync(temp, xml, new UTF8Encoding(false));

                var psi = new ProcessStartInfo
                {
                    FileName = tbExe.Text,
                    Arguments = $"-m exec -s \"{temp}\"",
                    UseShellExecute = false,
                    CreateNoWindow = true,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    StandardOutputEncoding = Encoding.GetEncoding(932),
                    StandardErrorEncoding = Encoding.GetEncoding(932)
                };
                var p = new Process { StartInfo = psi };
                var sbOut = new StringBuilder();
                var sbErr = new StringBuilder();
                p.OutputDataReceived += (s, e) => { if (e.Data != null) sbOut.AppendLine(e.Data); };
                p.ErrorDataReceived += (s, e) => { if (e.Data != null) sbErr.AppendLine(e.Data); };
                p.Start();
                p.BeginOutputReadLine();
                p.BeginErrorReadLine();
                await System.Threading.Tasks.Task.Run(() => p.WaitForExit());

                if (p.ExitCode != 0)
                {
                    Log($"{label} 実行エラー (ExitCode={p.ExitCode})\r\n[OUT]\r\n{sbOut}\r\n[ERR]\r\n{sbErr}");
                    MessageBox.Show($"{label} 実行エラー\r\n{sbErr}", "エラー", MessageBoxButtons.OK, MessageBoxIcon.Error);
                }
                else
                {
                    Log($"{label} 実行成功\r\n[OUT]\r\n{sbOut}");
                }
            }
            catch (Exception ex)
            {
                Log($"{label} 実行例外: {ex.Message}");
                MessageBox.Show($"{label} 実行例外: {ex.Message}", "例外", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        void Log(string msg)
        {
            var ts = DateTime.Now.ToString("HH:mm:ss");
            txtLog.AppendText($"[{ts}] {msg}\r\n");
        }
    }
}


