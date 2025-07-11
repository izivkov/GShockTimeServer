from luma.core.interface.serial import spi
from luma.lcd.device import st7789

from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

import serial

def generate_battery_icon(percent: int, width=20, height=10) -> Image.Image:
    """Generates a battery icon as a color image for preview.
    The full part is white, the empty part is black."""
    icon = Image.new("RGB", (width + 3, height), color=(0, 0, 0))  # Black background
    draw = ImageDraw.Draw(icon)
    # Battery outline
    draw.rectangle([0, 0, width - 1, height - 1], outline=(255, 255, 255), fill=None)
    # Battery terminal
    terminal_width = 3
    terminal_height = height // 2
    draw.rectangle([width, (height - terminal_height) // 2,
                    width + terminal_width, (height + terminal_height) // 2], fill=(255, 255, 255))
    # Battery fill (white for full, black for empty)
    fill_width = int((width - 2) * max(0, min(percent, 100)) / 100)
    if fill_width > 0:
        draw.rectangle([1, 1, 1 + fill_width - 1, height - 2], fill=(255, 255, 255))
    if fill_width < (width - 2):
        draw.rectangle([1 + fill_width, 1, width - 2, height - 2], fill=(0, 0, 0))
    return icon

# Common function to draw OLED status
def draw_oled_status(draw, image, width, height, font_large, font_small,
                     watch_name, battery, temperature, last_sync, alarm, reminder, auto_sync,
                     margin=8, box_padding=8):
    
    # Header (centered horizontally, margin from top)
    bbox = draw.textbbox((0, 0), watch_name, font=font_large)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((width - w) // 2, margin), watch_name, font=font_large, fill=(255, 255, 255))

    # Battery level
    battery_level = int(str(battery).strip('%')) if isinstance(battery, str) else int(battery)
    battery_icon = generate_battery_icon(battery_level)
    icon_x = width - battery_icon.width - margin
    icon_y = margin
    image.paste(battery_icon, (icon_x, icon_y))

    # Temperature below battery icon
    temp_str = f"{temperature}°C"
    bbox_temp = draw.textbbox((0, 0), temp_str, font=font_small)
    temp_w = bbox_temp[2] - bbox_temp[0]
    temp_h = bbox_temp[3] - bbox_temp[1]
    temp_x = width - temp_w - margin
    temp_y = icon_y + battery_icon.height + 2
    draw.text((temp_x, temp_y), temp_str, font=font_small, fill=(255, 255, 255))

    # Draw rectangle around battery icon and temperature with padding
    rect_left = min(icon_x, temp_x) - box_padding
    rect_top = icon_y - box_padding
    rect_right = width - margin + box_padding - 1
    rect_bottom = temp_y + temp_h + box_padding
    draw.rectangle(
        [rect_left, rect_top, rect_right, rect_bottom],
        outline=255,
        width=1
    )

    # Info text with top margin
    y = h + margin * 2 + 12 + 10

    if isinstance(last_sync, datetime):
        delta = datetime.now() - last_sync
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        last_sync_str = f"{hours:02}:{minutes:02} since sync"
    else:
        last_sync_str = str(last_sync).strip() if last_sync else ""

    info = [
        ("Last Sync:", last_sync_str),
        ("Next Alarm:", alarm),
        ("Rem:", reminder),
        ("Auto Sync:", auto_sync)
    ]

    for label, value in info:
        str_value = str(value).strip() if value is not None else ""
        draw.text((margin, y), label, font=font_small, fill=(255, 255, 255))
        bbox_val = draw.textbbox((0, 0), str_value, font=font_small)
        val_w = bbox_val[2] - bbox_val[0]
        draw.text((width - val_w - margin, y), str_value, font=font_small, fill=(255, 255, 255))
        y += bbox_val[3] - bbox_val[1] + margin
    
class OLEDDisplay:
    def __init__(self, width=240, height=240, i2c_port=1, i2c_address=0x3C):
        self.width = width
        self.height = height
        # serial = i2c(port=i2c_port, address=i2c_address)
        # self.device = ssd1306(serial, width=self.width, height=self.height)
        serial = spi(port=0, device=0, gpio_DC=24, gpio_RST=25)
        self.device = st7789(serial, width=240, height=240, rotate=0)

        self.font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        self.font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)

    def show_status(self, watch_name, battery, temperature, last_sync, alarm, reminder, auto_sync):
        MARGIN = 8  # margin in pixels around all edges
        BOX_PADDING = 8  # extra padding inside the battery/temperature box

        # Create a new image for each update.
        image = Image.new("RGB", (self.width, self.height), color=0)
        draw = ImageDraw.Draw(image)

        # Use the shared drawing function
        draw_oled_status(
            draw, image, self.width, self.height,
            self.font_large, self.font_small,
            watch_name, battery, temperature, last_sync, alarm, reminder, auto_sync,
            margin=MARGIN, box_padding=BOX_PADDING
        )

        # Display on the real OLED
        self.device.display(image)

class MockOLEDDisplay:
    def __init__(self, width=240, height=240, output_file="oled_preview.png"):
        self.width = width
        self.height = height
        self.output_file = output_file
        self.image = Image.new("RGB", (self.width, self.height), color=0)
        self.draw = ImageDraw.Draw(self.image)

        # Load fonts
        self.font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        self.font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)

    def show_status(self, watch_name, battery, temperature, last_sync, alarm, reminder, auto_sync):
        MARGIN = 8  # margin in pixels around all edges
        BOX_PADDING = 8  # extra padding inside the battery/temperature box

        # Clear screen
        self.draw.rectangle((0, 0, self.width, self.height), fill=0)

        # Use the shared drawing function
        draw_oled_status(
            self.draw, self.image, self.width, self.height,
            self.font_large, self.font_small,
            watch_name, battery, temperature, last_sync, alarm, reminder, auto_sync,
            margin=MARGIN, box_padding=BOX_PADDING
        )

        # Save image
        self.image.save(self.output_file)
        print(f"🖼 OLED preview saved as '{self.output_file}'.")

import RPi.GPIO as GPIO
from .oled_simulator import draw_oled_status


from display.lib import LCD_1inch3
import time

class WaveshareDisplay:
    def __init__(self, width=240, height=240, dc=24, rst=25, bl=18, spi_speed_hz=40000000):
        self.width = width
        self.height = height

        self.font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        self.font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)

        self.disp = LCD_1inch3.LCD_1inch3()
        self.disp.Init()
        self.disp.clear() 
        self.disp.bl_DutyCycle(10)

    def show_status(self, watch_name, battery, temperature, last_sync, alarm, reminder, auto_sync):

        MARGIN = 8
        BOX_PADDING = 8
        image = Image.new("RGB", (self.width, self.height), "BLACK")
        draw = ImageDraw.Draw(image)
        draw_oled_status(
            draw, image, self.width, self.height,
            self.font_large, self.font_small,
            watch_name, battery, temperature, last_sync, alarm, reminder, auto_sync,
            margin=MARGIN, box_padding=BOX_PADDING
        )
        self.disp.ShowImage(image)
