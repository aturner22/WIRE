"""
Test script to verify forecast hazard calculation with air quality.
"""
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv("../.env")

from app.services.hazard_calculator import hazard_calculator


async def test_forecast_calculation():
    """Test forecast calculation including respiratory hazard."""

    # Test location: London, UK
    lat = 51.5074
    lon = -0.1278

    print("=" * 60)
    print("WIRE - Forecast Hazard Calculation Test")
    print("=" * 60)
    print(f"\nTest Location: London, UK ({lat}, {lon})")
    print("\nFetching 24-hour forecast with air quality...\n")

    try:
        # Calculate forecast hazards (24 hours = 8 forecast points at 3-hour intervals)
        results = await hazard_calculator.calculate_forecast_hazards(lat, lon, hours=24)

        print(f"✅ Successfully calculated {len(results)} forecast points!\n")

        # Check first forecast point
        if results:
            first_forecast = results[0]
            print("=" * 60)
            print(f"FIRST FORECAST POINT: {first_forecast['dt_txt']}")
            print("=" * 60)

            hazards = first_forecast['hazards']
            print(f"\nTotal hazards calculated: {len(hazards)}")

            # Check if respiratory hazard is present
            if 'respiratory' in hazards:
                print("✅ RESPIRATORY HAZARD INCLUDED IN FORECAST!")
                resp = hazards['respiratory']
                print(f"   Score: {resp['score']}/5 ({resp['risk_level']})")
                print(f"   Factors: {list(resp['factors'].keys())}")
            else:
                print("⚠️  WARNING: Respiratory hazard NOT included in forecast")

            print(f"\nAll hazards in forecast:")
            for hazard_type, hazard in hazards.items():
                print(f"  - {hazard['name']}: {hazard['score']}/5 ({hazard['risk_level']})")

            print(f"\nSummary:")
            summary = first_forecast['summary']
            print(f"  Highest Risk: {summary['highest_risk']}/5")
            print(f"  Average Risk: {summary['average_risk']:.2f}/5")
            print(f"  Total Hazards: {summary['total_hazards']}")

        # Test all forecast points
        print("\n" + "=" * 60)
        print("ALL FORECAST POINTS")
        print("=" * 60)

        respiratory_count = 0
        for i, forecast in enumerate(results):
            has_respiratory = 'respiratory' in forecast['hazards']
            respiratory_count += 1 if has_respiratory else 0
            status = "✅" if has_respiratory else "❌"
            print(f"{status} Point {i+1}: {forecast['dt_txt']} - {len(forecast['hazards'])} hazards (respiratory: {has_respiratory})")

        print(f"\n📊 Respiratory hazard coverage: {respiratory_count}/{len(results)} forecast points")

        if respiratory_count == len(results):
            print("✅ PERFECT! All forecast points include respiratory hazard")
        elif respiratory_count > 0:
            print("⚠️  PARTIAL: Some forecast points missing respiratory hazard")
        else:
            print("❌ FAILED: No forecast points include respiratory hazard")

        print("\n" + "=" * 60)
        print("✅ Forecast test completed successfully!")
        print("=" * 60)

        return respiratory_count == len(results)

    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run forecast test."""

    # Check API key
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        print("❌ ERROR: OPENWEATHER_API_KEY not found in .env file!")
        print("Please add your API key to the .env file:")
        print("OPENWEATHER_API_KEY=your_key_here")
        return

    print(f"✅ API Key found: {api_key[:10]}...")

    # Run test
    success = await test_forecast_calculation()

    print("\n" + "=" * 60)
    if success:
        print("🎉 Forecast test PASSED - Respiratory hazard working!")
    else:
        print("⚠️  Forecast test FAILED - Check errors above")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
