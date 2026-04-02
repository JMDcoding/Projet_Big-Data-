from pathlib import Path

print(f"Current dir: {Path.cwd()}")

minio_path = Path("data/minio")
print(f"\nRel path: {minio_path}")
print(f"Rel path exists: {minio_path.exists()}")

abs_path = Path.cwd() / "data" / "minio"
print(f"\nAbs path: {abs_path}")
print(f"Abs path exists: {abs_path.exists()}")

# List files
if abs_path.exists():
    all_files = list(abs_path.rglob("*"))
    print(f"\nAll files in path: {len(all_files)}")
    
    json_files = [f for f in all_files if f.suffix.lower() == ".json" and ".minio.sys" not in str(f)]
    csv_files = [f for f in all_files if f.suffix.lower() == ".csv" and ".minio.sys" not in str(f)]
    
    print(f"JSON files (no .minio.sys): {len(json_files)}")
    print(f"CSV files (no .minio.sys): {len(csv_files)}")
    
    if json_files:
        print(f"\nFirst JSON: {json_files[0]}")
else:
    print("Path does not exist!")

