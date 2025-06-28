from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import os

def generate_battery_icon(percent: int, width=20, height=10) -> Image.Image:
    """Generates a battery icon as a 1-bit monochrome image."""
    icon = Image.new("1", (width + 3, height), color=0)
    draw = ImageDraw.Draw(icon)

    # Battery body
    draw.rectangle([0, 0, width - 1, height - 1], outline=1, fill=0)

    # Battery terminal
    terminal_width = 3
    terminal_height = height // 2
    draw.rectangle([width, (height - terminal_height) // 2,
                    width + terminal_width, (height + terminal_height) // 2], fill=1)

    # Fill level
    fill_width = int((width - 2) * max(0, min(percent, 100)) / 100)
    if fill_width > 0:
        draw.rectangle([1, 1, 1 + fill_width - 1, height - 2], fill=1)

    return icon


class MockOLEDDisplay:
    def __init__(self, width=240, height=240, output_file="oled_preview.png"):
        self.width = width
        self.height = height
        self.output_file = output_file
        self.image = Image.new("1", (self.width, self.height), color=0)
        self.draw = ImageDraw.Draw(self.image)

        # Load fonts
        self.font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        self.font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)

    def show_status(self, watch_name, battery, temperature, last_sync, alarm, reminder, auto_sync):
        MARGIN = 4  # margin in pixels around all edges

        # Clear screen
        self.draw.rectangle((0, 0, self.width, self.height), fill=0)

        # Header (centered horizontally, margin from top)
        bbox = self.draw.textbbox((0, 0), watch_name, font=self.font_large)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        self.draw.text(((self.width - w) // 2, MARGIN), watch_name, font=self.font_large, fill=255)

        # Battery level
        battery_level = int(str(battery).strip('%')) if isinstance(battery, str) else int(battery)
        battery_icon = generate_battery_icon(battery_level)
        icon_x = self.width - battery_icon.width - MARGIN
        icon_y = MARGIN
        self.image.paste(battery_icon, (icon_x, icon_y))

        # Temperature below battery icon
        temp_str = f"{temperature}°C"
        bbox_temp = self.draw.textbbox((0, 0), temp_str, font=self.font_small)
        temp_w = bbox_temp[2] - bbox_temp[0]
        self.draw.text((self.width - temp_w - MARGIN, icon_y + battery_icon.height + 2), temp_str, font=self.font_small, fill=255)

        # Info text with top margin
        y = h + MARGIN * 2 + 12 # below header with spacing
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
            self.draw.text((MARGIN, y), label, font=self.font_small, fill=255)
            bbox_val = self.draw.textbbox((0, 0), str_value, font=self.font_small)
            val_w = bbox_val[2] - bbox_val[0]
            self.draw.text((self.width - val_w - MARGIN, y), str_value, font=self.font_small, fill=255)
            y += bbox_val[3] - bbox_val[1] + MARGIN

        # Save image
        self.image.save(self.output_file)
        print(f"🖼 OLED preview saved as '{self.output_file}'")
