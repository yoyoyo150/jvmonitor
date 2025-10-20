# JRA-VAN Data Lab VB.NET開発ステップ

## 概要
JRA-VAN Data Labを使用したVB.NETアプリケーション開発の段階的な学習手順です。各Lessonは前のLessonの機能を基に、新しい機能を追加する形で構成されています。

## 開発環境
- **開発言語**: VB.NET
- **フレームワーク**: .NET Framework 4.6.1
- **プラットフォーム**: x86 (32bit)
- **JV-Link SDK**: JRA-VAN Data Lab. SDK Ver4.9.0.2
- **ActiveXコントロール**: AxJVLink1

## Lesson-1: 基本的なJV-Link設定画面の表示

### 目的
JV-Linkの設定画面を表示する基本的な機能を実装します。

### 実装内容
- **フォーム**: 基本的なWindowsフォーム
- **メニュー**: 設定メニューの追加
- **JV-Link設定**: `AxJVLink1.JVSetUIProperties()`の呼び出し

### 主要コード
```vb
Private Sub mnuConfJV_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles mnuConfJV.Click
    Try
        Dim lReturnCode As Long
        lReturnCode = AxJVLink1.JVSetUIProperties()
        If lReturnCode <> 0 Then
            MsgBox("JVSetUIPropertiesエラーコード：" & lReturnCode & ":", MessageBoxIcon.Error)
        End If
    Catch ex As Exception
    End Try
End Sub
```

### 学習ポイント
- JV-Link ActiveXコントロールの基本的な使用方法
- エラーハンドリングの基本

---

## Lesson-2: JVInitとJVOpenの基本実装

### 目的
JV-Linkの初期化とデータ取得の開始処理を実装します。

### 実装内容
- **JVInit**: JV-Linkの初期化処理
- **JVOpen**: データ取得の開始
- **JVClose**: データ取得の終了
- **固定日付**: 2005年3月1日からのデータ取得

### 主要コード
```vb
Private Sub frmMain_Load(ByVal sender As Object, ByVal e As System.EventArgs) Handles Me.Load
    Dim sid As String = "Test"
    Dim lReturnCode As Long = Me.AxJVLink1.JVInit(sid)
    
    If lReturnCode <> 0 Then
        MsgBox("JVInitエラーコード:" & lReturnCode & ":", MessageBoxIcon.Error)
        Exit Sub
    End If
End Sub

Private Sub btnGetJVData_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnGetJVData.Click
    Dim strDataSpec As String = "RACE"
    Dim strFromTime As String = "20050301000000"
    Dim lOption As Long = 2
    
    Dim lReturnCode As Long = Me.AxJVLink1.JVOpen(strDataSpec, strFromTime, lOption, _
                        lReadCount, lDownloadCount, strLastFileTimestamp)
    
    ' JVClose処理
    lReturnCode = Me.AxJVLink1.JVClose()
End Sub
```

### 学習ポイント
- JVInit: JV-Linkの初期化
- JVOpen: データ取得の開始
- JVClose: データ取得の終了
- エラーコードの確認方法

---

## Lesson-3: JVReadによるデータ読み込みと表示

### 目的
JVReadを使用してデータを読み込み、画面に表示する機能を実装します。

### 実装内容
- **JVRead**: データの読み込み処理
- **データ構造体**: `JV_RA_RACE`構造体の使用
- **データ表示**: RichTextBoxへの表示
- **レコード識別**: "RA"レコードの処理

### 主要コード
```vb
Const lBuffSize As Long = 110000
Const lNameSize As Integer = 256
Dim strBuff As String = New String(vbNullChar, lBuffSize)
Dim strFileName As String = New String(vbNullChar, lNameSize)
Dim RaceInfo As JV_RA_RACE = New JV_RA_RACE

Do
    lReturnCode = Me.AxJVLink1.JVRead(strBuff, lBuffSize, strFileName)
    
    Select Case lReturnCode
        Case 0      ' 全ファイル読み込み終了
            Exit Do
        Case Is > 0 ' データ読み込み
            If Mid(strBuff, 1, 2) = "RA" Then
                RaceInfo.SetData(strBuff)
                rtbData.AppendText("年:" & RaceInfo.id.Year & " 月日:" & RaceInfo.id.MonthDay & ...)
            End If
    End Select
Loop While (1)
```

