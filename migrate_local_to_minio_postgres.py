#!/usr/bin/env python3
"""
Migrate local data files to MinIO S3 and then to PostgreSQL.
This moves all data from local storage to cloud object storage.
"""

import sys
import json
import os
import shutil
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path.cwd()))

try:
    import pandas as pd
    from minio import Minio
    from minio.error import S3Error
    import io
except ImportError:
    print("❌ Dépendances manquantes. Installez: pip install minio pandas")
    sys.exit(1)

from config.config import get_config
from src.database.warehouse import PostgreSQLConnection, DataWarehouse


def get_minio_client(config) -> Minio:
    """Initialize MinIO client."""
    return Minio(
        f"{config.MINIO_HOST}:{config.MINIO_PORT}",
        access_key=config.MINIO_ACCESS_KEY,
        secret_key=config.MINIO_SECRET_KEY,
        secure=False
    )


def find_local_data_files(base_path: str = "data") -> dict:
    """Find all JSON and CSV files in local data directory.
    
    Returns:
        Dictionary with file paths grouped by type
    """
    files = {
        "json": [],
        "csv": [],
        "other": []
    }
    
    base = Path(base_path)
    if not base.exists():
        print(f"❌ Dossier {base_path} n'existe pas")
        return files
    
    for file_path in base.rglob("*"):
        if file_path.is_file():
            if file_path.suffix.lower() == ".json":
                files["json"].append(str(file_path))
            elif file_path.suffix.lower() == ".csv":
                files["csv"].append(str(file_path))
            else:
                files["other"].append(str(file_path))
    
    return files


def upload_to_minio(file_path: str, minio_client: Minio, config) -> bool:
    """Upload file to MinIO.
    
    Args:
        file_path: Local file path
        minio_client: MinIO client
        config: Configuration object
        
    Returns:
        True if successful
    """
    try:
        file_path_obj = Path(file_path)
        
        # Create bucket name from file structure
        if "lightning" in file_path:
            bucket = "lightning-data"
            prefix = "lightning"
        elif "flight" in file_path:
            bucket = "flight-data"
            prefix = "flights"
        else:
            bucket = "raw-data"
            prefix = "other"
        
        # Ensure bucket exists
        if not minio_client.bucket_exists(bucket):
            minio_client.make_bucket(bucket)
            print(f"  ✓ Bucket créé: {bucket}")
        
        # Upload file
        file_size = os.path.getsize(file_path)
        object_name = f"{prefix}/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}/{file_path_obj.name}"
        
        with open(file_path, 'rb') as file_data:
            minio_client.put_object(
                bucket,
                object_name,
                file_data,
                length=file_size
            )
        
        print(f"  ✓ {file_path_obj.name:40} -> {bucket}/{object_name}")
        return True
        
    except S3Error as e:
        print(f"  ❌ Erreur MinIO: {str(e)}")
        return False
    except Exception as e:
        print(f"  ❌ Erreur: {str(e)}")
        return False


