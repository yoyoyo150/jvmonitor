namespace JVMonitor
{
    partial class RaceBrowserForm
    {
        private System.ComponentModel.IContainer components = null;

        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null)) components.Dispose();
            base.Dispose(disposing);
        }

        private void InitializeComponent()
        {
            this.splitContainer1 = new System.Windows.Forms.SplitContainer();
            this.gridRaces = new System.Windows.Forms.DataGridView();
            this.gridEntries = new System.Windows.Forms.DataGridView();
            ((System.ComponentModel.ISupportInitialize)(this.splitContainer1)).BeginInit();
            this.splitContainer1.Panel1.SuspendLayout();
            this.splitContainer1.Panel2.SuspendLayout();
            this.splitContainer1.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.gridRaces)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.gridEntries)).BeginInit();
            this.SuspendLayout();
            // 
            // splitContainer1
            // 
            this.splitContainer1.Dock = System.Windows.Forms.DockStyle.Fill;
            this.splitContainer1.Location = new System.Drawing.Point(0, 0);
            this.splitContainer1.Name = "splitContainer1";
            this.splitContainer1.Orientation = System.Windows.Forms.Orientation.Horizontal;
            // 
            // splitContainer1.Panel1
            // 
            this.splitContainer1.Panel1.Controls.Add(this.gridRaces);
            // 
            // splitContainer1.Panel2
            // 
            this.splitContainer1.Panel2.Controls.Add(this.gridEntries);
            this.splitContainer1.Size = new System.Drawing.Size(1200, 700);
            this.splitContainer1.SplitterDistance = 320;
            this.splitContainer1.TabIndex = 0;
            // 
            // gridRaces
            // 
            this.gridRaces.AllowUserToAddRows = false;
            this.gridRaces.AllowUserToDeleteRows = false;
            this.gridRaces.AutoSizeColumnsMode = System.Windows.Forms.DataGridViewAutoSizeColumnsMode.Fill;
            this.gridRaces.BackgroundColor = System.Drawing.Color.White;
            this.gridRaces.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.gridRaces.Dock = System.Windows.Forms.DockStyle.Fill;
            this.gridRaces.Location = new System.Drawing.Point(0, 0);
            this.gridRaces.MultiSelect = false;
            this.gridRaces.Name = "gridRaces";
            this.gridRaces.ReadOnly = true;
            this.gridRaces.RowHeadersVisible = false;
            this.gridRaces.SelectionMode = System.Windows.Forms.DataGridViewSelectionMode.FullRowSelect;
            this.gridRaces.Size = new System.Drawing.Size(1200, 320);
            this.gridRaces.TabIndex = 0;
            this.gridRaces.SelectionChanged += new System.EventHandler(this.gridRaces_SelectionChanged);
            // 
            // gridEntries
            // 
            this.gridEntries.AllowUserToAddRows = false;
            this.gridEntries.AllowUserToDeleteRows = false;
            this.gridEntries.AutoSizeColumnsMode = System.Windows.Forms.DataGridViewAutoSizeColumnsMode.Fill;
            this.gridEntries.BackgroundColor = System.Drawing.Color.White;
            this.gridEntries.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.gridEntries.Dock = System.Windows.Forms.DockStyle.Fill;
            this.gridEntries.Location = new System.Drawing.Point(0, 0);
            this.gridEntries.MultiSelect = false;
            this.gridEntries.Name = "gridEntries";
            this.gridEntries.ReadOnly = true;
            this.gridEntries.RowHeadersVisible = false;
            this.gridEntries.SelectionMode = System.Windows.Forms.DataGridViewSelectionMode.FullRowSelect;
            this.gridEntries.Size = new System.Drawing.Size(1200, 376);
            this.gridEntries.TabIndex = 1;
            // 
            // RaceBrowserForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(7F, 15F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(1200, 700);
            this.Controls.Add(this.splitContainer1);
            this.Name = "RaceBrowserForm";
            this.Text = "レース/出馬ブラウザ";
            this.splitContainer1.Panel1.ResumeLayout(false);
            this.splitContainer1.Panel2.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.splitContainer1)).EndInit();
            this.splitContainer1.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.gridRaces)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.gridEntries)).EndInit();
            this.ResumeLayout(false);
        }

        private System.Windows.Forms.SplitContainer splitContainer1;
        private System.Windows.Forms.DataGridView gridRaces;
        private System.Windows.Forms.DataGridView gridEntries;
    }
}
