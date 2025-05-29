import os
from pathlib import Path
import platform
import sys
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)
from common.logging_config import logger

logger = logger.getChild(__name__)


class Graphics:
    def __init__(self, width: int = 320, height: int = 240):
        self.image = Image.new("RGB", (width, height), (34, 34, 34))
        self.draw = ImageDraw.Draw(self.image)
        self.width = width
        self.height = height
        self.font_path = self._find_font_path()  # Store only the path
        self.font = self._create_font(20)  # Default size

    def _find_font_path(self):
        # Try to find fonts with emoji support based on the operating system
        font_paths = {
            "Linux": [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/TTF/DejaVuSans.ttf",
                "/usr/share/fonts/dejavu/DejaVuSans.ttf",
            ],
            "Windows": [
                "C:\\Windows\\Fonts\\DejaVuSans.ttf",
                "C:\\Windows\\Fonts\\dejavu\\DejaVuSans.ttf",
            ],
        }

        current_os = platform.system()
        logger.debug(f"Detected operating system: {current_os}")

        paths_to_try = font_paths.get(current_os, []) + font_paths.get("Linux", [])

        for path in paths_to_try:
            if os.path.exists(path):
                try:
                    logger.debug(f"Using font: {path}")
                    return path
                except Exception as e:
                    logger.warning(f"Failed to load font from {path}: {str(e)}")
                    continue

        logger.info("No font path found, will use default font")
        return None

    def _create_font(self, size):
        if self.font_path:
            try:
                return ImageFont.truetype(self.font_path, size)
            except Exception as e:
                logger.warning(f"Failed to create font with size {size}: {str(e)}")
                # Try with a fallback size if the requested size fails
                try:
                    return ImageFont.truetype(self.font_path, 16)
                except Exception as e:
                    logger.warning(f"Failed to create fallback font: {str(e)}")

        try:
            return ImageFont.load_default()
        except Exception as e:
            logger.warning(f"Failed to load default font: {str(e)}")
            return ImageFont.truetype(None, size)

    def draw_text(self, text, x=10, y=10, size=20):
        if size is not None:
            self.font = self._create_font(size)
        self.draw.text((x, y), text, fill="white", font=self.font)

    def draw_text_centerted(self, text, ratio=0.8) -> None:
        # Create a temporary font to measure text
        temp_font = self._create_font(100)  # Use a reference size of 100
        text_bbox = temp_font.getbbox(text)
        ref_width = text_bbox[2] - text_bbox[0]
        ref_height = text_bbox[3] - text_bbox[1]

        # Calculate scale factors based on screen dimensions and ratio
        width_scale = (self.width * ratio) / ref_width
        height_scale = (self.height * ratio) / ref_height

        # Use the smaller scale to ensure text fits both dimensions
        font_size = int(min(width_scale, height_scale) * 100)

        # Create the final font with calculated size
        font = self._create_font(font_size)

        # Get final text dimensions
        text_bbox = font.getbbox(text)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        # Calculate position to center the text
        x = (self.width - text_width) // 2
        y = (self.height - text_height) // 2

        # Draw the text
        self.draw.text((x, y), text, fill="white", font=font)

    def draw_text_bottom(self, text, ratio=0.8, padding=20) -> None:
        # Create a temporary font to measure text
        temp_font = self._create_font(100)  # Use a reference size of 100
        text_bbox = temp_font.getbbox(text)
        ref_width = text_bbox[2] - text_bbox[0]
        ref_height = text_bbox[3] - text_bbox[1]

        # Calculate scale factors based on screen dimensions and ratio
        width_scale = (self.width * ratio) / ref_width
        height_scale = (self.height * ratio) / ref_height

        # Use the smaller scale to ensure text fits both dimensions
        font_size = int(min(width_scale, height_scale) * 100)

        # Create the final font with calculated size
        font = self._create_font(font_size)

        # Get final text dimensions
        text_bbox = font.getbbox(text)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        # Calculate position to center horizontally and place at bottom
        x = (self.width - text_width) // 2
        y = self.height - text_height - padding

        # Draw the text
        self.draw.text((x, y), text, fill="white", font=font)

    def draw_text_centered_horizontal(self, text: str, y: int, size: int = 20) -> None:
        """
        Draw text centered horizontally at the specified y position with given font size.

        Args:
            text (str): The text to draw
            y (int): The vertical position (y-coordinate)
            size (int): Font size (default: 20)
        """
        # Create font with specified size
        font = self._create_font(size)

        # Get text dimensions
        text_bbox = font.getbbox(text)
        text_width = text_bbox[2] - text_bbox[0]

        # Calculate x position to center horizontally
        x = (self.width - text_width) // 2

        # Draw the text
        self.draw.text((x, y), text, fill="white", font=font)

    def clear_screen(self, color: tuple = (34, 34, 34)):
        self.draw.rectangle((0, 0, self.width, self.height), fill=color)

    def get_image(self):
        return self.image

    def show(self):
        self.image.show()

    def draw_image(
        self, image_path: str, x: int = 0, y: int = 0, scale: float = 1.0
    ) -> None:
        """
        Load and draw a PNG image at specified coordinates with optional scaling.

        Args:
            image_path (str): Path to the PNG image file
            x (int): X coordinate to draw the image (default: 0)
            y (int): Y coordinate to draw the image (default: 0)
            scale (float): Scale factor for the image (default: 1.0)
        """
        try:
            # Load the image
            img = Image.open(image_path)

            # Apply scaling if needed
            if scale != 1.0:
                new_width = int(img.width * scale)
                new_height = int(img.height * scale)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Convert to RGBA if the image has transparency
            if img.mode == "RGBA":
                # Create a new image with the same size as the main image
                overlay = Image.new("RGBA", self.image.size, (0, 0, 0, 0))
                # Paste the image onto the overlay
                overlay.paste(img, (x, y), img)
                # Convert the main image to RGBA if it isn't already
                if self.image.mode != "RGBA":
                    self.image = self.image.convert("RGBA")
                # Composite the overlay onto the main image
                self.image = Image.alpha_composite(self.image, overlay)
                # Convert back to RGB
                self.image = self.image.convert("RGB")
            else:
                # For non-transparent images, just paste directly
                self.image.paste(img, (x, y))

            # Update the draw object
            self.draw = ImageDraw.Draw(self.image)

        except Exception as e:
            logger.error(f"Failed to draw image {image_path}: {str(e)}")


def get_datetime():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    graphics = Graphics()

    graphics.clear_screen()
    graphics.draw_text_centered_horizontal("25.00°C", 5, 40)
    graphics.draw_image("weather_card.png", 0, 80, 1.0)
    graphics.draw_text(get_datetime(), 34, 205, 24)
    graphics.show()
