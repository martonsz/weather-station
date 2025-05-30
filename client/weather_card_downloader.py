import asyncio
import os
from pathlib import Path
import sys
import aiohttp
from dotenv import load_dotenv

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)
from common.logging_config import logger

logger = logger.getChild(__name__)
load_dotenv()
SERVER_URLS = os.getenv("WEATHER_CARD_SERVER_URLS", "http://localhost:8080")
SERVER_PATH = os.getenv("WEATHER_CARD_SERVER_PATH", "/weather-card")
API_KEY = os.getenv("API_KEY")


class WeatherCardDownloader:
    def __init__(self, output_path: str = "weather_card.png"):
        """
        Initialize the WeatherCardDownloader with a list of server URLs and output path.

        Args:
            output_path (str): Path where the downloaded weather card will be saved
        """
        self.output_path = output_path
        self.servers = self._get_server_urls()
        self.server_path = SERVER_PATH
        self.headers = {"X-API-Key": API_KEY} if API_KEY else {}

        logger.info(f"Using servers: {self.servers}, with path: {self.server_path}")

    def _get_server_urls(self) -> list:
        """Get list of server URLs from environment variables."""
        servers = [url.strip() for url in SERVER_URLS.split(",") if url.strip()]
        return servers

    async def download(self) -> str:
        """
        Download the weather card from the first available server.

        Returns:
            str: Path to the downloaded weather card if successful, None otherwise
        """
        if not self.servers:
            logger.error("No servers configured for weather card download")
            return None

        for server_url in self.servers:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{server_url}{self.server_path}",
                        headers=self.headers
                    ) as response:
                        if response.status == 200:
                            content = await response.read()
                            with open(self.output_path, "wb") as f:
                                f.write(content)
                            logger.info(
                                f"Successfully downloaded weather card from {server_url}"
                            )
                            return self.output_path
                        elif response.status == 401:
                            logger.error(f"Authentication failed for {server_url}")
                            continue
                        else:
                            logger.warning(
                                f"Failed to download from {server_url}: Status {response.status}"
                            )
            except Exception as e:
                logger.error(f"Error downloading from {server_url}: {str(e)}")
                continue

        logger.error("Failed to download weather card from all servers")
        return None


if __name__ == "__main__":
    downloader = WeatherCardDownloader(output_path="weather_card-test.png")
    asyncio.run(downloader.download())
