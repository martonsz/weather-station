import logging
import os
import signal
import sys
import threading

from dotenv import load_dotenv
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Optional

from home_assistant_card_capture import HomeAssistantCardCapture

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)
from common.logging_config import logger

logger = logger.getChild(__name__)

load_dotenv()

lock = threading.Lock()
capturer = HomeAssistantCardCapture(size=(320, 240))
image_path = Path("weather_card.png")
port = int(os.getenv("PORT", 8080))


def signal_handler(signum: int, frame: Optional[object]) -> None:
    """Handle shutdown signals gracefully"""
    logger.info(f"Received signal {signum}. Shutting down gracefully...")
    sys.exit(0)


class WeatherServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.index()
        elif self.path == "/weather-card":
            self.get_weather_card()
        else:
            self.send_error(404, "Not found")

    def index(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Hello World")

    def get_weather_card(self):
        image_exists = image_path.exists()
        if lock.acquire(blocking=not image_exists):
            try:
                capturer.capture_weather_card(image_path)
                try:
                    capturer.capture_weather_card(image_path)
                    self.send_response(200)
                    self.send_header("Content-type", "image/png")
                    self.end_headers()
                except Exception as e:
                    logger.error(f"Error serving weather card: {e}")
                    self.send_error(500, "Internal server error")
            finally:
                lock.release()
        with open(image_path, "rb") as f:
            self.wfile.write(f.read())


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    server = HTTPServer(("0.0.0.0", port), WeatherServer)
    logger.info(f"Starting server on port {port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        server.server_close()
