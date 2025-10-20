using System;
using System.Diagnostics;
using System.IO;

namespace JVMonitor
{
    public class DataCollector
    {
        private string scriptFullPath;
        private Action<string> updateStatus;
        private Action<string> logMessage;

        public DataCollector(string scriptFullPath, Action<string> updateStatus, Action<string> logMessage)
        {
            this.scriptFullPath = scriptFullPath;
            this.updateStatus = updateStatus;
            this.logMessage = logMessage;
        }

        public void CollectData(bool incremental)
        {
            try
            {
                string searchDir = Path.GetDirectoryName(scriptFullPath);
                if (searchDir == null)
                {
                    logMessage("Error: Could not determine the script directory.");
                    updateStatus("スクリプトディレクトリの取得に失敗しました。");
                    return;
                }
                
                string pythonScriptPath = Path.Combine(searchDir, "update_today_data.py");

                if (!File.Exists(pythonScriptPath))
                {
                    logMessage($"Error: Python script not found at {pythonScriptPath}");
                    updateStatus("Pythonスクリプトが見つかりません。");
                    return;
                }

                ProcessStartInfo startInfo = new ProcessStartInfo
                {
                    FileName = "python",
                    Arguments = $"\"{pythonScriptPath}\" {(incremental ? "--incremental" : "")}",
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true,
                    WorkingDirectory = searchDir
                };

                using (Process process = new Process { StartInfo = startInfo })
                {
                    process.OutputDataReceived += (sender, e) => { if (e.Data != null) logMessage("Output: " + e.Data); };
                    process.ErrorDataReceived += (sender, e) => { if (e.Data != null) logMessage("Error: " + e.Data); };

                    process.Start();
                    process.BeginOutputReadLine();
                    process.BeginErrorReadLine();

                    process.WaitForExit();

                    if (process.ExitCode == 0)
                    {
                        updateStatus("データ取得が正常に完了しました。");
                    }
                    else
                    {
                        updateStatus($"データ取得プロセスがエラーコード {process.ExitCode} で終了しました。");
                    }
                }
            }
            catch (Exception ex)
            {
                logMessage($"エラーが発生しました: {ex.Message}");
                updateStatus("データ取得中にエラーが発生しました。");
            }
        }
    }
}