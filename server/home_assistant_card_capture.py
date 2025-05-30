import os
import sys

from PIL import Image
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
import playwright
from playwright.sync_api import sync_playwright
from typing import Optional, Tuple

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from common.logging_config import logger


# Create module-specific logger
logger = logger.getChild(__name__)

# Load environment variables from .env file
load_dotenv()

HA_URL = os.getenv("HA_URL")
dashboard_url = f"{HA_URL}/dashboard-weather/0"
HA_USERNAME = os.getenv("HA_USERNAME")
HA_PASSWORD = os.getenv("HA_PASSWORD")
ENABLE_VIDEO_CAPTURE = os.getenv("ENABLE_VIDEO_CAPTURE", "false").lower() == "true"


class HomeAssistantCardCapture:
    def __init__(
        self, output_path: Optional[str] = None, size: Tuple[int, int] = (320, 240)
    ) -> None:
        """
        Initialize the HomeAssistantCardCapture class.

        Args:
            output_path (str, optional): Directory where images will be saved.
                                       Defaults to current working directory.
            size (Tuple[int, int], optional): Dimensions for the screenshot (width, height).
                                            Defaults to (320, 240).
        """
        self.output_path = output_path or os.getcwd()
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)
        self.size = size

        # Create context options
        context_options = {
            "viewport": {"width": 1920, "height": 1080},
        }

        # Add video recording options if enabled
        if ENABLE_VIDEO_CAPTURE:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            video_path = os.path.join(self.output_path, f"recording_{timestamp}.webm")
            context_options.update(
                {
                    "record_video_dir": self.output_path,
                    "record_video_size": {"width": 1920, "height": 1080},
                }
            )

        # Initialize context with or without video recording
        self.context = self.browser.new_context(**context_options)
        self.page = self.context.new_page()

    def __del__(self):
        """Clean up the Playwright resources when the object is destroyed."""
        if hasattr(self, "context"):
            self.context.close()
        if hasattr(self, "browser"):
            self.browser.close()
        if hasattr(self, "playwright"):
            self.playwright.stop()

    def capture_weather_card(
        self, output_file: str, dashboard_url: str = dashboard_url
    ) -> Optional[str]:
        """
        Capture a weather card from a Home Assistant dashboard.

        Args:
            dashboard_url (str): The URL of the Home Assistant dashboard
            output_file (str): The filename where the image will be saved

        Returns:
            Optional[str]: Path to the saved image file, or None if capture failed
        """
        self.page.goto(dashboard_url, wait_until="domcontentloaded")

        # First check if we need to log in
        try:
            # Wait for either the weather card or the login form
            self.page.wait_for_selector(
                "hui-weather-forecast-card, input[name='username']",
                state="visible",
                timeout=5000
            )
            
            # Check if we're on the login page
            if self.page.locator('input[name="username"]').is_visible():
                logger.debug("Login form detected, attempting to log in...")
                self.page.locator('input[name="username"]').fill(HA_USERNAME)
                self.page.locator('input[name="password"]').fill(HA_PASSWORD)
                self.page.locator('input[name="password"]').press("Enter")
                
                # Wait for the weather card after login
                self.page.locator("hui-weather-forecast-card").wait_for(
                    state="visible", timeout=10000
                )
            else:
                logger.debug("Already authenticated, proceeding with capture...")
        except playwright._impl._errors.TimeoutError as e:
            logger.error(f"Timeout waiting for weather card or login form: {e}")
            return None

        # Set dark theme in local storage
        self.page.evaluate(
            """() => {
            localStorage.setItem('selectedTheme', JSON.stringify({dark: true}));
        }"""
        )

        # Wait for the weather card to be present
        self.page.locator("hui-weather-forecast-card").wait_for(state="visible")

        # Ensure the output directory exists
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Get the full path for the output file
        full_path = os.path.join(self.output_path, output_file)

        # Take screenshot of just the weather card element
        self.page.locator("hui-weather-forecast-card").screenshot(path=full_path)

        # Get the video path from the context if video recording is enabled
        if ENABLE_VIDEO_CAPTURE:
            self.page.locator("hui-weather-forecast-card").screenshot(
                path=os.path.join(self.output_path, "screenshot.png")
            )
            video_path = self.page.video.path()
            logger.debug(f"Recording saved to: {video_path}")

        full_path = self.scale_image(full_path, self.size[0], self.size[1])
        return full_path

    def scale_image(self, image_path: str, max_width: int, max_height: int) -> str:
        """
        Scale down an image to fit within maximum dimensions while maintaining aspect ratio.

        Args:
            image_path (str): Path to the input image
            max_width (int): Maximum width for the scaled image
            max_height (int): Maximum height for the scaled image

        Returns:
            str: Path to the scaled image file
        """
        # Open the image
        with Image.open(image_path) as img:
            # Calculate the scaling factor to maintain aspect ratio
            width_ratio = max_width / img.width
            height_ratio = max_height / img.height
            scale_factor = min(width_ratio, height_ratio)

            # Only scale down if the image is larger than max dimensions
            if scale_factor < 1:
                # Calculate new dimensions
                new_width = int(img.width * scale_factor)
                new_height = int(img.height * scale_factor)

                # Resize the image
                resized_img = img.resize(
                    (new_width, new_height), Image.Resampling.LANCZOS
                )

                # Save the resized image
                resized_img.save(image_path, quality=100)
                return image_path
            else:
                logger.debug(
                    "Image is already smaller than max dimensions, no scaling needed"
                )
                return image_path


def main() -> None:
    if not all([HA_URL, HA_USERNAME, HA_PASSWORD]):
        logger.error(
            "Error: HA_URL, HA_USERNAME, and HA_PASSWORD must be set in .env file"
        )
        return

    # Create an instance of HomeAssistantCardCapture
    capturer = HomeAssistantCardCapture()

    # Example usage
    output_file = "weather_card.png"

    logger.info(f"Using Home Assistant URL: {HA_URL}")
    logger.info(f"Dashboard URL: {dashboard_url}")

    # Capture the weather card
    result = capturer.capture_weather_card(output_file)

    if result:
        logger.info(f"Successfully captured weather card to: {result}")
    else:
        logger.error("Failed to capture weather card")


if __name__ == "__main__":
    main()
