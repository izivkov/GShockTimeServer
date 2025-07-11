from luma.core.interface.serial import spi
from luma.lcd.device import st7789
from PIL import Image, ImageDraw, ImageFont
import time

# Init display (adjust DC and RST pins if needed)
serial = spi(port=0, device=0, gpio_DC=24, gpio_RST=25)
device = st7789(serial, width=240, height=240, rotate=0)

# Create blank image
image = Image.new("RGB", (240, 240), "black")
draw = ImageDraw.Draw(image)

# Draw text
draw.text((30, 20), "Hello LCD!", fill="white")

# Draw rectangles
draw.rectangle([10, 60, 100, 120], outline="yellow", width=3)
draw.rectangle([120, 60, 220, 120], fill="blue", outline="white", width=2)

# Draw ellipse
draw.ellipse([60, 140, 180, 220], outline="red", fill="green")

# Draw lines
draw.line([0, 0, 239, 239], fill="cyan", width=2)
draw.line([0, 239, 239, 0], fill="magenta", width=2)

# Draw with a custom font (if available)
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    draw.text((20, 200), "Custom Font!", font=font, fill="orange")
except Exception:
    draw.text((20, 200), "No font found", fill="orange")

# Display it
device.display(image)

time.sleep(5)  # Keep it on for 5 seconds