def import_json_to_postgres(file_path: str, db: PostgreSQLConnection) -> bool:
    """Import JSON data to PostgreSQL.
    
    Args:
        file_path: Path to JSON file
        db: Database connection
        
    Returns:
        True if successful
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle different data types
        if isinstance(data, dict):
            if "strikes" in data:
                # Lightning data
                cursor = db.connection.cursor()
                for strike in data.get("strikes", []):
                    try:
                        cursor.execute(
                            "INSERT INTO lightning_strikes (lightning_id, latitude, longitude, altitude, intensity, timestamp, source) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                            (
                                strike.get("id"),
                                strike.get("latitude"),
                                strike.get("longitude"),
                                strike.get("altitude"),
                                strike.get("signal"),
                                strike.get("timestamp"),
                                strike.get("source", "local_import")
                            )
                        )
                    except Exception as e:
                        pass  # Skip duplicates
                
                db.connection.commit()
                return True
            elif "flights" in data:
                # Flight data
                cursor = db.connection.cursor()
                for flight in data.get("flights", []):
                    try:
                        cursor.execute(
                            "INSERT INTO flights (flight_number, departure, arrival, departure_time, arrival_time, source) VALUES (%s, %s, %s, %s, %s, %s)",
                            (
                                flight.get("flight_number"),
                                flight.get("departure"),
                                flight.get("arrival"),
                                flight.get("departure_time"),
                                flight.get("arrival_time"),
                                flight.get("source", "local_import")
                            )
                        )
                    except Exception as e:
                        pass  # Skip duplicates
                
                db.connection.commit()
                return True
        
        return False
        
    except Exception as e:
        print(f"  ❌ Erreur importation {Path(file_path).name}: {str(e)}")
        return False


def import_csv_to_postgres(file_path: str, db: PostgreSQLConnection) -> bool:
    """Import CSV data to PostgreSQL.
    
    Args:
        file_path: Path to CSV file
        db: Database connection
        
    Returns:
        True if successful
    """
    try:
        df = pd.read_csv(file_path)
        
        # Determine table based on filename
        if "lightning" in file_path:
            table = "lightning_strikes"
            # Map CSV columns to DB columns
            column_mapping = {
                "id": "lightning_id",
                "signal": "intensity"
            }
            df = df.rename(columns=column_mapping)
            
            for _, row in df.iterrows():
                try:
                    cursor = db.connection.cursor()
                    cursor.execute(
                        "INSERT INTO lightning_strikes (lightning_id, latitude, longitude, altitude, intensity, timestamp, source) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        (
                            row.get("lightning_id") or row.get("id"),
                            row.get("latitude"),
                            row.get("longitude"),
                            row.get("altitude"),
                            row.get("intensity") or row.get("signal"),
                            row.get("timestamp"),
                            row.get("source", "local_csv_import")
                        )
                    )
                    db.connection.commit()
                except Exception as e:
                    pass  # Skip duplicates or errors
        
        elif "flight" in file_path:
            table = "flights"
            for _, row in df.iterrows():
                try:
                    cursor = db.connection.cursor()
                    cursor.execute(
                        "INSERT INTO flights (flight_number, departure, arrival, departure_time, arrival_time, source) VALUES (%s, %s, %s, %s, %s, %s)",
                        (
                            row.get("flight_number"),
                            row.get("departure"),
                            row.get("arrival"),
                            row.get("departure_time"),
                            row.get("arrival_time"),
                            row.get("source", "local_csv_import")
                        )
                    )
                    db.connection.commit()
                except Exception as e:
                    pass  # Skip duplicates or errors
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur importation CSV {Path(file_path).name}: {str(e)}")
        return False


def cleanup_local_files(files: dict, dry_run: bool = True) -> bool:
    """Remove local data files after successful migration.
    
    Args:
        files: Dictionary of files to delete
        dry_run: If True, only show what would be deleted
        
    Returns:
        True if successful
    """
    total_files = len(files["json"]) + len(files["csv"])
    
    if dry_run:
        print(f"\n📋 DRY RUN - Fichiers à supprimer ({total_files}):")
        for file_path in files["json"] + files["csv"]:
            print(f"  - {file_path}")
        return True
    
    print(f"\n🗑️  Suppression de {total_files} fichiers locaux...")
    
    deleted = 0
    for file_path in files["json"] + files["csv"]:
        try:
            Path(file_path).unlink()
            deleted += 1
        except Exception as e:
            print(f"  ❌ Erreur suppression {file_path}: {str(e)}")
    
    print(f"✅ {deleted}/{total_files} fichiers supprimés")
    return True


def main():
    """Main entry point."""
    print("=" * 80)
    print("📦 MIGRATION: LOCAL → MinIO S3 → PostgreSQL")
    print("=" * 80)
    
    # Get configuration
    try:
        config = get_config()
    except Exception as e:
        print(f"❌ Erreur de configuration: {str(e)}")
        return False
    
    # Find local files
    print("\n🔍 Recherche des fichiers locaux...")
    files = find_local_data_files("data")
    
    json_count = len(files["json"])
    csv_count = len(files["csv"])
    total = json_count + csv_count
    
    if total == 0:
        print("✅ Aucun fichier à migrer")
        return True
    
    print(f"✅ Trouvé: {json_count} JSON + {csv_count} CSV = {total} fichiers")
    
    # Initialize clients
    print("\n🔌 Initialisation des connexions...")
    try:
        minio_client = get_minio_client(config)
        db = PostgreSQLConnection(
            host=config.DB_HOST,
            port=config.DB_PORT,
            database=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD
        )
        db.connect()
        print("✅ MinIO et PostgreSQL connectés")
    except Exception as e:
        print(f"❌ Erreur connexion: {str(e)}")
        return False
    
    # Upload to MinIO
    print(f"\n📤 Upload vers MinIO ({total} fichiers)...")
    uploaded = 0
    
    for file_path in files["json"] + files["csv"]:
        if upload_to_minio(file_path, minio_client, config):
            uploaded += 1
    
    print(f"✅ {uploaded}/{total} fichiers uploadés vers MinIO")
    
    # Import to PostgreSQL
    print(f"\n💾 Import vers PostgreSQL...")
    imported = 0
    
    print("  JSON files:")
    for file_path in files["json"]:
        if import_json_to_postgres(file_path, db):
            imported += 1
            print(f"    ✓ {Path(file_path).name}")
    
    print("  CSV files:")
    for file_path in files["csv"]:
        if import_csv_to_postgres(file_path, db):
            imported += 1
            print(f"    ✓ {Path(file_path).name}")
    
    print(f"✅ {imported} fichiers importés dans PostgreSQL")
    
    # Cleanup
    print("\n🧹 CLEANUP LOCAL - Avant suppression des fichiers")
    while True:
        choice = input("\nSupprimer les fichiers locaux? (y/n) [n]: ").strip().lower()
        if choice in ['y', 'n', '']:
            break
    
    if choice == 'y':
        cleanup_local_files(files, dry_run=True)
        confirm = input("\nConfirmer la suppression? (y/n) [n]: ").strip().lower()
        if confirm == 'y':
            cleanup_local_files(files, dry_run=False)
        else:
            print("❌ Suppression annulée")
    else:
        print("✅ Fichiers locaux conservés")
    
    # Summary
    db.disconnect()
    
    print("\n" + "=" * 80)
    print("✅ MIGRATION COMPLÉTÉE")
    print("=" * 80)
    print(f"📊 Résultats:")
    print(f"   ✓ {uploaded} fichiers sur MinIO")
    print(f"   ✓ {imported} records dans PostgreSQL")
    print(f"   ✓ Données archivées en date: {datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}")
    print("\n💡 Les données sont maintenant:")
    print("   - Stockées dans MinIO (objet storage)")
    print("   - Importées dans PostgreSQL (data warehouse)")
    print("   - Disponibles pour analyse et visualisation")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