### 学習ポイント
- JVRead: データの読み込み
- データ構造体の使用方法
- レコードタイプの識別
- ループ処理によるデータ読み込み

---

## Lesson-4: プログレスバーとタイマーによる進捗表示

### 目的
データ取得の進捗を視覚的に表示する機能を実装します。

### 実装内容
- **プログレスバー**: ダウンロード進捗と読み込み進捗の表示
- **タイマー**: 定期的な進捗更新
- **JVStatus**: ダウンロード状況の取得
- **Application.DoEvents()**: UI応答性の維持

### 主要コード
```vb
' 進捗表示の初期設定
tmrDownload.Enabled = False
prgDownload.Value = 0
prgJVRead.Value = 0

' プログレスバーの最大値設定
If lDownloadCount = 0 Then
    prgDownload.Maximum = 100
    prgDownload.Value = 100
Else
    prgDownload.Maximum = lDownloadCount
    tmrDownload.Enabled = True
End If
prgJVRead.Maximum = lReadCount

' タイマー処理
Private Sub tmrDownload_Tick(ByVal sender As Object, ByVal e As System.EventArgs) Handles tmrDownload.Tick
    Dim lReturnCode As Long = AxJVLink1.JVStatus
    
    If lReturnCode < 0 Then
        ' エラー処理
    ElseIf lReturnCode < lDownloadCount Then
        prgDownload.Value = lReturnCode
    ElseIf lReturnCode = lDownloadCount Then
        tmrDownload.Enabled = False
        prgDownload.Value = lReturnCode
    End If
End Sub
```

### 学習ポイント
- プログレスバーの使用方法
- タイマーコントロールの使用方法
- JVStatusによる進捗取得
- UI応答性の維持方法

---

## Lesson-5: コード変換機能の追加

### 目的
競馬場コードなどの数値コードを人間が読める文字列に変換する機能を実装します。

### 実装内容
- **コード変換クラス**: `clsCodeConv`の使用
- **CSVファイル**: `CodeTable.csv`からのコード読み込み
- **競馬場名表示**: コードから競馬場名への変換
- **JVSkip**: 不要なレコードのスキップ

### 主要コード
```vb
' コード変換クラスインスタンス作成
objCodeConv = New clsCodeConv
objCodeConv.FileName = Application.StartupPath & "\CodeTable.csv"

' データ表示（コード変換付き）
rtbData.AppendText("年:" & RaceInfo.id.Year & _
                   " 月日:" & RaceInfo.id.MonthDay & _
                   " 場:" & objCodeConv.GetCodeName("2001", RaceInfo.id.JyoCD, "3") & _
                   " 回:" & RaceInfo.id.Kaiji & _
                   " 日目:" & RaceInfo.id.Nichiji & _
                   " Ｒ:" & RaceInfo.id.RaceNum & _
                   " レース名:" & RaceInfo.RaceInfo.Ryakusyo10 & vbCrLf)

' レース詳細以外は読み飛ばし
If Mid(strBuff, 1, 2) <> "RA" Then
    Call AxJVLink1.JVSkip()
End If
```

### 学習ポイント
- コード変換の仕組み
- CSVファイルの読み込み
- JVSkipの使用方法
- データの可読性向上

---

## Lesson-6: データベース連携

### 目的
取得したデータをデータベースに保存する機能を実装します。

### 実装内容
- **ADO.NET**: データベースアクセス
- **Access データベース**: `JVData.accdb`の使用
- **データ保存**: 取得データの永続化
- **basADOUtility**: データベース操作ユーティリティ

### 主要ファイル
- `JVData.accdb`: Accessデータベースファイル
- `basADOUtility.vb`: データベース操作ユーティリティ

### 学習ポイント
- ADO.NETの使用方法
- Accessデータベースの操作
- データの永続化
- データベース設計の基本

---

## Lesson-7: 複数データ種別対応とPython連携

### 目的
レースデータ以外のデータ種別（調教データなど）にも対応し、Pythonとの連携機能を実装します。

### 実装内容
- **複数データ種別**: レースデータ、調教データ（HC、WC）の対応
- **日付範囲指定**: ユーザーが指定した期間のデータ取得
- **Python連携**: CSV出力とPython設定ファイル作成
- **統合データ構造**: レースデータと調教データの統合

