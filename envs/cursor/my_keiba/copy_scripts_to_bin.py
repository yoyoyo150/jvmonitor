import sys
import shutil
from pathlib import Path

# 文字化け対策
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# ソースとターゲットパス
source = Path("JVMonitor/JVMonitor/import_excel_marks_wrapper.py")
target_dir = Path("JVMonitor/JVMonitor/bin/Debug/net6.0-windows/")
target = target_dir / "import_excel_marks_wrapper.py"

print(f"ソース: {source.absolute()}")
print(f"ターゲット: {target.absolute()}")

if source.exists():
    shutil.copy2(source, target)
    print("OK コピー完了")
else:
    print("NG ソースファイルが見つかりません")

# fix_excel_data_import.pyもコピー
source2 = Path("fix_excel_data_import.py")
target2 = target_dir / "fix_excel_data_import.py"

print(f"ソース2: {source2.absolute()}")
print(f"ターゲット2: {target2.absolute()}")

if source2.exists():
    shutil.copy2(source2, target2)
    print("OK コピー完了（fix_excel_data_import.py）")
else:
    print("NG ソースファイルが見つかりません（fix_excel_data_import.py）")

