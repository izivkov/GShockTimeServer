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
        MARGIN = 8  # margin in pixels around all edges
        BOX_PADDING = 8  # extra padding inside the battery/temperature box

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
        temp_h = bbox_temp[3] - bbox_temp[1]
        temp_x = self.width - temp_w - MARGIN
        temp_y = icon_y + battery_icon.height + 2
        self.draw.text((temp_x, temp_y), temp_str, font=self.font_small, fill=255)

        # Draw rectangle around battery icon and temperature with padding
        rect_left = min(icon_x, temp_x) - BOX_PADDING
        rect_top = icon_y - BOX_PADDING
        rect_right = self.width - MARGIN + BOX_PADDING - 1
        rect_bottom = temp_y + temp_h + BOX_PADDING
        self.draw.rectangle(
            [rect_left, rect_top, rect_right, rect_bottom],
            outline=255,
            width=1
        )

        # Info text with top margin
        y = h + MARGIN * 2 + 12 + 10 # below header with spacing
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

        # Draw a small watch icon at the bottom right in blue and yellow
        icon_size = 24
        watch_x = self.width - icon_size - MARGIN
        watch_y = self.height - icon_size - MARGIN

        # Create a small RGB image for the watch icon
        watch_icon = Image.new("RGB", (icon_size, icon_size), (0, 0, 0))
        icon_draw = ImageDraw.Draw(watch_icon)

        # Draw watch body (blue circle)
        icon_draw.ellipse(
            [2, 2, icon_size - 3, icon_size - 3],
            outline=(0, 0, 255),
            fill=(0, 0, 255)
        )

        # Draw watch face (yellow circle)
        icon_draw.ellipse(
            [6, 6, icon_size - 7, icon_size - 7],
            outline=(255, 255, 0),
            fill=(255, 255, 0)
        )

        # Draw watch hands (blue)
        center = icon_size // 2
        icon_draw.line(
            [center, center, center, center - 6],
            fill=(0, 0, 255),
            width=2
        )
        icon_draw.line(
            [center, center, center + 5, center],
            fill=(0, 0, 255),
            width=2
        )

        # Convert to 1-bit if needed, or paste as RGB
        self.image.paste(watch_icon.convert("1"), (watch_x, watch_y))

        # Save image
        self.image.save(self.output_file)
        print(f"🖼 OLED preview saved as '{self.output_file}'")

    def show_status_short(self, watch_name, battery, temperature, last_sync, alarm, reminder, auto_sync):
        """Short version of show_status for smaller displays."""
        self.show_status(
            watch_name=watch_name,
            battery=battery,
            temperature=temperature,
            last_sync=last_sync,
            alarm=alarm,
            reminder=reminder,
            auto_sync=auto_sync
        )
