from PIL import Image, ImageDraw
from display.display import Display

class MockDisplay(Display):
    def __init__(self, width=240, height=240, output_file="oled_preview.png"):
        self.width = width
        self.height = height
        self.output_file = output_file
        self.image = Image.new("RGB", (self.width, self.height), color=0)
        self.draw = ImageDraw.Draw(self.image)

    def show_status(self, watch_name, battery, temperature, last_sync, alarm, reminder, auto_sync):
        image = super().show_status(self, watch_name, battery, temperature, last_sync, alarm, reminder, auto_sync)

        # Save image
        self.image.save(self.output_file)
        print(f"🖼 OLED preview saved as '{self.output_file}'.")