### 主要コード
```vb
' 日付範囲指定
strFromTime = dtpFromDate.Value.ToString("yyyyMMdd000000")

' データ構造（統合版）
Public Class RaceData
    ' レースデータ用フィールド
    Public Year As String = ""
    Public MonthDay As String = ""
    Public JyoCD As String = ""
    Public JyoName As String = ""
    Public RaceNum As String = ""
    
    ' 調教データ用フィールド
    Public ChokyoDate As String = ""
    Public ChokyoType As String = ""    ' HC(坂路) or WC(ウッド)
    Public KettoNum As String = ""
    Public HaronTime4 As String = ""    ' 4ハロンタイム
    Public HaronTime3 As String = ""    ' 3ハロンタイム
End Class

' CSV出力
Private Sub ExportDataToCsv()
    Dim filePath As String = Path.Combine(Application.StartupPath, "race_data.csv")
    Using writer As New StreamWriter(filePath, False, Encoding.UTF8)
        writer.WriteLine("年,月日,競馬場コード,競馬場名,回次,日次,レース番号,レース名")
        For Each raceData As RaceData In raceDataList
            writer.WriteLine(String.Format("{0},{1},{2},""{3}"",{4},{5},{6},""{7}""", _
                raceData.Year, raceData.MonthDay, raceData.JyoCD, raceData.JyoName, _
                raceData.Kaiji, raceData.Nichiji, raceData.RaceNum, raceData.RaceName))
        Next
    End Using
End Sub
```

### 学習ポイント
- 複数データ種別の処理
- 日付範囲指定の実装
- CSVファイル出力
- Python連携の設計
- 統合データ構造の設計

---

## 開発の流れ

### 1. 環境構築
1. Visual Studio 2019のインストール
2. JRA-VAN Data Lab. SDKのインストール
3. 32bitプロジェクトの作成
4. JV-Link ActiveXコントロールの参照追加

### 2. 段階的開発
1. **Lesson-1**: 基本的な設定画面
2. **Lesson-2**: データ取得の基本
3. **Lesson-3**: データ読み込みと表示
4. **Lesson-4**: 進捗表示の改善
5. **Lesson-5**: コード変換機能
6. **Lesson-6**: データベース連携
7. **Lesson-7**: 高度な機能とPython連携

### 3. テストとデバッグ
- 各Lesson完了後に動作確認
- エラーハンドリングの確認
- データ取得の正確性確認

## 注意事項

### 技術的要件
- **32bit環境**: JV-Linkは32bit環境でのみ動作
- **ライセンス**: JRA-VAN Data Labの有効なライセンスが必要
- **ネットワーク**: インターネット接続が必要

### 開発時の注意点
- エラーハンドリングの徹底
- メモリ管理の適切な実装
- UI応答性の維持
- データの整合性確認

### 運用時の注意点
- データ取得頻度の制限
- ディスク容量の管理
- ログファイルの管理
- セキュリティの確保

## 参考資料

- JRA-VAN Data Lab. SDK ドキュメント
- VB.NET開発ガイド
- JV-Link API リファレンス
- データ構造体定義

---

*このドキュメントは、JRA-VAN Data Labを使用したVB.NETアプリケーション開発の学習手順をまとめたものです。各Lessonは段階的に機能を追加する形で設計されており、順番に学習することで、JV-Linkの使用方法を理解できます。* 

実行ファイルは以下の場所にあります：

**`C:\my_project_folder\envs\cursor\my_keiba\Lesson-7-Fixed\WindowsApplication1\bin\x86\Debug\WindowsApplication1.exe`**

PowerShellでの実行に問題があるので、Windowsエクスプローラーで直接実行してみてください：

1. **Windowsエクスプローラーを開く**
2. **以下のパスに移動：**
   ```
   C:\my_project_folder\envs\cursor\my_keiba\Lesson-7-Fixed\WindowsApplication1\bin\x86\Debug\
   ```
3. **`WindowsApplication1.exe` をダブルクリック**

または、コマンドプロンプト（cmd.exe）で実行することもできます：

1. **コマンドプロンプトを開く**
2. **以下のコマンドを実行：**
   ```cmd
   cd "C:\my_project_folder\envs\cursor\my_keiba\Lesson-7-Fixed\WindowsApplication1\bin\x86\Debug"
   WindowsApplication1.exe
   ```

PowerShell 7では実行ポリシーの問題がある可能性がありますが、コマンドプロンプトや直接ダブルクリックでは動作するはずです。 