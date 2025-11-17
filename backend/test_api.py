"""
Quick test script to verify OpenWeather API integration.
Run this to test the hazard calculation system with real data.
"""
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv("../.env")

from app.services.hazard_calculator import hazard_calculator


async def test_hazard_calculation():
    """Test hazard calculation with real weather data."""

    # Test location: London, UK
    lat = 51.5074
    lon = -0.1278

    print("=" * 60)
    print("SafetyWatch - Hazard Calculation Test")
    print("=" * 60)
    print(f"\nTest Location: London, UK ({lat}, {lon})")
    print("\nFetching weather data and calculating hazards...\n")

    try:
        # Calculate all hazards
        result = await hazard_calculator.calculate_all_hazards(lat, lon)

        print("✅ Successfully calculated hazards!\n")
        print("=" * 60)
        print("SUMMARY")
        print("=" * 60)

        summary = result["summary"]
        print(f"Highest Risk Level: {summary['highest_risk']}/5")
        print(f"Average Risk: {summary['average_risk']:.2f}/5")
        print(f"\nRisk Distribution:")
        print(f"  - Extreme:    {summary['extreme_count']}")
        print(f"  - Very High:  {summary['very_high_count']}")
        print(f"  - High:       {summary['high_count']}")
        print(f"  - Moderate:   {summary['moderate_count']}")
        print(f"  - Low:        {summary['low_count']}")

        print(f"\n⚠️  Hazards above Moderate: {summary['hazards_above_moderate']}")

        print("\n" + "=" * 60)
        print("INDIVIDUAL HAZARDS")
        print("=" * 60)

        # Display each hazard
        for hazard_type, hazard in result["hazards"].items():
            print(f"\n📊 {hazard['name']}")
            print(f"   Score: {hazard['score']}/5 ({hazard['risk_level']})")
            print(f"   Confidence: {hazard.get('confidence', 'N/A')}")

            # Show key factors
            print(f"   Key Factors:")
            for key, value in list(hazard['factors'].items())[:3]:
                print(f"     - {key}: {value}")

            # Show top recommendation
            if hazard['recommendations']:
                print(f"   Top Recommendation: {hazard['recommendations'][0]}")

        # Check for errors
        if result.get("errors"):
            print("\n" + "=" * 60)
            print("⚠️  ERRORS")
            print("=" * 60)
            for hazard_type, error in result["errors"].items():
                print(f"  - {hazard_type}: {error}")

        print("\n" + "=" * 60)
        print("✅ Test completed successfully!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_single_hazard():
    """Test a single hazard calculation."""

    print("\n" + "=" * 60)
    print("Testing Individual Hazard: Heat Stress")
    print("=" * 60)

    lat = 51.5074
    lon = -0.1278

    try:
        result = await hazard_calculator.calculate_single_hazard(
            "heat_stress", lat, lon
        )

        print(f"\n✅ Heat Stress Calculation:")
        print(f"   Score: {result.score}/5")
        print(f"   Level: {result.risk_level}")
        print(f"   Factors: {result.factors}")
        print(f"   Recommendations: {result.recommendations[:2]}")

        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


async def main():
    """Run all tests."""

    # Check API key
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        print("❌ ERROR: OPENWEATHER_API_KEY not found in .env file!")
        print("Please add your API key to the .env file:")
        print("OPENWEATHER_API_KEY=your_key_here")
        return

    print(f"✅ API Key found: {api_key[:10]}...")

    # Run tests
    test1 = await test_hazard_calculation()
    test2 = await test_single_hazard()

    print("\n" + "=" * 60)
    if test1 and test2:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed - check errors above")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
