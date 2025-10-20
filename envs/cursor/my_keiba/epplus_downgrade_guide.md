
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
