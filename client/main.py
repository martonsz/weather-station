import asyncio
import os
from pathlib import Path
import signal

from datetime import datetime
import sys

from display import Display
from dotenv import load_dotenv
from ha_client import get_thermometer_data
from weather_card_downloader import WeatherCardDownloader

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)
from common.logging_config import logger

logger = logger.getChild(__name__)
load_dotenv()

# Initialize display and card capture
display = Display()
device_base = os.getenv("DEVICE_BASE", "sensor.temp_carport")
HA_URL = os.getenv("HA_URL")

downloader = WeatherCardDownloader("weather_card.png")


def get_datetime():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


async def download_weather_card():
    """Download the weather card image from the server."""
    return await downloader.download()


async def main():
    logger.info("Weather station started")
    display.set_backlight(0.5)  # Set display brightness to 50%
    display.graphics.draw_text("Starting...")

    while True:
        # Get current temperature from thermometer
        thermometer_data = await get_thermometer_data(device_base)
        if not thermometer_data or not thermometer_data["temperature"]:
            logger.error("Failed to get temperature data")
            display.set_led(1, 0, 0)  # Red LED for error
            current_temp = "error"
        else:
            current_temp = thermometer_data["temperature"]["state"]
            display.set_led(0, 1, 0)  # Green LED for success

        # Update weather card image
        weather_card_path = await download_weather_card()
        if not weather_card_path:
            logger.error("Failed to update weather card")
            display.set_led(1, 0, 0)  # Red LED for error
        else:
            display.set_led(0, 1, 0)  # Green LED for success

        for _ in range(15):
            display.clear()
            display.graphics.draw_text_centered_horizontal(f"{current_temp}°C", 5, 40)
            if weather_card_path:
                display.graphics.draw_image(weather_card_path, 0, 80, 1.0)
            display.graphics.draw_text(get_datetime(), 34, 205, 24)
            display.display()
            await asyncio.sleep(1)


def signal_handler(sig, frame):
    logger.info("Received shutdown signal")
    display.set_led(0, 0, 1)
    display.clear()
    display.graphics.draw_text("Shutting down...")
    display.display()
    exit(0)


if __name__ == "__main__":
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Program terminated by user")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise
