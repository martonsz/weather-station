import os
import asyncio
import aiohttp
from dotenv import load_dotenv

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
        "humidity":    f"{device_base}_humidity",
        "pressure":    f"{device_base}_pressure",
    }

    async with aiohttp.ClientSession() as session:
        # Gather all states concurrently
        tasks = {
            name: asyncio.create_task(get_entity_state(session, eid))
            for name, eid in to_fetch.items()
        }
        results = {name: await task for name, task in tasks.items()}
        return results

def main():
    device_base = "sensor.temp_carport"

    results = asyncio.run(get_thermometer_data(device_base))

    # Print out the results
    for name, data in results.items():
        if data is None:
            print(f"{name.capitalize()}: Not available")
        else:
            print(f"{name.capitalize()}: {data['state']} {data['attributes']['unit_of_measurement']}")


if __name__ == "__main__":
    main()
