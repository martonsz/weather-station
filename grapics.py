import os
import platform
import logging
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)


class Graphics:
    def __init__(self, width: int = 320, height: int = 240):
        self.image = Image.new("RGB", (width, height))
        self.draw = ImageDraw.Draw(self.image)
        self.width = width
        self.height = height
        self.font_path = self._find_font_path()  # Store only the path
        self.font = self._create_font(20)  # Default size

    def _find_font_path(self):
        # Try to find DejaVu Sans font based on the operating system
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

        try:
            return ImageFont.load_default()
        except Exception as e:
            logger.warning(f"Failed to load default font: {str(e)}")
            return ImageFont.truetype(None, size)

    def draw_circle(self):
        circle_radius = 50
        circle_x = self.width // 2
        circle_y = self.height // 2
        left = circle_x - circle_radius
        top = circle_y - circle_radius
        right = circle_x + circle_radius
        bottom = circle_y + circle_radius

        self.draw.ellipse([left, top, right, bottom], fill="blue")

    def draw_text(self, text, x, y, size=20):
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

    def clear_screen(self, color: str = "black"):
        self.draw.rectangle((0, 0, self.width, self.height), fill=color)

    def get_image(self):
        return self.image

    def show(self):
        self.image.show()


if __name__ == "__main__":
    graphics = Graphics()

    graphics.clear_screen()
    # graphics.draw_circle()
    # graphics.draw_text("Hello, World!", 10, 10, 25)
    graphics.draw_text_centerted("25.0°C")
    graphics.show()
