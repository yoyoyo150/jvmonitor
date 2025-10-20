# -*- coding: utf-8 -*-
import sqlite3
import sys
import io

# UTF-8エンコーディング設定
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def check_difn_data():
    """DIFNデータの確認"""
    conn = sqlite3.connect('ecore.db')
    cursor = conn.cursor()
    
    print("=== DIFNデータの確認 ===\n")
    
    # 1. DIFNテーブルの存在確認
    print("1. DIFNテーブルの存在確認")
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name LIKE '%DIFN%'
    """)
    difn_tables = cursor.fetchall()
    
    print(f"DIFN関連テーブル: {len(difn_tables)} 個")
    for table in difn_tables:
        print(f"  - {table[0]}")
    
    # 2. DIFNテーブルの内容確認
    if difn_tables:
        print("\n2. DIFNテーブルの内容確認")
        for table in difn_tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  {table_name}: {count:,} 件")
            
            # テーブル構造を確認
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print(f"    カラム数: {len(columns)}")
            
            # サンプルデータを表示
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                samples = cursor.fetchall()
                print(f"    サンプルデータ:")
                for i, sample in enumerate(samples, 1):
                    print(f"      {i}: {sample[:5]}...")  # 最初の5カラムのみ表示
    
    # 3. プラダリアのデータをDIFNテーブルで検索
    print("\n3. プラダリアのデータをDIFNテーブルで検索")
    for table in difn_tables:
        table_name = table[0]
        try:
            # テーブル構造を確認して、馬名カラムを探す
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            # 馬名らしきカラムを探す
            bamei_columns = [col[1] for col in columns if 'bamei' in col[1].lower() or '馬名' in col[1]]
            
            if bamei_columns:
                bamei_col = bamei_columns[0]
                cursor.execute(f"""
                    SELECT COUNT(*) FROM {table_name} 
                    WHERE {bamei_col} = 'プラダリア'
                """)
                pradaria_count = cursor.fetchone()[0]
                print(f"  {table_name} のプラダリアデータ: {pradaria_count} 件")
                
                if pradaria_count > 0:
                    cursor.execute(f"""
                        SELECT * FROM {table_name} 
                        WHERE {bamei_col} = 'プラダリア'
                        LIMIT 3
                    """)
                    samples = cursor.fetchall()
                    print(f"    サンプル:")
                    for i, sample in enumerate(samples, 1):
                        print(f"      {i}: {sample}")
        except Exception as e:
            print(f"  {table_name}: 検索エラー - {e}")
    
    # 4. 2023年のデータ確認
    print("\n4. 2023年のデータ確認")
    for table in difn_tables:
        table_name = table[0]
        try:
            # 年カラムを探す
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            year_columns = [col[1] for col in columns if 'year' in col[1].lower() or '年' in col[1]]
            
            if year_columns:
                year_col = year_columns[0]
                cursor.execute(f"""
                    SELECT COUNT(*) FROM {table_name} 
                    WHERE {year_col} = '2023'
                """)
                count_2023 = cursor.fetchone()[0]
                print(f"  {table_name} の2023年データ: {count_2023:,} 件")
        except Exception as e:
            print(f"  {table_name}: 2023年データ確認エラー - {e}")
    
    conn.close()

def check_uma_race_alternatives():
    """N_UMA_RACEの代替テーブルを確認"""
    print("\n=== N_UMA_RACEの代替テーブル確認 ===\n")
    
    conn = sqlite3.connect('ecore.db')
    cursor = conn.cursor()
    
    # 1. 出馬関連テーブルを検索
    print("1. 出馬関連テーブルを検索")
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND (
            name LIKE '%UMA%' OR 
            name LIKE '%RACE%' OR
            name LIKE '%出馬%' OR
            name LIKE '%馬%'
        )
        ORDER BY name
    """)
    uma_tables = cursor.fetchall()
    
    print("出馬関連テーブル:")
    for table in uma_tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"  {table_name}: {count:,} 件")
    
    # 2. プラダリアのデータを各テーブルで検索
    print("\n2. プラダリアのデータを各テーブルで検索")
    for table in uma_tables:
        table_name = table[0]
        try:
            # テーブル構造を確認
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            # 馬名らしきカラムを探す
            bamei_columns = [col[1] for col in columns if 'bamei' in col[1].lower() or '馬名' in col[1] or 'Bamei' in col[1]]
            
            if bamei_columns:
                bamei_col = bamei_columns[0]
                cursor.execute(f"""
                    SELECT COUNT(*) FROM {table_name} 
                    WHERE {bamei_col} = 'プラダリア'
                """)
                pradaria_count = cursor.fetchone()[0]
                if pradaria_count > 0:
                    print(f"  ✅ {table_name}: プラダリアデータ {pradaria_count} 件")
                    
                    # 2023年のデータを確認
                    year_columns = [col[1] for col in columns if 'year' in col[1].lower() or '年' in col[1] or 'Year' in col[1]]
                    if year_columns:
                        year_col = year_columns[0]
                        cursor.execute(f"""
                            SELECT COUNT(*) FROM {table_name} 
                            WHERE {bamei_col} = 'プラダリア' AND {year_col} = '2023'
                        """)
                        count_2023 = cursor.fetchone()[0]
                        print(f"    2023年データ: {count_2023} 件")
        except Exception as e:
            print(f"  ❌ {table_name}: 検索エラー - {e}")
    
    conn.close()

def create_difn_download_guide():
    """DIFNデータダウンロードガイドの作成"""
    print("\n=== DIFNデータダウンロードガイドの作成 ===\n")
    
    guide_content = '''# DIFNデータダウンロードガイド

## 問題の状況
- N_UMA_RACEが直接選択できない
- DIFNに含まれている可能性
- 期間設定で開始日しか選べない

## 解決方法

### 1. EveryDB2.3での設定
1. **蓄積系** > **通常** を選択
2. **DIFN** を選択（蓄積系ソフト用蓄積情報）
3. **開始日**: 2023/01/01 を設定
4. **ダウンロード開始**

### 2. データ種別の確認
- DIFN: 蓄積系ソフト用蓄積情報
- 出馬データが含まれている可能性

### 3. 期間設定の制限
- 開始日のみ設定可能
- 終了日は自動的に最新日まで

### 4. データ確認方法
```python
python check_difn_data.py
```

## 注意点
- DIFNデータには出馬情報が含まれている可能性
- 期間設定の制限により、全期間のデータが取得される
- データサイズが大きくなる可能性
'''
    
    with open('DIFN_download_guide.md', 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print("[OK] DIFN_download_guide.md を作成しました")

if __name__ == "__main__":
    check_difn_data()
    check_uma_race_alternatives()
    create_difn_download_guide()


