from email.mime import message
from luma.core.interface.serial import spi
from luma.lcd.device import st7789

from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from gshock_api.logger import logger

font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
font_extra_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)

def generate_battery_icon(percent: int, width=20, height=10) -> Image.Image:
    """Generates a battery icon as a color image for preview.
    The full part is white, the empty part is black."""
    icon = Image.new("RGB", (width + 3, height), color=(0, 0, 0))  # Black background
    draw = ImageDraw.Draw(icon)
    # Battery outline.
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

from PIL import Image, ImageDraw, ImageFont

def show_welcome_screen(self, message, watch_name=None, last_sync=None):
    """
    Display a multi-line message at the bottom of the screen over a background image.
    If watch_name and last_sync are provided, they appear above the message.
    All lines are horizontally centered.
    """
    # font = self.font_extra_large if hasattr(self, 'font_extra_large') else ImageFont.load_default()
    font = font_small
    margin = 5  # Bottom margin in pixels
    line_spacing = 4  # Pixels between lines

    # Load background image
    try:
        img_path = "gshock-server-dist/display/pic/dw-b5600.png" if hasattr(self, 'output_file') \
            else "display/pic/dw-b5600.png"

        logger.info (f"img_path: {img_path}")
        import os
        cwd = os.getcwd()
        logger.info("Current working directory:", cwd)

        image = Image.open(img_path).convert("RGB").resize((self.width, self.height))
    except FileNotFoundError:
        print(f"❌ Background image '{img_path}' not found. Using black fallback.")
        image = Image.new("RGB", (self.width, self.height), "BLACK")

    draw = ImageDraw.Draw(image)

    # Compose all lines to be displayed
    lines = []

    if watch_name is not None:
        lines.append(f"Watch: {watch_name}")
    if last_sync is not None:
        lines.append(f"Last sync: {last_sync}")
    
    # Split the main message into lines and add
    message_lines = message.strip().split('\n')
    lines.extend(message_lines)

    # Measure each line's size
    line_sizes = [draw.textbbox((0, 0), line, font=font) for line in lines]
    line_widths = [bbox[2] - bbox[0] for bbox in line_sizes]
    line_heights = [bbox[3] - bbox[1] for bbox in line_sizes]

    total_text_height = sum(line_heights) + line_spacing * (len(lines) - 1)

    # Compute vertical starting point (bottom-aligned)
    start_y = self.height - total_text_height - margin

    # Draw all lines centered
    y = start_y
    for i, line in enumerate(lines):
        text_w = line_widths[i]
        text_h = line_heights[i]
        x = (self.width - text_w) // 2
        draw.text((x, y), line, font=font, fill=(255, 255, 255))
        y += text_h + line_spacing

    # Display the image
    if hasattr(self, "disp") and hasattr(self.disp, "ShowImage"):
        self.disp.ShowImage(image)
    elif hasattr(self, "device") and hasattr(self.device, "display"):
        self.device.display(image)
    elif hasattr(self, "output_file"):
        image.save(self.output_file)

    # Save for use in overlays (e.g., blinking dot)
    self.last_image = image.copy()

def draw_status(draw, image, width, height, font_large, font_small,
                watch_name, battery, temperature, last_sync, alarm, reminder, auto_sync,
                margin=8):

    # Header (centered at the top)
    bbox = draw.textbbox((0, 0), watch_name, font=font_large)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((width - w) // 2, margin), watch_name, font=font_large, fill=(255, 255, 255))

    # Temperature string — draw it at bottom-left
    temp_str = f"{temperature}°C"
    bbox_temp = draw.textbbox((0, 0), temp_str, font=font_small)
    temp_w = bbox_temp[2] - bbox_temp[0]
    temp_h = bbox_temp[3] - bbox_temp[1]
    temp_x = margin
    temp_y = height - temp_h - margin
    draw.text((temp_x, temp_y), temp_str, font=font_small, fill=(255, 255, 255))

    # Battery icon — make it longer (wider horizontally)
    battery_level = int(str(battery).strip('%')) if isinstance(battery, str) else int(battery)
    battery_icon = generate_battery_icon(battery_level)

    # Stretch battery icon width-wise (1.8x) and height-wise slightly (1.3x)
    scale_x = 1.5
    scale_y = 1.5
    new_size = (int(battery_icon.width * scale_x), int(battery_icon.height * scale_y))
    battery_icon = battery_icon.resize(new_size, Image.LANCZOS)

    # Position battery icon at bottom-right
    icon_x = width - battery_icon.width - margin
    icon_y = height - battery_icon.height - margin
    image.paste(battery_icon, (icon_x, icon_y))

    # Info text (middle of screen, below header)
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
        val_h = bbox_val[3] - bbox_val[1]
        draw.text((width - val_w - margin, y), str_value, font=font_small, fill=(255, 255, 255))
        y += val_h + margin
            
class Display:
    def __init__(self, draw, image, width=240, height=240):
        self.draw = draw
        self.image = image
        self.width = width
        self.height = height

    def show_status(self, watch_name, battery, temperature, last_sync, alarm, reminder, auto_sync):
        MARGIN = 8  # margin in pixels around all edges

        # Clear screen
        self.draw.rectangle((0, 0, self.width, self.height), fill=0)

        # Use the shared drawing function
        draw_status(
            self.draw, self.image, self.width, self.height,
            font_large, font_small,
            watch_name, battery, temperature, last_sync, alarm, reminder, auto_sync,
            margin=MARGIN
        )

        return self.image

    def show_welcome_screen(self, message, watch_name=None, last_sync=None):
        show_welcome_screen(self, message, watch_name, last_sync)
