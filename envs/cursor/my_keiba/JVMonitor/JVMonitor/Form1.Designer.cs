namespace JVMonitor
{
    partial class Form1
    {
        private System.ComponentModel.IContainer components = null;

        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        private void InitializeComponent()
        {
            mainPanel = new TableLayoutPanel();
            flowLayoutPanelTop = new FlowLayoutPanel();
            lblToday = new Label();
            btnRefreshDate = new Button();
            lblFrom = new Label();
            dtFrom = new DateTimePicker();
            // 不要なボタンを削除
            // btnRunDiff = new Button();
            // btnAcquireTool = new Button();
            // btnPickExe = new Button();
            // chkOdds = new CheckBox();
            btnImportMarksIncremental = new Button();
            btnImportMarksOverwrite = new Button();
            btnDataIntegrityCheck = new Button();
            btnLogic1Report = new Button();
            btnOpenPrediction = new Button();
            panelCenter = new Panel();
            lblRaceHeader = new Label();
            dgvEntries = new DataGridView();
            txtStatus = new TextBox();
            lblStatus = new Label();
            mainPanel.SuspendLayout();
            flowLayoutPanelTop.SuspendLayout();
            panelCenter.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(dgvEntries)).BeginInit();
            SuspendLayout();
            // 
            // mainPanel
            // 
            mainPanel.ColumnCount = 1;
            mainPanel.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100F));
            mainPanel.Controls.Add(flowLayoutPanelTop, 0, 0);
            mainPanel.Controls.Add(panelCenter, 0, 1);
            mainPanel.Controls.Add(txtStatus, 0, 2);
            mainPanel.Controls.Add(lblStatus, 0, 3);
            mainPanel.Dock = DockStyle.Fill;
            mainPanel.Location = new Point(0, 0);
            mainPanel.Name = "mainPanel";
            mainPanel.RowCount = 4;
            mainPanel.RowStyles.Add(new RowStyle(SizeType.Absolute, 50F));
            mainPanel.RowStyles.Add(new RowStyle(SizeType.Percent, 100F));
            mainPanel.RowStyles.Add(new RowStyle(SizeType.Absolute, 80F));
            mainPanel.RowStyles.Add(new RowStyle(SizeType.Absolute, 25F));
            mainPanel.Size = new Size(1200, 750);
            mainPanel.TabIndex = 0;
            // 
            // flowLayoutPanelTop
            // 
            flowLayoutPanelTop.AutoScroll = true;
            flowLayoutPanelTop.Controls.Add(lblToday);
            flowLayoutPanelTop.Controls.Add(btnRefreshDate);
            flowLayoutPanelTop.Controls.Add(lblFrom);
            flowLayoutPanelTop.Controls.Add(dtFrom);
            flowLayoutPanelTop.Controls.Add(btnImportMarksIncremental);
            flowLayoutPanelTop.Controls.Add(btnImportMarksOverwrite);
            flowLayoutPanelTop.Controls.Add(btnDataIntegrityCheck);
            flowLayoutPanelTop.Controls.Add(btnLogic1Report);
            flowLayoutPanelTop.Controls.Add(btnOpenPrediction);
            // 不要なボタンを削除
            // flowLayoutPanelTop.Controls.Add(btnRunDiff);
            // flowLayoutPanelTop.Controls.Add(btnPickExe);
            // flowLayoutPanelTop.Controls.Add(chkOdds);
            flowLayoutPanelTop.Dock = DockStyle.Fill;
            flowLayoutPanelTop.Location = new Point(3, 3);
            flowLayoutPanelTop.Name = "flowLayoutPanelTop";
            flowLayoutPanelTop.Size = new Size(1194, 44);
            flowLayoutPanelTop.TabIndex = 0;
            flowLayoutPanelTop.WrapContents = false;
            // 
            // lblToday
            // 
            lblToday.Anchor = AnchorStyles.Left;
            lblToday.AutoSize = true;
            lblToday.Font = new Font("Yu Gothic UI", 12F, FontStyle.Bold, GraphicsUnit.Point);
            lblToday.Location = new Point(3, 6);
            lblToday.Name = "lblToday";
            lblToday.Size = new Size(94, 21);
            lblToday.TabIndex = 0;
            lblToday.Text = "2025-09-06";
            lblToday.TextAlign = ContentAlignment.MiddleCenter;
            // 
            // btnRefreshDate
            // 
            btnRefreshDate.Location = new Point(103, 5);
            btnRefreshDate.Margin = new Padding(3, 5, 3, 3);
            btnRefreshDate.Name = "btnRefreshDate";
            btnRefreshDate.Size = new Size(50, 25);
            btnRefreshDate.TabIndex = 1;
            btnRefreshDate.Text = "更新";
            btnRefreshDate.UseVisualStyleBackColor = true;
            btnRefreshDate.Click += BtnRefreshDate_Click;
            // 
            // lblFrom
            // 
            lblFrom.Anchor = AnchorStyles.Left;
            lblFrom.AutoSize = true;
            lblFrom.Location = new Point(159, 9);
            lblFrom.Name = "lblFrom";
            lblFrom.Size = new Size(46, 15);
            lblFrom.TabIndex = 10;
            lblFrom.Text = "開催日:";
            // 
            // dtFrom
            // 
            dtFrom.CustomFormat = "yyyy年MM月dd日";
            dtFrom.Format = DateTimePickerFormat.Custom;
            dtFrom.Location = new Point(211, 8);
            dtFrom.Margin = new Padding(3, 8, 3, 3);
            dtFrom.Name = "dtFrom";
            dtFrom.Size = new Size(135, 23);
            dtFrom.TabIndex = 11;
            // 
            // btnImportMarksIncremental
            // 
            btnImportMarksIncremental.BackColor = Color.LightBlue;
            btnImportMarksIncremental.Font = new Font("Yu Gothic UI", 9F, FontStyle.Bold, GraphicsUnit.Point);
            btnImportMarksIncremental.Location = new Point(352, 5);
            btnImportMarksIncremental.Margin = new Padding(3, 5, 3, 3);
            btnImportMarksIncremental.Name = "btnImportMarksIncremental";
            btnImportMarksIncremental.Size = new Size(100, 25);
            btnImportMarksIncremental.TabIndex = 2;
            btnImportMarksIncremental.Text = "\u30a8\u30af\u30bb\u30eb\u66f4\u65b0(\u672a\u51e6\u7406\u30fb7\u65e5\u5206)";
            btnImportMarksIncremental.UseVisualStyleBackColor = false;
            btnImportMarksIncremental.Click += BtnImportMarksIncremental_Click;
            // 
            // btnImportMarksOverwrite
            // 
            btnImportMarksOverwrite.BackColor = Color.LightCoral;
            btnImportMarksOverwrite.Font = new Font("Yu Gothic UI", 9F, FontStyle.Bold, GraphicsUnit.Point);
            btnImportMarksOverwrite.Location = new Point(458, 5);
            btnImportMarksOverwrite.Margin = new Padding(3, 5, 3, 3);
            btnImportMarksOverwrite.Name = "btnImportMarksOverwrite";
            btnImportMarksOverwrite.Size = new Size(100, 25);
            btnImportMarksOverwrite.TabIndex = 3;
            btnImportMarksOverwrite.Text = "\u30a8\u30af\u30bb\u30eb\u66f4\u65b0(\u5168\u4ef6)";
            btnImportMarksOverwrite.UseVisualStyleBackColor = false;
            btnImportMarksOverwrite.Click += BtnImportMarksOverwrite_Click;
            // 
            // btnDataIntegrityCheck
            // 
            btnDataIntegrityCheck.BackColor = Color.LightBlue;
            btnDataIntegrityCheck.Font = new Font("Yu Gothic UI", 9F, FontStyle.Bold, GraphicsUnit.Point);
            btnDataIntegrityCheck.Location = new Point(564, 5);
            btnDataIntegrityCheck.Margin = new Padding(3, 5, 3, 3);
            btnDataIntegrityCheck.Name = "btnDataIntegrityCheck";
            btnDataIntegrityCheck.Size = new Size(100, 25);
            btnDataIntegrityCheck.TabIndex = 4;
            btnDataIntegrityCheck.Text = "整合性チェック";
            btnDataIntegrityCheck.UseVisualStyleBackColor = false;
            btnDataIntegrityCheck.Click += BtnDataIntegrityCheck_Click;
            // 
            // btnLogic1Report
            // 
            btnLogic1Report.BackColor = Color.LightGreen;
            btnLogic1Report.Font = new Font("Yu Gothic UI", 9F, FontStyle.Bold, GraphicsUnit.Point);
            btnLogic1Report.Location = new Point(670, 5);
            btnLogic1Report.Margin = new Padding(3, 5, 3, 3);
            btnLogic1Report.Name = "btnLogic1Report";
            btnLogic1Report.Size = new Size(100, 25);
            btnLogic1Report.TabIndex = 5;
            btnLogic1Report.Text = "ロジック1評価";
            btnLogic1Report.UseVisualStyleBackColor = false;
            btnLogic1Report.Click += BtnLogic1Report_Click;
            // 
            // btnOpenPrediction
            // 
            btnOpenPrediction.BackColor = Color.Gainsboro;
            btnOpenPrediction.Font = new Font("Yu Gothic UI", 9F, FontStyle.Regular, GraphicsUnit.Point);
            btnOpenPrediction.Location = new Point(776, 5);
            btnOpenPrediction.Margin = new Padding(3, 5, 3, 3);
            btnOpenPrediction.Name = "btnOpenPrediction";
            btnOpenPrediction.Size = new Size(110, 25);
            btnOpenPrediction.TabIndex = 4;
            btnOpenPrediction.Text = "予想・評価パネル";
            btnOpenPrediction.UseVisualStyleBackColor = false;
            btnOpenPrediction.Click += BtnOpenPrediction_Click;
            // 
            // btnRunDiff - 削除
            /*
            btnRunDiff.BackColor = Color.PaleGreen;
            btnRunDiff.Font = new Font("Yu Gothic UI", 9F, FontStyle.Bold, GraphicsUnit.Point);
            btnRunDiff.Location = new Point(352, 5);
            btnRunDiff.Margin = new Padding(3, 5, 3, 3);
            btnRunDiff.Name = "btnRunDiff";
            btnRunDiff.Size = new Size(90, 25);
            btnRunDiff.TabIndex = 2;
            btnRunDiff.Text = "差分更新";
            btnRunDiff.UseVisualStyleBackColor = false;
            btnRunDiff.Click += BtnRunDiff_Click;
            */
            // 
            // btnAcquireTool
            // 
            /*
            btnAcquireTool.Location = new Point(448, 5);
            btnAcquireTool.Margin = new Padding(3, 5, 3, 3);
            btnAcquireTool.Name = "btnAcquireTool";
            btnAcquireTool.Size = new Size(90, 25);
            btnAcquireTool.TabIndex = 22;
            btnAcquireTool.Text = "取得ツール…";
            btnAcquireTool.UseVisualStyleBackColor = true;
            btnAcquireTool.Click += BtnAcquireTool_Click;
            */
            // 
            // btnPickExe - 削除
            /*
            btnPickExe.Location = new Point(544, 5);
            btnPickExe.Margin = new Padding(3, 5, 3, 3);
            btnPickExe.Name = "btnPickExe";
            btnPickExe.Size = new Size(90, 25);
            btnPickExe.TabIndex = 20;
            btnPickExe.Text = "EXE選択…";
            btnPickExe.UseVisualStyleBackColor = true;
            btnPickExe.Click += BtnPickExe_Click;
            */
            // 
            // chkOdds - 削除
            /*
            chkOdds.AutoSize = true;
            chkOdds.Location = new Point(640, 9);
            chkOdds.Margin = new Padding(3, 9, 3, 3);
            chkOdds.Name = "chkOdds";
            chkOdds.Size = new Size(82, 19);
            chkOdds.TabIndex = 21;
            chkOdds.Text = "オッズ取得";
            chkOdds.UseVisualStyleBackColor = true;
            chkOdds.Checked = true;
            */
            // 
            // panelCenter
            // 
            panelCenter.Controls.Add(dgvEntries);
            panelCenter.Controls.Add(lblRaceHeader);
            panelCenter.Dock = DockStyle.Fill;
            panelCenter.Location = new Point(3, 53);
            panelCenter.Name = "panelCenter";
            panelCenter.Size = new Size(1194, 592);
            panelCenter.TabIndex = 4;
            // 
            // lblRaceHeader
            // 
            lblRaceHeader.Dock = DockStyle.Top;
            lblRaceHeader.Font = new Font("Yu Gothic UI", 9F, FontStyle.Bold, GraphicsUnit.Point);
            lblRaceHeader.Padding = new Padding(6, 4, 6, 4);
            lblRaceHeader.Height = 24;
            lblRaceHeader.Text = "";
            // 
            // dgvEntries
            // 
            dgvEntries.Dock = DockStyle.Fill;
            dgvEntries.ReadOnly = true;
            dgvEntries.AllowUserToAddRows = false;
            dgvEntries.AllowUserToDeleteRows = false;
            dgvEntries.RowHeadersVisible = false;
            dgvEntries.AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.None;
            // 
            // txtStatus
            // 
            txtStatus.BackColor = Color.White;
            txtStatus.Dock = DockStyle.Fill;
            txtStatus.ForeColor = Color.Black;
            txtStatus.Location = new Point(3, 651);
            txtStatus.Multiline = true;
            txtStatus.Name = "txtStatus";
            txtStatus.ReadOnly = true;
            txtStatus.ScrollBars = ScrollBars.Vertical;
            txtStatus.Size = new Size(1194, 74);
            txtStatus.TabIndex = 3;
            // 
            // lblStatus
            // 
            lblStatus.BorderStyle = BorderStyle.FixedSingle;
            lblStatus.Dock = DockStyle.Fill;
            lblStatus.Location = new Point(3, 731);
            lblStatus.Name = "lblStatus";
            lblStatus.Padding = new Padding(5);
            lblStatus.Size = new Size(1194, 19);
            lblStatus.TabIndex = 2;
            lblStatus.Text = "準備完了";
            lblStatus.TextAlign = ContentAlignment.MiddleLeft;
            // 
            // Form1
            // 
            AutoScaleDimensions = new SizeF(7F, 15F);
            AutoScaleMode = AutoScaleMode.Font;
            ClientSize = new Size(1200, 750);
            Controls.Add(mainPanel);
            Name = "Form1";
            Text = "JVMonitor";
            Load += Form1_Load;
            mainPanel.ResumeLayout(false);
            mainPanel.PerformLayout();
            flowLayoutPanelTop.ResumeLayout(false);
            flowLayoutPanelTop.PerformLayout();
            panelCenter.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(dgvEntries)).EndInit();
            ResumeLayout(false);

        }

        private System.Windows.Forms.TableLayoutPanel mainPanel;
        private System.Windows.Forms.FlowLayoutPanel flowLayoutPanelTop;
        private System.Windows.Forms.Label lblToday;
        private System.Windows.Forms.Button btnRefreshDate;
        // private System.Windows.Forms.Button btnRunDiff; // 削除
        private System.Windows.Forms.Label lblFrom;
        private System.Windows.Forms.DateTimePicker dtFrom;
        private System.Windows.Forms.TextBox txtStatus;
        private System.Windows.Forms.Label lblStatus;
        // private System.Windows.Forms.Button btnPickExe; // 削除
        // private System.Windows.Forms.Button btnAcquireTool;
        // private System.Windows.Forms.CheckBox chkOdds; // 削除
        private System.Windows.Forms.Panel panelCenter;
        private System.Windows.Forms.Label lblRaceHeader;
        private System.Windows.Forms.DataGridView dgvEntries;
        private System.Windows.Forms.Button btnImportMarksIncremental;
        private System.Windows.Forms.Button btnImportMarksOverwrite;
        private System.Windows.Forms.Button btnDataIntegrityCheck;
        private System.Windows.Forms.Button btnLogic1Report;
        private System.Windows.Forms.Button btnOpenPrediction;
    }
}


