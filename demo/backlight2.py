#!/usr/bin/env python3
import time
import RPi.GPIO as GPIO  # Explicitly import GPIO
from displayhatmini import DisplayHATMini
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("""This example requires PIL/Pillow, try:
sudo apt install python3-pil
""")

# First, make sure no conflicting GPIO setup exists
GPIO.setwarnings(False)  # Suppress warnings about channels already in use
GPIO.cleanup()  # Clean up any previous GPIO configurations

width = DisplayHATMini.WIDTH
height = DisplayHATMini.HEIGHT
buffer = Image.new("RGB", (width, height))
draw = ImageDraw.Draw(buffer)
font = ImageFont.load_default()
displayhatmini = DisplayHATMini(buffer, backlight_pwm=True)
displayhatmini.set_led(0.05, 0.05, 0.05)
brightness = 1.0

# Plumbing to convert Display HAT Mini button presses into pygame events
def button_callback(pin):
    global brightness
    # Only handle presses
    if not displayhatmini.read_button(pin):
        return
    if pin == displayhatmini.BUTTON_A:
        brightness += 0.1
        brightness = min(1, brightness)
    if pin == displayhatmini.BUTTON_B:
        brightness -= 0.1
        brightness = max(0, brightness)

# Try setting up button callbacks with error handling
try:
    displayhatmini.on_button_pressed(button_callback)
except RuntimeError as e:
    print(f"Error setting up button callback: {e}")
    print("Try running the script with sudo permissions")
    # Fall back to polling buttons instead of events
    use_polling = True
else:
    use_polling = False

draw.rectangle((0, 0, width, height), (255, 255, 255))
draw.text((10, 70), "Backlight Up", font=font, fill=(0, 0, 0))
draw.text((10, 160), "Backlight Down", font=font, fill=(0, 0, 0))

# Previous button states for polling method
prev_button_a = False
prev_button_b = False

while True:
    displayhatmini.display()
    displayhatmini.set_backlight(brightness)
    
    # If event detection failed, fall back to polling
    if use_polling:
        # Read current button states
        button_a = displayhatmini.read_button(displayhatmini.BUTTON_A)
        button_b = displayhatmini.read_button(displayhatmini.BUTTON_B)
        
        # Check for button A press (transition from not pressed to pressed)
        if button_a and not prev_button_a:
            brightness += 0.1
            brightness = min(1, brightness)
            
        # Check for button B press
        if button_b and not prev_button_b:
            brightness -= 0.1
            brightness = max(0, brightness)
            
        # Update previous states
        prev_button_a = button_a
        prev_button_b = button_b
    
    time.sleep(1.0 / 30)
