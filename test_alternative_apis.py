#!/usr/bin/env python3
"""
Test alternative APIs for lightning and flight data.
Find the most reliable sources when primary APIs fail.
"""
import sys
import logging
from pathlib import Path
from datetime import datetime
import json

sys.path.insert(0, str(Path.cwd()))

# Setup logging
logging.basicConfig(
    format='%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

from src.ingestion.api_client import BlitzortungAPI, OpenMeteoAPI, AviationStackAPI
from src.ingestion.alternative_apis import (
    WeatherAPILightning,
    OpenWeatherLightning,
    ADSBExchangeAPI,
    OpenSkyAlternative
)


def test_lightning_apis():
    """Test all available lightning APIs."""
    logger.info("=" * 80)
    logger.info("⚡ TESTING LIGHTNING DATA SOURCES")
    logger.info("=" * 80)
    logger.info("")
    
    lightning_apis = [
        ("Blitzortung API", BlitzortungAPI()),
        ("OpenMeteo API", OpenMeteoAPI()),
        ("WeatherAPI", WeatherAPILightning(api_key="free", lat=48.8, lon=2.3)),
        ("OpenWeather", OpenWeatherLightning(api_key="", lat=48.8, lon=2.3)),
    ]
    
    results = {}
    
    for name, api in lightning_apis:
        try:
            logger.info(f"🔌 Testing {name}...")
            data = api.fetch()
            strikes = data.get("strikes", [])
            
            status = "✅ OK" if strikes else "⚠️  No data"
            logger.info(f"   {status} - {len(strikes)} strikes found")
            
            results[name] = {
                "status": "success" if strikes else "no_data",
                "strikes": len(strikes),
                "data": data
            }
        
        except Exception as e:
            logger.error(f"   ❌ FAILED - {str(e)}")
            results[name] = {
                "status": "error",
                "error": str(e)
            }
    
    return results


def test_flight_apis():
    """Test all available flight APIs."""
    logger.info("")
    logger.info("=" * 80)
    logger.info("✈️  TESTING FLIGHT DATA SOURCES")
    logger.info("=" * 80)
    logger.info("")
    
    flight_apis = [
        ("AviationStack", AviationStackAPI()),
        ("ADS-B Exchange", ADSBExchangeAPI(lat=48.8, lon=2.3, radius_km=100)),
        ("OpenSky Network", OpenSkyAlternative(lat=48.8, lon=2.3, radius_km=50)),
    ]
    
    results = {}
    
    for name, api in flight_apis:
        try:
            logger.info(f"🔌 Testing {name}...")
            data = api.fetch()
            flights = data.get("flights", [])
            
            status = "✅ OK" if flights else "⚠️  No data"
            logger.info(f"   {status} - {len(flights)} flights found")
            
            if flights:
                logger.info(f"   Sample: {flights[0].get('flight_number', 'N/A')} @ " 
                          f"({flights[0].get('latitude', 0):.2f}, "
                          f"{flights[0].get('longitude', 0):.2f})")
            
            results[name] = {
                "status": "success" if flights else "no_data",
                "flights": len(flights),
                "data": data
            }
        
        except Exception as e:
            logger.error(f"   ❌ FAILED - {str(e)}")
            results[name] = {
                "status": "error",
                "error": str(e)
            }
    
    return results


def print_summary(lightning_results, flight_results):
    """Print summary of API test results."""
    logger.info("")
    logger.info("=" * 80)
    logger.info("📊 SUMMARY")
    logger.info("=" * 80)
    logger.info("")
    
    logger.info("⚡ LIGHTNING SOURCES:")
    logger.info("-" * 80)
    
    working_lightning = []
    for name, result in lightning_results.items():
        status_icon = "✅" if result.get("strikes", 0) > 0 else "⚠️"
        strikes = result.get("strikes", 0)
        error = result.get("error", "")
        
        if strikes > 0:
            working_lightning.append(name)
            logger.info(f"{status_icon} {name:<25} | Strikes: {strikes:4} | ✓ Working")
        elif error:
            logger.info(f"❌ {name:<25} | Error: {error[:40]}")
        else:
            logger.info(f"{status_icon} {name:<25} | No strikes detected")
    
    logger.info("")
    logger.info("✈️  FLIGHT SOURCES:")
    logger.info("-" * 80)
    
    working_flights = []
    for name, result in flight_results.items():
        status_icon = "✅" if result.get("flights", 0) > 0 else "⚠️"
        flights = result.get("flights", 0)
        error = result.get("error", "")
        
        if flights > 0:
            working_flights.append(name)
            logger.info(f"{status_icon} {name:<25} | Flights: {flights:4} | ✓ Working")
        elif error:
            logger.info(f"❌ {name:<25} | Error: {error[:40]}")
        else:
            logger.info(f"{status_icon} {name:<25} | No flights detected")
    
    logger.info("")
    logger.info("=" * 80)
    logger.info("📈 RECOMMENDATIONS")
    logger.info("=" * 80)
    logger.info("")
    
    if working_lightning:
        logger.info(f"✅ Lightning: Use {', '.join(working_lightning)}")
    else:
        logger.info("⚠️  Lightning: No working APIs found - check internet/credentials")
    
    if working_flights:
        logger.info(f"✅ Flights: Use {', '.join(working_flights)}")
    else:
        logger.info("⚠️  Flights: No working APIs found - check internet/credentials")
    
    logger.info("")


def main():
    """Run all API tests."""
    logger.info("🚀 STARTING API COMPATIBILITY TEST")
    logger.info(f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("")
    
    try:
        # Test lightning APIs
        lightning_results = test_lightning_apis()
        
        # Test flight APIs
        flight_results = test_flight_apis()
        
        # Print summary
        print_summary(lightning_results, flight_results)
        
        logger.info("✅ Test complete!")
    
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
