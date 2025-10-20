# データベース構造ガイド

## 重要なポイント

### 日付系カラムの使い分け

**MakeDate**
- そのレコードが登録（更新）された日付
- レポート用や最新データ判定に使用
- 形式: "YYYYMMDD" (例: "20251016")

**Year + MonthDay**
- レース開催日自体
- MonthDay は "MMDD" 形式
- RaceDate = Year || MonthDay で作成すると扱いやすい
- スクリプトでは datetime に変換して比較する

### 賞金カラムの処理

**Honsyokin (本賞金)**
- 単勝払戻ではなく、上位馬にもらえる賞金額
- 1/100 単位（例: 00006800 → 68.00万円）
- 分析時は `CAST(Honsyokin AS INTEGER)/100.0` で処理

**Fukasyokin (複賞金)**
- 着外でも分配される賞金
- 1/100 単位（例: 00006800 → 68.00万円）
- 分析時は `CAST(Fukasyokin AS INTEGER)/100.0` で処理

## スクリプトでの使い方

### 日付フィルタリング
```sql
-- レース開催日でフィルタリング
WHERE Year || MonthDay = '20251012'

-- 複数日
WHERE Year || MonthDay IN ('20251012', '20251013')

-- 期間指定
WHERE Year || MonthDay BETWEEN '20251001' AND '20251031'
```

### 賞金の計算
```sql
-- 万円単位で取得
SELECT 
    CAST(Honsyokin AS INTEGER)/100.0 as WinReward_Man,
    CAST(Fukasyokin AS INTEGER)/100.0 as PlaceReward_Man
FROM N_UMA_RACE
```

## CURSORエージェントへの指示

### 明確な指示例
- 「Year と MonthDay を連結して日付にする」
- 「賞金は 100 で割って万円にする」
- 「MakeDate は更新日、Year+MonthDay が開催日」

### 混乱を避けるためのメモ
- MakeDate: 更新日
- Year+MonthDay: 開催日
- 賞金: 万円換算
- スクリプトではこの順で処理する

## 修正が必要な箇所

1. **予想結果分析スクリプト**
   - 日付の扱いを統一
   - 賞金の単位を正しく処理

2. **ROI計算**
   - 配当金の正しい計算
   - 投資金額との比較

3. **データ突合**
   - 日付形式の統一
   - カラム名の確認


