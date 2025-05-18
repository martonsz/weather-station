import os
import asyncio
import signal
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from datetime import datetime
from ha_client import get_thermometer_data
from display import Display

# Load environment variables
load_dotenv()

# Configure logging
LOG_DIR = os.getenv("LOG_DIR", "log")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "weather_station.log")

# Get log level from environment variable
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
numeric_level = getattr(logging, log_level, logging.INFO)

# Set up logging with rotation
handler = RotatingFileHandler(
    LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=1, encoding="utf-8"  # 5MB
)
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

logger = logging.getLogger("weather_station")
logger.setLevel(numeric_level)
logger.addHandler(handler)

# Initialize display
display = Display()
device_base = "sensor.temp_carport"


async def update_temperature():
    try:
        # Get temperature data
        results = await get_thermometer_data(device_base)

        if results["temperature"] is None:
            logger.error("Failed to fetch temperature data")
            display.set_led(1, 0, 0)  # Red LED for error
            return "Error"
        else:
            temp = results["temperature"]["state"]
            unit = results["temperature"]["attributes"]["unit_of_measurement"]
            display.set_led(0, 0, 0)  # Turn off LED
            logger.debug(
                f"Fetched temperature: {temp if results['temperature'] else 'N/A'}"
            )
            return f"{temp} {unit}"

    except Exception as e:
        logger.error(f"Error updating temperature: {str(e)}")
        display.set_led(1, 0, 0)  # Red LED for error
        return "Error"


def get_datetime():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


async def main():
    logger.info("Weather station started")
    display.set_backlight(0.5)  # Set display brightness to 50%
    display.graphics.draw_text_centerted("Starting...")

    while True:
        # Update temperature every 5 seconds
        current_temp = await update_temperature()

        # Update time every second for 5 seconds
        for _ in range(5):
            display.clear()
            if current_temp:
                display.graphics.draw_text_centerted(current_temp)
            display.graphics.draw_text_bottom(get_datetime())
            display.display()
            await asyncio.sleep(1)


def signal_handler(sig, frame):
    logger.info("Received shutdown signal")
    display.set_led(0, 0, 1)
    display.clear()
    display.graphics.draw_text_centerted("Shutting down...")
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
