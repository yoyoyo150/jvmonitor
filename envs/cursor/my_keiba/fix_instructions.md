# JVMonitor「ないない」問題の解決手順

## 問題の原因
- データは実際に存在している
- データベースのインデックスが不足している
- JVMonitorのキャッシュが古い

## 解決手順

### 1. JVMonitorを閉じる
- JVMonitorアプリケーションを完全に終了する

### 2. データベース最適化を実行
```bash
python simple_fix.py
```

### 3. JVMonitorを再起動
- JVMonitorを再度起動する

### 4. 確認
- データが正しく表示されることを確認

## 代替案（JVMonitorを閉じたくない場合）

### 手動でデータベース最適化
```sql
-- SQLiteで直接実行
CREATE INDEX IF NOT EXISTS idx_source_date ON HORSE_MARKS(SourceDate);
CREATE INDEX IF NOT EXISTS idx_horse_name ON HORSE_MARKS(HorseName);
VACUUM;
ANALYZE;
```

### または、JVMonitorの「更新」ボタンをクリック
- 上部の「更新」ボタンをクリックしてデータを再読み込み

## 根本的な解決策

### 1. データベースインデックスの追加
- SourceDateカラムにインデックスを追加
- HorseNameカラムにインデックスを追加

### 2. クエリの最適化
- 複数の検索パターンを使用
- LIKE検索の最適化

### 3. キャッシュのクリア
- JVMonitorのキャッシュをクリア
- アプリケーション再起動

## 確認方法

### データが存在することを確認
```python
import sqlite3
conn = sqlite3.connect('excel_data.db')
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM HORSE_MARKS WHERE SourceDate = '20251013'")
count = cursor.fetchone()[0]
print(f"10/13のデータ: {count}件")
conn.close()
```

## 注意事項
- データベース最適化中はJVMonitorを閉じる必要がある
- 最適化には数分かかる場合がある
- 最適化後は検索速度が向上する








