using System.Drawing;
using System.Windows.Forms;

namespace JVMonitor
{
    partial class PredictionForm
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        private void InitializeComponent()
        {
            tableLayoutPanel = new TableLayoutPanel();
            panelParameters = new Panel();
            lblDate = new Label();
            dtPredictionDate = new DateTimePicker();
            lblScenario = new Label();
            cmbScenario = new ComboBox();
            lblRankInfo = new Label();

            btnRunPre = new Button();
            btnRunLive = new Button();
            btnEvaluate = new Button();
            groupSimulation = new GroupBox();
            lblRangeFrom = new Label();
            dtRangeFrom = new DateTimePicker();
            lblRangeTo = new Label();
            dtRangeTo = new DateTimePicker();
            btnRangePredict = new Button();
            btnRangeEvaluate = new Button();
            txtLog = new TextBox();
            tableLayoutPanel.SuspendLayout();
            panelParameters.SuspendLayout();
            groupSimulation.SuspendLayout();
            SuspendLayout();
            // 
            // tableLayoutPanel
            // 
            tableLayoutPanel.ColumnCount = 1;
            tableLayoutPanel.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100F));
            tableLayoutPanel.Controls.Add(panelParameters, 0, 0);
            tableLayoutPanel.Controls.Add(txtLog, 0, 1);
            tableLayoutPanel.Dock = DockStyle.Fill;
            tableLayoutPanel.Location = new System.Drawing.Point(0, 0);
            tableLayoutPanel.Name = "tableLayoutPanel";
            tableLayoutPanel.RowCount = 2;
            tableLayoutPanel.RowStyles.Add(new RowStyle(SizeType.Absolute, 200F));
            tableLayoutPanel.RowStyles.Add(new RowStyle(SizeType.Percent, 100F));
            tableLayoutPanel.Size = new System.Drawing.Size(720, 450);
            tableLayoutPanel.TabIndex = 0;
            // 
            // panelParameters
            // 
            panelParameters.Controls.Add(groupSimulation);
            panelParameters.Controls.Add(lblRankInfo);
            panelParameters.Controls.Add(btnEvaluate);
            panelParameters.Controls.Add(btnRunLive);
            panelParameters.Controls.Add(btnRunPre);
            panelParameters.Controls.Add(cmbScenario);
            panelParameters.Controls.Add(lblScenario);
            panelParameters.Controls.Add(dtPredictionDate);
            panelParameters.Controls.Add(lblDate);
            panelParameters.Dock = DockStyle.Fill;
            panelParameters.Location = new System.Drawing.Point(3, 3);
            panelParameters.Name = "panelParameters";
            panelParameters.Size = new System.Drawing.Size(714, 200);
            panelParameters.TabIndex = 0;
            // 
            // lblDate
            // 
            lblDate.AutoSize = true;
            lblDate.Location = new System.Drawing.Point(16, 18);
            lblDate.Name = "lblDate";
            lblDate.Size = new System.Drawing.Size(67, 15);
            lblDate.TabIndex = 0;
            lblDate.Text = "対象日付：";
            // 
            // dtPredictionDate
            // 
            dtPredictionDate.CustomFormat = "yyyy-MM-dd";
            dtPredictionDate.Format = DateTimePickerFormat.Custom;
            dtPredictionDate.Location = new System.Drawing.Point(110, 14);
            dtPredictionDate.Name = "dtPredictionDate";
            dtPredictionDate.Size = new System.Drawing.Size(140, 23);
            dtPredictionDate.TabIndex = 1;
            // 
            // lblScenario
            // 
            lblScenario.AutoSize = true;
            lblScenario.Location = new System.Drawing.Point(16, 55);
            lblScenario.Name = "lblScenario";
            lblScenario.Size = new System.Drawing.Size(68, 15);
            lblScenario.TabIndex = 2;
            lblScenario.Text = "シナリオ：";
            // 
            // cmbScenario
            // 
            cmbScenario.DropDownStyle = ComboBoxStyle.DropDownList;
            cmbScenario.FormattingEnabled = true;
            cmbScenario.Items.AddRange(new object[] { "PRE", "LIVE", "BACKTEST" });
            cmbScenario.Location = new System.Drawing.Point(110, 51);
            cmbScenario.Name = "cmbScenario";
            cmbScenario.Size = new System.Drawing.Size(140, 23);
            cmbScenario.TabIndex = 3;
            // 
            // lblRankInfo
            //
            lblRankInfo.AutoSize = true;
            lblRankInfo.Location = new System.Drawing.Point(16, 92);
            lblRankInfo.Name = "lblRankInfo";
            lblRankInfo.Size = new System.Drawing.Size(249, 15);
            lblRankInfo.TabIndex = 4;
            lblRankInfo.Text = "投資対象ランク: S/A （ml/config/rank_rules.json）";

            // btnRunPre
            // 
            btnRunPre.Location = new System.Drawing.Point(404, 14);
            btnRunPre.Name = "btnRunPre";
            btnRunPre.Size = new System.Drawing.Size(130, 30);
            btnRunPre.TabIndex = 5;
            btnRunPre.Text = "前日予想 (PRE)";
            btnRunPre.UseVisualStyleBackColor = true;
            btnRunPre.Click += btnRunPre_Click;
            // 
            // btnRunLive
            // 
            btnRunLive.Location = new System.Drawing.Point(544, 14);
            btnRunLive.Name = "btnRunLive";
            btnRunLive.Size = new System.Drawing.Size(130, 30);
            btnRunLive.TabIndex = 6;
            btnRunLive.Text = "当日 LIVE 更新";
            btnRunLive.UseVisualStyleBackColor = true;
            btnRunLive.Click += btnRunLive_Click;
            // 
            // btnEvaluate
            // 
            btnEvaluate.Location = new System.Drawing.Point(544, 53);
            btnEvaluate.Name = "btnEvaluate";
            btnEvaluate.Size = new System.Drawing.Size(130, 30);
            btnEvaluate.TabIndex = 7;
            btnEvaluate.Text = "結果評価";
            btnEvaluate.UseVisualStyleBackColor = true;
            btnEvaluate.Click += btnEvaluate_Click;
            // 
            // groupSimulation
            groupSimulation.Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right;
            groupSimulation.Controls.Add(btnRangeEvaluate);
            groupSimulation.Controls.Add(btnRangePredict);
            groupSimulation.Controls.Add(dtRangeTo);
            groupSimulation.Controls.Add(lblRangeTo);
            groupSimulation.Controls.Add(dtRangeFrom);
            groupSimulation.Controls.Add(lblRangeFrom);
            groupSimulation.Location = new System.Drawing.Point(16, 120);
            groupSimulation.Name = "groupSimulation";
            groupSimulation.Size = new System.Drawing.Size(674, 72);
            groupSimulation.TabIndex = 15;
            groupSimulation.TabStop = false;
            groupSimulation.Text = "期間シミュレーション";
            // 
            // lblRangeFrom
            lblRangeFrom.AutoSize = true;
            lblRangeFrom.Location = new System.Drawing.Point(16, 32);
            lblRangeFrom.Name = "lblRangeFrom";
            lblRangeFrom.Size = new System.Drawing.Size(66, 15);
            lblRangeFrom.TabIndex = 0;
            lblRangeFrom.Text = "開始日付";
            // 
            // dtRangeFrom
            dtRangeFrom.CustomFormat = "yyyy-MM-dd";
            dtRangeFrom.Format = DateTimePickerFormat.Custom;
            dtRangeFrom.Location = new System.Drawing.Point(100, 28);
            dtRangeFrom.Name = "dtRangeFrom";
            dtRangeFrom.Size = new System.Drawing.Size(130, 23);
            dtRangeFrom.TabIndex = 1;
            // 
            // lblRangeTo
            lblRangeTo.AutoSize = true;
            lblRangeTo.Location = new System.Drawing.Point(244, 32);
            lblRangeTo.Name = "lblRangeTo";
            lblRangeTo.Size = new System.Drawing.Size(54, 15);
            lblRangeTo.TabIndex = 2;
            lblRangeTo.Text = "終了日付";
            // 
            // dtRangeTo
            dtRangeTo.CustomFormat = "yyyy-MM-dd";
            dtRangeTo.Format = DateTimePickerFormat.Custom;
            dtRangeTo.Location = new System.Drawing.Point(318, 28);
            dtRangeTo.Name = "dtRangeTo";
            dtRangeTo.Size = new System.Drawing.Size(130, 23);
            dtRangeTo.TabIndex = 3;
            // 
            // btnRangePredict
            btnRangePredict.Anchor = AnchorStyles.Top | AnchorStyles.Right;
            btnRangePredict.Location = new System.Drawing.Point(470, 24);
            btnRangePredict.Name = "btnRangePredict";
            btnRangePredict.Size = new System.Drawing.Size(90, 30);
            btnRangePredict.TabIndex = 4;
            btnRangePredict.Text = "期間予測";
            btnRangePredict.UseVisualStyleBackColor = true;
            btnRangePredict.Click += btnRangePredict_Click;
            // 
            // btnRangeEvaluate
            btnRangeEvaluate.Anchor = AnchorStyles.Top | AnchorStyles.Right;
            btnRangeEvaluate.Location = new System.Drawing.Point(570, 24);
            btnRangeEvaluate.Name = "btnRangeEvaluate";
            btnRangeEvaluate.Size = new System.Drawing.Size(90, 30);
            btnRangeEvaluate.TabIndex = 5;
            btnRangeEvaluate.Text = "期間評価";
            btnRangeEvaluate.UseVisualStyleBackColor = true;
            btnRangeEvaluate.Click += btnRangeEvaluate_Click;
            // 
            // txtLog
            // 
            txtLog.Dock = DockStyle.Fill;
            txtLog.Location = new System.Drawing.Point(3, 183);
            txtLog.Multiline = true;
            txtLog.Name = "txtLog";
            txtLog.ReadOnly = true;
            txtLog.ScrollBars = ScrollBars.Vertical;
            txtLog.Size = new System.Drawing.Size(714, 264);
            txtLog.TabIndex = 1;
            // 
            // PredictionForm
            // 
            AutoScaleDimensions = new System.Drawing.SizeF(7F, 15F);
            AutoScaleMode = AutoScaleMode.Font;
            ClientSize = new System.Drawing.Size(720, 450);
            Controls.Add(tableLayoutPanel);
            FormBorderStyle = FormBorderStyle.FixedDialog;
            MaximizeBox = false;
            MinimizeBox = false;
            Name = "PredictionForm";
            StartPosition = FormStartPosition.CenterParent;
            Text = "予想・評価パネル";
            tableLayoutPanel.ResumeLayout(false);
            tableLayoutPanel.PerformLayout();
            panelParameters.ResumeLayout(false);
            panelParameters.PerformLayout();
            groupSimulation.ResumeLayout(false);
            groupSimulation.PerformLayout();
            ResumeLayout(false);
        }

        #endregion

        private TableLayoutPanel tableLayoutPanel;
        private Panel panelParameters;
        private Label lblDate;
        private DateTimePicker dtPredictionDate;
        private Label lblScenario;
        private ComboBox cmbScenario;
        private Label lblOddsMin;
        private Label lblRankInfo;
        private Button btnRunPre;
        private Button btnRunLive;
        private Button btnEvaluate;
        private GroupBox groupSimulation;
        private Label lblRangeFrom;
        private DateTimePicker dtRangeFrom;
        private Label lblRangeTo;
        private DateTimePicker dtRangeTo;
        private Button btnRangePredict;
        private Button btnRangeEvaluate;
        private TextBox txtLog;
    }
}
