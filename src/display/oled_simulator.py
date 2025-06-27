from PIL import Image, ImageDraw, ImageFont
import os

class MockOLEDDisplay:
    def __init__(self, width=128, height=64, output_file="oled_preview.png"):
        self.width = width
        self.height = height
        self.output_file = output_file
        self.image = Image.new("1", (self.width, self.height), color=0)
        self.draw = ImageDraw.Draw(self.image)

        # Load fonts (change path if needed)
        self.font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        self.font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)

    def show_status(self, watch_name, battery, temperature, last_sync, alarm, reminder, auto_sync):
        # Clear screen
        self.draw.rectangle((0, 0, self.width, self.height), fill=0)

        # Header (centered)
        w, h = self.draw.textsize(watch_name, font=self.font_large)
        self.draw.text(((self.width - w) // 2, 0), watch_name, font=self.font_large, fill=255)

        # Status info
        y = 18
        info = [
            ("Battery:", battery),
            ("Temp:", temperature),
            ("Last Sync:", last_sync),
            ("Next Alarm:", alarm),
            ("Reminder:", reminder),
            ("Auto Sync:", auto_sync)
        ]
        for label, value in info:
            self.draw.text((0, y), label, font=self.font_small, fill=255)
            w_val, _ = self.draw.textsize(value, font=self.font_small)
            self.draw.text((self.width - w_val, y), value, font=self.font_small, fill=255)
            y += 12

        # Save as image for inspection
        self.image.save(self.output_file)
        print(f"🖼 OLED preview saved as '{self.output_file}'")

