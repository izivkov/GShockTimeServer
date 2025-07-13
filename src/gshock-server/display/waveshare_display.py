from display.lib import LCD_1inch3
from display.display import Display
from PIL import Image, ImageDraw

class WaveshareDisplay(Display):
    def __init__(self, width=240, height=240, dc=24, rst=25, bl=18, spi_speed_hz=40000000):
        self.width = width
        self.height = height

        self.disp = LCD_1inch3.LCD_1inch3()
        self.disp.Init()
        self.disp.clear() 
        self.disp.bl_DutyCycle(10)

        self.image = Image.new("RGB", (self.width, self.height), color=0)
        self.draw = ImageDraw.Draw(self.image)

    def show_status(self, watch_name, battery, temperature, last_sync, alarm, reminder, auto_sync):
        super().show_status(watch_name, battery, temperature, last_sync, alarm, reminder, auto_sync)

        self.disp.ShowImage(self.image)
 