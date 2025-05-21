import os
import aiohttp
from typing import List
from weather_data import ForecastHourly
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Default to Östersund coordinates if not set in .env
SMHI_LAT = os.getenv("SMHI_LAT")
SMHI_LON = os.getenv("SMHI_LON")


async def get_hourly_forecast() -> List[ForecastHourly]:
    """
    Fetch hourly forecast data directly from SMHI API.
    Returns a list of ForecastHourly instances, or empty list if not found.
    """
    # SMHI API endpoint for hourly forecast
    url = f"https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/{SMHI_LON}/lat/{SMHI_LAT}/data.json"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    print(f"Failed to fetch SMHI forecast data: {resp.status}")
                    return []

                data = await resp.json()
                forecasts = []

                # Process each time series entry
                for time_series in data.get("timeSeries", []):
                    valid_time = time_series.get("validTime")
                    parameters = {
                        p["name"]: p["values"][0]
                        for p in time_series.get("parameters", [])
                    }

                    # Create forecast entry if we have the required data
                    if all(
                        key in parameters for key in ["t", "ws", "wd", "r", "Wsymb2"]
                    ):
                        forecast = {
                            "datetime": valid_time,
                            "temperature": parameters["t"],
                            "temperature_unit": "°C",
                            "condition": str(
                                parameters["Wsymb2"]
                            ),  # Weather symbol code
                            "precipitation_probability": parameters.get("r", 0),
                            "wind_speed": parameters["ws"],
                            "wind_speed_unit": "m/s",
                            "wind_bearing": parameters["wd"],
                            "humidity": parameters.get("rh", 0),
                        }
                        forecasts.append(ForecastHourly.from_dict(forecast))

                return forecasts

    except Exception as e:
        print(f"Error fetching SMHI forecast: {str(e)}")
        return []


async def main():
    """
    Test function to demonstrate the SMHI weather forecast functionality.
    """
    print("Fetching hourly weather forecast from SMHI...")
    forecasts = await get_hourly_forecast()

    if not forecasts:
        print("No forecast data available")
        return

    print(f"\nFound {len(forecasts)} forecast entries:")
    for forecast in forecasts:
        print(f"\nTime: {forecast.datetime}")
        print(f"Temperature: {forecast.temperature}{forecast.temperature_unit}")
        print(f"Condition: {forecast.emoji} {forecast.condition}")
        print(f"Precipitation Probability: {forecast.precipitation_probability}%")
        print(f"Wind Speed: {forecast.wind_speed} {forecast.wind_speed_unit}")
        print(f"Wind Bearing: {forecast.wind_bearing}°")
        print(f"Humidity: {forecast.humidity}%")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
