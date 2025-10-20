#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EveryDB2.3 Update Issue Fix Script (English Version)
Fix the problem where updates stop in the middle
"""

import os
import sqlite3
import shutil
from datetime import datetime
import glob

def fix_everydb_english():
    """Fix EveryDB2.3 update issues"""
    
    print("=== EveryDB2.3 Update Issue Fix ===")
    print("Fixing the problem where updates stop in the middle")
    print()
    
    # 1. Check current status
    print("1. Current Status Check")
    print("=" * 60)
    
    # Check database files
    db_files = ["ecore.db", "ecore_backup.db"]
    for db_file in db_files:
        if os.path.exists(db_file):
            print(f"OK {db_file} exists")
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM N_UMA;")
                horse_count = cursor.fetchone()[0]
                print(f"   Horse count: {horse_count:,}")
                conn.close()
            except Exception as e:
                print(f"   Error: {e}")
        else:
            print(f"NG {db_file} not found")
    
    # 2. Database integrity check
    print(f"\n2. Database Integrity Check")
    print("=" * 60)
    
    for db_file in db_files:
        if os.path.exists(db_file):
            print(f"\n--- {db_file} ---")
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                # Integrity check
                cursor.execute("PRAGMA integrity_check;")
                result = cursor.fetchone()[0]
                
                if result == "ok":
                    print("OK Integrity check: OK")
                else:
                    print(f"NG Integrity check: {result}")
                
                # Table count
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table';")
                table_count = cursor.fetchone()[0]
                print(f"Table count: {table_count}")
                
                conn.close()
                
            except Exception as e:
                print(f"NG Database error: {e}")
    
    # 3. Create backup
    print(f"\n3. Create Backup")
    print("=" * 60)
    
    backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    print(f"Backup directory: {backup_dir}")
    
    for db_file in db_files:
        if os.path.exists(db_file):
            backup_file = os.path.join(backup_dir, db_file)
            shutil.copy2(db_file, backup_file)
            print(f"OK {db_file} -> {backup_file}")
    
    # 4. Clean up temporary files
    print(f"\n4. Clean Up Temporary Files")
    print("=" * 60)
    
    # Temporary file patterns
    temp_patterns = [
        "*.tmp",
        "*.temp",
        "*.log",
        "*.lock",
        "*.db-journal",
        "*.db-wal",
        "*.db-shm"
    ]
    
    cleaned_files = 0
    for pattern in temp_patterns:
        for temp_file in glob.glob(pattern):
            try:
                os.remove(temp_file)
                print(f"Deleted: {temp_file}")
                cleaned_files += 1
            except Exception as e:
                print(f"Delete failed: {temp_file} - {e}")
    
    print(f"Cleanup completed: {cleaned_files} files")
    
    # 5. Recommended update procedure
    print(f"\n5. Recommended Update Procedure")
    print("=" * 60)
    
    print("Solution for EveryDB2.3 update stopping in the middle:")
    print()
    print("1. Manual Update Mode")
    print("   - Select manual update instead of automatic update")
    print("   - Update data types one by one")
    print()
    print("2. Split Update Period")
    print("   - 2017-2020")
    print("   - 2021-2023") 
    print("   - 2024-present")
    print()
    print("3. Individual Data Type Updates")
    print("   - Race information (RACE) only")
    print("   - Horse information (UMA) only")
    print("   - Jockey information (KISYU) only")
    print()
    print("4. Ensure System Resources")
    print("   - Free up memory space")
    print("   - Free up disk space")
    print("   - Close other applications")
    
    # 6. Recommended execution steps
    print(f"\n6. Recommended Execution Steps")
    print("=" * 60)
    
    print("1. Run EveryDB2.3 with administrator privileges")
    print("2. Check database path in connection settings")
    print("3. Select 'Manual Update' in update settings")
    print("4. Limit data type to 'Race Information (RACE)' only")
    print("5. Set short update period (e.g., 2024 only)")
    print("6. Click 'Start Acquisition' button")
    print("7. If error occurs, split period even shorter")
    
    # 7. Provide monitoring script
    print(f"\n7. Provide Monitoring Script")
    print("=" * 60)
    
    monitor_script = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EveryDB2.3 Monitoring Script
"""
import time
import os
import sqlite3

def monitor_everydb():
    db_file = "ecore.db"
    last_size = 0
    
    while True:
        if os.path.exists(db_file):
            current_size = os.path.getsize(db_file)
            if current_size != last_size:
                print(f"{time.strftime('%H:%M:%S')} - Database updating: {current_size:,} bytes")
                last_size = current_size
            else:
                print(f"{time.strftime('%H:%M:%S')} - Waiting...")
        else:
            print(f"{time.strftime('%H:%M:%S')} - Database file not found")
        
        time.sleep(10)  # Monitor every 10 seconds

if __name__ == "__main__":
    monitor_everydb()
'''
    
    with open("monitor_everydb_english.py", "w", encoding="utf-8") as f:
        f.write(monitor_script)
    
    print("OK Monitoring script created: monitor_everydb_english.py")
    print("Usage: python monitor_everydb_english.py")
    
    # 8. Final confirmation
    print(f"\n8. Preparation Complete")
    print("=" * 60)
    
    print("The following preparations are complete:")
    print("1. Database integrity check")
    print("2. Backup creation")
    print("3. Temporary file cleanup")
    print("4. Monitoring script provision")
    print()
    print("Next, run manual update in EveryDB2.3.")

if __name__ == "__main__":
    fix_everydb_english()


