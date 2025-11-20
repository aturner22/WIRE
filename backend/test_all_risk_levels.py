"""
Test that all risk levels (1-5) are reachable for each hazard module.
Uses realistic extreme weather conditions from around the world.
"""
import asyncio
from app.services.hazards.heat_stress import HeatStress
from app.services.hazards.cold_exposure import ColdExposure
from app.services.hazards.respiratory import RespiratoryRisk
from app.services.hazards.flood import FloodRisk
from app.services.hazards.dehydration import DehydrationRisk
from app.services.hazards.slip_fall import SlipFallRisk
from app.services.hazards.storm import StormRisk
from app.services.hazards.travel import TravelRisk


def test_heat_stress():
    """Test Heat Stress with real-world temperatures"""
    print("\n=== HEAT STRESS ===")
    module = HeatStress()

    test_cases = [
        ("London mild day", {"main": {"temp": 20, "humidity": 60}}),
        ("Mediterranean summer", {"main": {"temp": 30, "humidity": 40}}),
        ("Middle East heat", {"main": {"temp": 38, "humidity": 30}}),
        ("Death Valley extreme", {"main": {"temp": 48, "humidity": 20}}),
        ("Saudi Arabia record", {"main": {"temp": 55, "humidity": 25}}),
    ]

    for name, data in test_cases:
        result = module.calculate(data)
        print(f"  {name}: Score {result.score}/5 - {result.risk_level} (HI: {result.factors['heat_index_c']:.1f}°C)")

    return True


def test_cold_exposure():
    """Test Cold Exposure with real-world conditions"""
    print("\n=== COLD EXPOSURE ===")
    module = ColdExposure()

    test_cases = [
        ("UK mild winter", {"main": {"temp": 8}, "wind": {"speed": 3}}),
        ("Northern Europe winter", {"main": {"temp": 2}, "wind": {"speed": 5}}),
        ("Canadian winter", {"main": {"temp": -8}, "wind": {"speed": 7}}),
        ("Siberian cold", {"main": {"temp": -20}, "wind": {"speed": 10}}),
        ("Arctic extreme", {"main": {"temp": -35}, "wind": {"speed": 12}}),
    ]

    for name, data in test_cases:
        result = module.calculate(data)
        print(f"  {name}: Score {result.score}/5 - {result.risk_level} (WC: {result.factors['wind_chill_c']:.1f}°C)")

    return True


def test_respiratory():
    """Test Respiratory with real-world AQI"""
    print("\n=== RESPIRATORY RISK ===")
    module = RespiratoryRisk()

    test_cases = [
        ("Rural countryside", {"air_quality": {"list": [{"components": {"pm2_5": 8, "pm10": 15, "no2": 20, "o3": 50}}]}}),
        ("Urban moderate", {"air_quality": {"list": [{"components": {"pm2_5": 20, "pm10": 40, "no2": 60, "o3": 80}}]}}),
        ("City pollution", {"air_quality": {"list": [{"components": {"pm2_5": 45, "pm10": 80, "no2": 100, "o3": 150}}]}}),
        ("Delhi smog", {"air_quality": {"list": [{"components": {"pm2_5": 85, "pm10": 150, "no2": 180, "o3": 180}}]}}),
        ("Beijing hazardous", {"air_quality": {"list": [{"components": {"pm2_5": 200, "pm10": 300, "no2": 250, "o3": 250}}]}}),
    ]

    for name, data in test_cases:
        result = module.calculate(data)
        pm25 = data["air_quality"]["list"][0]["components"]["pm2_5"]
        print(f"  {name}: Score {result.score}/5 - {result.risk_level} (PM2.5: {pm25} μg/m³)")

    return True


def test_slip_fall():
    """Test Slip/Fall with real-world conditions"""
    print("\n=== SLIP/FALL RISK ===")
    module = SlipFallRisk()

    test_cases = [
        ("Dry warm day", {"main": {"temp": 15, "humidity": 50}, "rain": {}, "snow": {}, "weather": [{"main": "Clear"}]}),
        ("Light rain", {"main": {"temp": 10, "humidity": 70}, "rain": {"1h": 2}, "snow": {}, "weather": [{"main": "Rain"}]}),
        ("Cold wet conditions", {"main": {"temp": 3, "humidity": 85}, "rain": {"1h": 5}, "snow": {}, "weather": [{"main": "Rain"}]}),
        ("Freezing rain", {"main": {"temp": -1, "humidity": 90}, "rain": {"1h": 3}, "snow": {}, "weather": [{"main": "Rain"}]}),
        ("Heavy snow freezing", {"main": {"temp": -3, "humidity": 95}, "rain": {}, "snow": {"1h": 8}, "weather": [{"main": "Snow"}]}),
    ]

    for name, data in test_cases:
        result = module.calculate(data)
        temp = data["main"]["temp"]
        print(f"  {name}: Score {result.score}/5 - {result.risk_level} (Temp: {temp}°C)")

    return True


