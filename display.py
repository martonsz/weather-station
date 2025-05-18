import time
from displayhatmini import DisplayHATMini
from grapics import Graphics


class Display:
    def __init__(self):
        self.width = DisplayHATMini.WIDTH
        self.height = DisplayHATMini.HEIGHT
        self.graphics = Graphics(self.width, self.height)
        self.displayhatmini = DisplayHATMini(
            self.graphics.get_image(), backlight_pwm=True
        )

    def set_led(self, r: float, g: float, b: float):
        self.displayhatmini.set_led(r, g, b)

    def set_backlight(self, brightness: float):
        if brightness >= 0.0 and brightness <= 1.0:
            self.displayhatmini.set_backlight(brightness)

    def display(self):
        self.displayhatmini.display()

    def clear(self):
        self.graphics.clear_screen()


if __name__ == "__main__":
    display = Display()
    display.set_led(0, 0.100, 0)
    display.set_backlight(0.5)
    display.graphics.draw_text_centerted("Adrian Szucs")
    display.display()
    time.sleep(10)
