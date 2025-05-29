import aiohttp
import asyncio
import os
import sys

from dotenv import load_dotenv
from pathlib import Path
from weather_data import WeatherData

project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from common.logging_config import logger

logger = logger.getChild(__name__)
# Load environment variables from .env file
load_dotenv()

# Read from environment (make sure you've done `source .env`)
HA_URL = os.getenv("HA_URL")
HA_TOKEN = os.getenv("HA_TOKEN")

if not HA_URL or not HA_TOKEN:
    raise RuntimeError("HA_URL and HA_TOKEN must be set in the environment")


async def get_entity_state(session: aiohttp.ClientSession, entity_id: str) -> dict:
    """
    Fetch the current state of a Home Assistant entity.
    Returns the full response data as a dict, or None if entity not found.
    """
    url = f"{HA_URL}/api/states/{entity_id}"
    headers = {
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json",
    }
    try:
        async with session.get(url, headers=headers) as resp:
            if resp.status == 404:
                return None
            resp.raise_for_status()
            return await resp.json()
    except aiohttp.ClientError as e:
        print(f"Error fetching {entity_id}: {str(e)}")
        return None


async def get_thermometer_data(device_base: str) -> dict:
    to_fetch = {
        "temperature": f"{device_base}_temperature",
        "humidity": f"{device_base}_humidity",
        "pressure": f"{device_base}_pressure",
    }

    async with aiohttp.ClientSession() as session:
        # Gather all states concurrently
        tasks = {
            name: asyncio.create_task(get_entity_state(session, eid))
            for name, eid in to_fetch.items()
        }
        results = {name: await task for name, task in tasks.items()}
        return results


async def get_weather_data() -> WeatherData:
    """
    Fetch weather data from SMHI integration in Home Assistant.
    Returns a WeatherData instance, or None if not found.
    """
    weather_entity = "weather.smhi_home"

    async with aiohttp.ClientSession() as session:
        weather_data = await get_entity_state(session, weather_entity)
        if weather_data:
            return WeatherData.from_dict(
                weather_data["attributes"], weather_data["state"]
            )
        return None


def main():
    device_base = "sensor.temp_carport"

    results = asyncio.run(get_thermometer_data(device_base))
    for name, data in results.items():
        if data is None:
            print(f"{name.capitalize()}:: Not available")
        else:
            print(
                f"{name.capitalize()}:: {data['state']} {data['attributes']['unit_of_measurement']}"
            )

    print("--------------------------------")

    weather_data = asyncio.run(get_weather_data())
    if weather_data:
        print(f"Condition: {weather_data.state}")
        print(
            f"Temperature: {weather_data.temperature} {weather_data.temperature_unit}"
        )
        print(f"Humidity: {weather_data.humidity}%")
        print(f"Wind Speed: {weather_data.wind_speed} {weather_data.wind_speed_unit}")
        print(f"Pressure: {weather_data.pressure} {weather_data.pressure_unit}")
        print(f"Visibility: {weather_data.visibility} {weather_data.visibility_unit}")
        print(f"Cloud Coverage: {weather_data.cloud_coverage}%")
        print(f"Thunder Probability: {weather_data.thunder_probability}%")
    else:
        print("Weather data not available")


if __name__ == "__main__":
    main()