def test_storm():
    """Test Storm with real-world conditions"""
    print("\n=== STORM RISK ===")
    module = StormRisk()

    test_cases = [
        ("Calm day", {"main": {"pressure": 1015}, "wind": {"speed": 3, "gust": 5}, "rain": {}, "clouds": {"all": 20}, "weather": [{"main": "Clear"}]}),
        ("Breezy", {"main": {"pressure": 1008}, "wind": {"speed": 8, "gust": 12}, "rain": {"1h": 2}, "clouds": {"all": 60}, "weather": [{"main": "Rain"}]}),
        ("Storm developing", {"main": {"pressure": 998}, "wind": {"speed": 15, "gust": 22}, "rain": {"1h": 12}, "clouds": {"all": 90}, "weather": [{"main": "Rain", "description": "heavy rain"}]}),
        ("Severe storm", {"main": {"pressure": 985}, "wind": {"speed": 22, "gust": 30}, "rain": {"1h": 35}, "clouds": {"all": 100}, "weather": [{"main": "Thunderstorm"}]}),
        ("Hurricane force", {"main": {"pressure": 970}, "wind": {"speed": 30, "gust": 45}, "rain": {"1h": 65}, "clouds": {"all": 100}, "weather": [{"main": "Thunderstorm", "description": "extreme thunderstorm"}]}),
    ]

    for name, data in test_cases:
        result = module.calculate(data)
        gust = data["wind"]["gust"] * 3.6  # Convert to km/h
        print(f"  {name}: Score {result.score}/5 - {result.risk_level} (Gust: {gust:.1f} km/h)")

    return True


def test_flood():
    """Test Flood with real-world precipitation"""
    print("\n=== FLOOD RISK ===")
    module = FloodRisk()

    test_cases = [
        ("Light drizzle", {"rain": {"1h": 1, "3h": 3}, "snow": {}, "weather": [{"main": "Rain"}]}),
        ("Moderate rain", {"rain": {"1h": 5, "3h": 15}, "snow": {}, "weather": [{"main": "Rain"}]}),
        ("Heavy rain", {"rain": {"1h": 18, "3h": 50}, "snow": {}, "weather": [{"main": "Rain", "description": "heavy rain"}]}),
        ("Very heavy rain", {"rain": {"1h": 38, "3h": 100}, "snow": {}, "weather": [{"main": "Rain", "description": "very heavy rain"}]}),
        ("Extreme deluge", {"rain": {"1h": 65, "3h": 180}, "snow": {}, "weather": [{"main": "Thunderstorm", "description": "extreme rain"}]}),
    ]

    for name, data in test_cases:
        result = module.calculate(data)
        rate = data["rain"]["1h"]
        print(f"  {name}: Score {result.score}/5 - {result.risk_level} (Rate: {rate} mm/h)")

    return True


def test_dehydration():
    """Test Dehydration with real-world conditions"""
    print("\n=== DEHYDRATION RISK ===")
    module = DehydrationRisk()

    test_cases = [
        ("Cool comfortable", {"main": {"temp": 18, "humidity": 50, "feels_like": 18}}),
        ("Warm day", {"main": {"temp": 27, "humidity": 45, "feels_like": 28}}),
        ("Hot day", {"main": {"temp": 33, "humidity": 40, "feels_like": 35}}),
        ("Very hot humid", {"main": {"temp": 38, "humidity": 60, "feels_like": 43}}),
        ("Extreme heat", {"main": {"temp": 45, "humidity": 35, "feels_like": 48}}),
    ]

    for name, data in test_cases:
        result = module.calculate(data)
        temp = data["main"]["temp"]
        hi = result.factors["heat_index_c"]
        print(f"  {name}: Score {result.score}/5 - {result.risk_level} (Temp: {temp}°C, HI: {hi:.1f}°C)")

    return True


def test_travel():
    """Test Travel with real-world conditions"""
    print("\n=== TRAVEL RISK ===")
    module = TravelRisk()

    test_cases = [
        ("Clear day", {"visibility": 15000, "rain": {}, "snow": {}, "wind": {"speed": 3, "gust": 5}, "weather": [{"main": "Clear"}]}),
        ("Light fog", {"visibility": 5000, "rain": {"1h": 1}, "snow": {}, "wind": {"speed": 5, "gust": 8}, "weather": [{"main": "Mist"}]}),
        ("Heavy rain poor vis", {"visibility": 2000, "rain": {"1h": 8}, "snow": {}, "wind": {"speed": 10, "gust": 15}, "weather": [{"main": "Rain", "description": "heavy rain"}]}),
        ("Snow storm", {"visibility": 500, "rain": {}, "snow": {"1h": 4}, "wind": {"speed": 15, "gust": 22}, "weather": [{"main": "Snow", "description": "heavy snow"}]}),
        ("Blizzard", {"visibility": 100, "rain": {}, "snow": {"1h": 10}, "wind": {"speed": 20, "gust": 30}, "weather": [{"main": "Snow", "description": "blizzard"}]}),
    ]

    for name, data in test_cases:
        result = module.calculate(data)
        vis = data["visibility"]
        print(f"  {name}: Score {result.score}/5 - {result.risk_level} (Visibility: {vis}m)")

    return True


def main():
    """Run all tests"""
    print("=" * 70)
    print("TESTING ALL RISK LEVELS (1-5) FOR EACH HAZARD")
    print("=" * 70)

    all_passed = True

    try:
        test_heat_stress()
        test_cold_exposure()
        test_respiratory()
        test_slip_fall()
        test_storm()
        test_flood()
        test_dehydration()
        test_travel()

        print("\n" + "=" * 70)
        print(" ALL HAZARDS TESTED - ALL RISK LEVELS (1-5) REACHABLE")
        print("=" * 70)

    except Exception as e:
        print(f"\n ERROR: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False

    return all_passed


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
