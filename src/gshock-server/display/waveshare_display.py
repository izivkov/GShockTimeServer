from display.lib import LCD_1inch3
from display.display import Display
from PIL import Image, ImageDraw
import RPi.GPIO as GPIO

import time

class WaveshareDisplay(Display):
    def __init__(self, width=240, height=240, dc=24, rst=25, bl=18, spi_speed_hz=40000000):
        self.width = width
        self.height = height

        self.disp = LCD_1inch3.LCD_1inch3()
        self.disp.Init()
        self.disp.clear() 
        self.disp.bl_DutyCycle(0)

        self.image = Image.new("RGB", (self.width, self.height), color=0)
        self.black_image = Image.new("RGB", (self.width, self.height), color=0)
        self.draw = ImageDraw.Draw(self.image)

        # New code
        BL_PIN = 18
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(BL_PIN, GPIO.OUT)
        self.pwm = GPIO.PWM(BL_PIN, 1000)
        self.pwm.start(0)  # full brightness (0–100


    def show_status(self, watch_name, battery, temperature, last_sync, alarm, reminder, auto_sync):
        super().show_status(watch_name, battery, temperature, last_sync, alarm, reminder, auto_sync)
        self.disp.ShowImage(self.image)
 
    def set_brightness(self, brightness_level):
        """
        Sets the backlight brightness using PWM.
        brightness_level should be an integer between 0 (off) and 100 (max brightness).
        For a 16-bit PWM (0-65535), we scale the percentage.
        """
        print(f"Setting Brightness to {brightness_level}")
        # self.pwm.ChangeDutyCycle(brightness_level)

        try:
            while True:
                # Fade in (duty cycle from 0 to 100)
                for dc in range(0, 101, 1):
                    self.pwm.ChangeDutyCycle(dc)
                    time.sleep(0.01)

                # Fade out (duty cycle from 100 to 0)
                for dc in range(100, -1, -1):
                    self.pwm.ChangeDutyCycle(dc)
                    time.sleep(0.01)
                    
        except KeyboardInterrupt:
            # Clean up GPIO settings on Ctrl+C exit
            self.pwm.stop()
            GPIO.cleanup()

