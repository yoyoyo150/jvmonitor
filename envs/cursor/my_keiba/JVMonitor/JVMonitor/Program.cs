using System;
using System.Text;
using System.Windows.Forms;
using OfficeOpenXml;

namespace JVMonitor
{
    internal static class Program
    {
        [STAThread]
        static void Main()
        {
            // EPPlus 8以降ではライセンスを明示的に設定する必要がある（非商用利用）
            var license = ExcelPackage.License;
            license?.SetNonCommercialPersonal("JVMonitor User");

            // 追加: 932(Shift_JIS) 等のコードページを利用可能にする
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);

            ApplicationConfiguration.Initialize();
            Application.Run(new Form1());
        }
    }
}
