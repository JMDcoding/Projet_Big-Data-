# MinIO Integration - Data Lake Object Storage

## Overview

MinIO is an S3-compatible object storage system integrated into this Big Data pipeline. All data from APIs is now stored in:
- **Local File System** (JSON/CSV for backup)
- **MinIO Object Storage** (primary data lake)
- **PostgreSQL Database** (indexing & queries)

## Setup

### 1. Download MinIO

Download `minio.exe` from: https://min.io/download

Place it in the project root directory:
```
c:\Users\Barraud\OneDrive - Emineo Education\Cours\BigData & IA\B2\TP - Projet\Projet_Big-Data-\minio.exe
```

### 2. Create Data Directory

MinIO requires a directory to store data:
```powershell
mkdir data\minio
```

### 3. Start MinIO Server

**Option A: Using the batch script**
```powershell
# Windows
.\start_minio.bat
```

**Option B: Manual command**
```powershell
.\minio.exe server data\minio
```

### 4. Verify MinIO is Running

MinIO server output should show:
```
API: http://127.0.0.1:9000
RootUser: minioadmin
RootPass: minioadmin

Browser Access:
   http://127.0.0.1:9000
```

## Architecture

### Data Flow

```
API Data
   ↓
LocalDemoData/BlitzortungAPI/OpenSkyAPI
   ↓
Transformation (Pandas DataFrame)
   ↓
┌─────────────────────────────────┐
├─ Local File System (backup)     ├─ CSV/JSON files in ./data/raw/
├─ MinIO Object Storage (primary) ├─ lightning-data bucket
└─ PostgreSQL Database            ┴─ lightning_strikes table
```

### Updated Pipeline

The `main.py` now saves data to 3 locations:

```python
# In main.py DataPipeline.run_storage():
1. JSON Lake (local): data/raw/*.json
2. CSV Lake (local):  data/raw/*.csv
3. MinIO Lake:        lightning-data/lightning/*.json
```

## Usage

### Running the Pipeline

```powershell
# Terminal 1: Start MinIO
.\start_minio.bat

# Terminal 2: Run the data pipeline
python main.py
```

This will:
1. ✅ Fetch 50 lightning strikes from LocalDemoData
2. ✅ Fetch 3000+ flights from OpenSkyAPI
3. ✅ Transform & normalize data
4. ✅ Save to all 3 storage backends:
   - Local filesystem (CSV + JSON)
   - MinIO object storage (JSON)
   - PostgreSQL database (indexed records)

### Verify MinIO Storage

Access MinIO Browser UI:
```
http://localhost:9000
```

Login with:
- Username: `minioadmin`
- Password: `minioadmin`

You'll see the `lightning-data` bucket containing:
```
lightning-data/
├── lightning/
│   ├── lightning_processed_2026-04-01T15-30-45.json
│   ├── lightning_data_2026-04-01T15-30-45.csv
│   └── (more files...)
└── flights/
    ├── flights_processed_2026-04-01T15-30-50.json
    └── (more files...)
```

## Configuration

MinIO connection settings are hardcoded in `main.py`:

```python
self.minio_lake = MinIODataLake(
    minio_host="localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    bucket_name="lightning-data"
)
```

To change settings, edit the `DataPipeline.__init__()` method in `main.py`.

## Bucket Information

The pipeline logs bucket statistics after each save:

```
MinIO Bucket: 150 objects, 45.23 MB
```

This shows:
- Total number of objects stored
- Total storage size in MB

## Class Reference

### MinIODataLake

Location: `src/storage/data_lake.py`

**Methods:**

```python
# Create instance
minio = MinIODataLake(
    minio_host="localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    bucket_name="lightning-data"
)

# Save data
minio.save(data_dict, "lightning/data_2026-04-01.json")
# Returns: "lightning-data/lightning/data_2026-04-01.json"

# Load data
data = minio.load("lightning/data_2026-04-01.json")

# List files
files = minio.list_files()

# Delete file
minio.delete("lightning/data_2026-04-01.json")

# Get bucket stats
info = minio.get_bucket_info()
# Returns: {'object_count': 150, 'total_size_mb': 45.23, ...}
```

## Troubleshooting

### Issue: "minio: command not found"

**Solution:** Add minio.exe to your PATH or use the full path:
```powershell
C:\path\to\minio.exe server data\minio
```

### Issue: "connection refused" on port 9000

**Solution:** MinIO is not running. Start it with:
```powershell
.\start_minio.bat
```

### Issue: "Permission denied" on data/minio

**Solution:** Ensure you have write permissions to the data directory:
```powershell
# Run PowerShell as Administrator
icacls "data\minio" /grant:r "%USERNAME%:F"
```

### Issue: "Bucket already exists"

This is normal. MinIO will reuse the existing bucket. No action needed.

## Performance Tips

1. **Use MinIO for archival**: Large historical datasets
2. **Use PostgreSQL for queries**: Real-time analytics
3. **Use local filesystem for backups**: Disaster recovery

## Next Steps

1. Integrate with Apache Spark for distributed processing
2. Add data retention policies (30 days for raw, 1 year for aggregates)
3. Implement versioning for data lineage
4. Add Prometheus metrics for monitoring

## References

- MinIO Docs: https://docs.min.io
- S3 Compatibility: https://docs.min.io/minio/baremetal/s3-select/
- Python SDK: https://github.com/minio/minio-py
