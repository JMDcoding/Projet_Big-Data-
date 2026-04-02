#!/usr/bin/env python3
"""
Clean local data directory completely.
All data must come from MinIO data lake, not from local storage.

IMPORTANT: This permanently deletes the local data/ folder.
"""
import sys
import shutil
from pathlib import Path

print("\n" + "="*70)
print("LOCAL DATA CLEANUP - FORCE MinIO ONLY")
print("="*70)

data_dir = Path("data")

if not data_dir.exists():
    print(f"\n[OK] No data/ directory found - already clean")
    sys.exit(0)

print(f"\n[WARNING] This will DELETE the entire {data_dir} directory!")
print("[WARNING] All data must come from MinIO data lake instead")
print("\nTo proceed, type 'DELETE' (case-sensitive):")

response = input("> ").strip()

if response != "DELETE":
    print("\n[CANCELLED] Cleanup aborted")
    sys.exit(1)

print("\n[*] Deleting data/ directory and all contents...")

try:
    shutil.rmtree(data_dir)
    print(f"[OK] {data_dir} deleted successfully")
    
    # Recreate empty directory structure for reference (with .gitkeep)
    data_dir.mkdir(exist_ok=True)
    raw_dir = data_dir / "raw"
    processed_dir = data_dir / "processed"
    
    raw_dir.mkdir(exist_ok=True)
    processed_dir.mkdir(exist_ok=True)
    
    # Add .gitkeep to keep directory in git
    (raw_dir / ".gitkeep").touch()
    (processed_dir / ".gitkeep").touch()
    
    print(f"[OK] Recreated {data_dir}/ with .gitkeep files")
    
    print("\n[OK] Cleanup complete!")
    print("\nData storage configuration:")
    print("  1. MinIO (localhost:9000) - PRIMARY data lake")
    print("  2. PostgreSQL (localhost:5433) - Indexed database")
    print("  3. Local data/ folder - TEMPORARY STAGING ONLY (no persistence)")
    print("\nAll data flows:")
    print("  API → MinIO → PostgreSQL")
    print("  (No data remains in local data/ folder after processing)")
    
except Exception as e:
    print(f"\n[ERROR] Cleanup failed: {str(e)}")
    sys.exit(1)
