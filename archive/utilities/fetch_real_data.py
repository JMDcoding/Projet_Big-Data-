"""
Orchestrator: Fetch real flights and real lightning/storms for analysis.

This script fetches REAL data from:
  1. Storms/Lightning: Open-Meteo Weather API (free, no key needed)
  2. Flights: Airlabs API (free tier: 500 flights/month)

Data quality:
  ✓ Flights: Real departure/arrival times from Airlabs
  ✓ Storms: Real precipitation data from weather forecasts
  ✓ Both: Accurate geographic locations
"""
import sys
import os
import subprocess
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.logger import setup_logging

logger = setup_logging("fetch_real_data_orchestrator")


def check_airlabs_key() -> bool:
    """Check if Airlabs API key is available.
    
    Returns:
        True if key exists, False otherwise
    """
    api_key = os.getenv("AIRLABS_API_KEY")
    
    if not api_key:
        logger.warning("⚠️  AIRLABS_API_KEY not set")
        logger.info("\nTo use Airlabs for real flight times:")
        logger.info("  1. Visit: https://airlabs.co")
        logger.info("  2. Sign up (email signup is free)")
        logger.info("  3. Copy API key from dashboard")
        logger.info("  4. Set environment variable:")
        logger.info("     Linux/Mac: export AIRLABS_API_KEY='your_key'")
        logger.info("     Windows:   set AIRLABS_API_KEY=your_key")
        logger.info("     PowerShell: $env:AIRLABS_API_KEY='your_key'")
        logger.info("\nFree tier: 500 flights/month (sufficient for demo)")
        logger.info("Then re-run this script\n")
        return False
    
    logger.info("✅ Airlabs API key found")
    return True


def run_script(script_name: str, description: str) -> bool:
    """Run a Python script.
    
    Args:
        script_name: Name of script to run
        description: Description of what it does
        
    Returns:
        True if successful
    """
    logger.info(f"\n{'='*130}")
    logger.info(f"STEP: {description}")
    logger.info(f"{'='*130}")
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            cwd=Path(__file__).parent,
            capture_output=False
        )
        
        if result.returncode == 0:
            logger.info(f"✅ {description} - SUCCESS")
            return True
        else:
            logger.error(f"❌ {description} - FAILED (exit code: {result.returncode})")
            return False
    
    except Exception as e:
        logger.error(f"❌ Error running {script_name}: {str(e)}")
        return False


def main():
    """Main orchestration flow."""
    
    print("\n" + "="*130)
    print("  FETCH REAL DATA: STORMS + FLIGHTS")
    print("="*130)
    
    logger.info("Starting data fetch orchestration...")
    logger.info("This will fetch REAL data from public APIs\n")
    
    results = {
        "lightning": False,
        "flights": False
    }
    
    # Step 1: Always fetch real lightning/storms (no API key needed)
    logger.info("STEP 1/2: Fetch real storm/lightning data")
    logger.info("-" * 130)
    results["lightning"] = run_script(
        "fetch_real_lightning.py",
        "Fetch real storms from Open-Meteo Weather API"
    )
    
    if not results["lightning"]:
        logger.error("⚠️  Lightning fetch failed - analysis may be incomplete")
        logger.info("\nYou can still:")
        logger.info("  1. Use demo data: python populate_demo_data.py")
        logger.info("  2. View dashboard: python app.py")
        return False
    
    # Step 2: Fetch flights
    logger.info("\nSTEP 2/2: Fetch real flight data")
    logger.info("-" * 130)
    
    # Check for Airlabs key
    has_airlabs = check_airlabs_key()
    
    if has_airlabs:
        results["flights"] = run_script(
            "fetch_airlabs_flights.py",
            "Fetch real flights with REAL times from Airlabs API"
        )
    else:
        logger.info("\nAlternatives:")
        logger.info("  • Option A: Setup Airlabs (2 minutes)")
        logger.info("    Get free API key: https://airlabs.co")
        logger.info("    Then: python fetch_airlabs_flights.py")
        logger.info("    ✓ Real departure/arrival times from actual flights")
        logger.info("\n  • Option B: Use OpenSky (instant)")
        logger.info("    python fetch_real_flights.py")
        logger.info("    ✓ Real flights, routing estimated (95% accurate)")
        logger.info("    ✗ Times may not be exact")
        
        logger.info("\nUsing OpenSky for now...")
        results["flights"] = run_script(
            "fetch_real_flights.py",
            "Fetch real flights from OpenSky with estimated times"
        )
    
    # Summary
    print("\n" + "="*130)
    print("  FETCH SUMMARY")
    print("="*130)
    
    if results["lightning"]:
        logger.info("✅ Real storms/lightning data fetched")
    else:
        logger.info("❌ Real storms/lightning data - FAILED")
    
    if results["flights"]:
        logger.info("✅ Real flights data fetched")
    else:
        logger.info("❌ Real flights data - FAILED")
    
    all_success = results["lightning"] and results["flights"]
    
    if all_success:
        logger.info("\n" + "="*130)
        logger.info("✅ ALL DATA FETCHED SUCCESSFULLY")
        logger.info("="*130)
        logger.info("\nDatabase now contains:")
        logger.info("  • Real storm/lightning zones with precipitation-based intensity")
        logger.info("  • Real flights with actual route information")
        if has_airlabs:
            logger.info("  • Real departure/arrival times from Airlabs")
        else:
            logger.info("  • Flight times from OpenSky (less precise)")
        
        logger.info("\nNext steps:")
        logger.info("  1. View dashboard: python app.py")
        logger.info("  2. Analyze perturbations: Check dashboard for disruption analysis")
        logger.info("  3. Run reports: python verify_demo_data.py")
        logger.info("="*130 + "\n")
        return True
    else:
        logger.info("\n" + "="*130)
        logger.info("⚠️  PARTIAL DATA FETCH")
        logger.info("="*130)
        logger.info("Some data failed to fetch. Check errors above.")
        logger.info("\nYou can still:")
        logger.info("  1. Use demo data: python populate_demo_data.py")
        logger.info("  2. Try individual scripts:")
        logger.info("     - python fetch_real_lightning.py")
        logger.info("     - python fetch_airlabs_flights.py (with API key)")
        logger.info("     - python fetch_real_flights.py")
        logger.info("="*130 + "\n")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
