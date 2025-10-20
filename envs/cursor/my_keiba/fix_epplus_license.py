# -*- coding: utf-8 -*-
import sys
import io

# UTF-8エンコーディング設定
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def create_epplus_license_fix():
    """EPPlusライセンス問題の修正"""
    print("=== EPPlusライセンス問題の修正 ===\n")
    
    # 1. ライセンス設定用のC#コードを作成
    csharp_code = '''
// EPPlusライセンス設定
using OfficeOpenXml;

// アプリケーション起動時に実行
ExcelPackage.LicenseContext = LicenseContext.NonCommercial;

// または商用ライセンスの場合
// ExcelPackage.LicenseContext = LicenseContext.Commercial;
'''
    
    with open('epplus_license_fix.cs', 'w', encoding='utf-8') as f:
        f.write(csharp_code)
    
    print("[OK] epplus_license_fix.cs を作成しました")
    
    # 2. Program.csの修正案を作成
    program_cs_fix = '''
// Program.cs の修正案
// アプリケーション起動時にEPPlusライセンスを設定

using OfficeOpenXml;

namespace JVMonitor
{
    internal static class Program
    {
        [STAThread]
        static void Main()
        {
            // EPPlusライセンス設定（アプリケーション起動時）
            ExcelPackage.LicenseContext = LicenseContext.NonCommercial;
            
            // 既存のコード
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new Form1());
        }
    }
}
'''
    
    with open('program_cs_fix.cs', 'w', encoding='utf-8') as f:
        f.write(program_cs_fix)
    
    print("[OK] program_cs_fix.cs を作成しました")
    
    # 3. 修正手順の説明
    print("\n=== 修正手順 ===")
    print("1. JVMonitorプロジェクトのProgram.csを開く")
    print("2. Main()メソッドの最初に以下を追加:")
    print("   ExcelPackage.LicenseContext = LicenseContext.NonCommercial;")
    print("3. プロジェクトを再ビルド")
    print("4. JVMonitor.exeを再実行")
    
    # 4. 代替案の提示
    print("\n=== 代替案 ===")
    print("1. EPPlusのバージョンをダウングレード（7.x系）")
    print("2. 商用ライセンスを購入")
    print("3. オープンソースの代替ライブラリを使用")

def create_epplus_downgrade_guide():
    """EPPlusダウングレードガイドの作成"""
    print("\n=== EPPlusダウングレードガイド ===")
    
    guide_content = '''
# EPPlusダウングレードガイド

## 問題
EPPlus 8.x系ではライセンス設定が必須になりました。

## 解決策1: ライセンス設定（推奨）
Program.csのMain()メソッドの最初に以下を追加:

```csharp
using OfficeOpenXml;

// アプリケーション起動時
ExcelPackage.LicenseContext = LicenseContext.NonCommercial;
```

## 解決策2: EPPlusダウングレード
1. プロジェクトファイル（.csproj）を編集
2. EPPlusのバージョンを7.x系に変更

```xml
<PackageReference Include="EPPlus" Version="7.4.2" />
```

3. プロジェクトを再ビルド

## 解決策3: 代替ライブラリ
- ClosedXML
- NPOI
- ExcelDataReader

## 修正後の確認
1. JVMonitor.exeを実行
2. ログでライセンスエラーが消えることを確認
3. Excelファイルの読み込みが正常に動作することを確認
'''
    
    with open('epplus_downgrade_guide.md', 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print("[OK] epplus_downgrade_guide.md を作成しました")

if __name__ == "__main__":
    create_epplus_license_fix()
    create_epplus_downgrade_guide()


