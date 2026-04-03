"""
Data orchestration and refresh script.
Script d'orchestration des données et refresh.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import subprocess
from config.config import Config
from src.utils.logger import setup_logging

logger = setup_logging("data_orchestrator")


class DataOrchestrator:
    """Orchestrate data fetching from various sources."""
    
    def __init__(self):
        """Initialize orchestrator."""
        self.scripts_dir = Path(__file__).parent
        self.project_root = self.scripts_dir.parent
    
    def fetch_lightning(self):
        """Fetch lightning data from weather API."""
        logger.info("\n⚡ Fetching lightning data...")
        script = self.scripts_dir / "fetch_lightning.py"
        
        try:
            result = subprocess.run(
                [sys.executable, str(script)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("✅ Lightning data fetched successfully")
                return True
            else:
                logger.error(f"❌ Lightning fetch failed: {result.stderr}")
                return False
        
        except Exception as e:
            logger.error(f"❌ Error fetching lightning: {str(e)}")
            return False
    
    def fetch_flights(self):
        """Fetch flight data from API."""
        logger.info("\n✈️  Fetching flight data...")
        script = self.scripts_dir / "fetch_flights.py"
        
        try:
            result = subprocess.run(
                [sys.executable, str(script)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("✅ Flight data fetched successfully")
                return True
            else:
                logger.error(f"❌ Flight fetch failed: {result.stderr}")
                return False
        
        except Exception as e:
            logger.error(f"❌ Error fetching flights: {str(e)}")
            return False
    
    def run_full_refresh(self):
        """Run full data refresh pipeline."""
        print("\n" + "="*80)
        print("  DATA REFRESH PIPELINE")
        print("="*80)
        
        logger.info("Starting data refresh...")
        
        # Fetch data
        lightning_ok = self.fetch_lightning()
        flights_ok = self.fetch_flights()
        
        # Summary
        print("\n" + "="*80)
        print("  REFRESH SUMMARY")
        print("="*80)
        logger.info(f"Lightning: {'✅ OK' if lightning_ok else '❌ FAILED'}")
        logger.info(f"Flights: {'✅ OK' if flights_ok else '❌ FAILED'}")
        
        success = lightning_ok and flights_ok
        logger.info(f"\n{'✅ REFRESH COMPLETE' if success else '❌ REFRESH INCOMPLETE'}\n")
        
        return success


if __name__ == "__main__":
    orchestrator = DataOrchestrator()
    success = orchestrator.run_full_refresh()
    sys.exit(0 if success else 1)
