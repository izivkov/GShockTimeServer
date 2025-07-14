# display_manager.py

import time

class DisplayManager:
    def __init__(self, display, idle_timeout_secs=300, reset_callback=None):
        """
        :param display: your display object (OLED, LCD, etc.)
        :param idle_timeout_secs: time before screen is considered idle
        :param reset_callback: function to call when timeout is reached
        """
        self.display = display
        self.last_update = 0
        self.idle_timeout_secs = idle_timeout_secs
        self.reset_callback = reset_callback  # e.g., show_welcome_screen()

    def show_if_idle(self, func, *args, **kwargs):
        now = time.time()
        if now - self.last_update > self.idle_timeout_secs:
            func(*args, **kwargs)
            self.last_update = now

    def force_show(self, func, *args, **kwargs):
        func(*args, **kwargs)
        self.last_update = time.time()

    def touch(self):
        self.last_update = time.time()

    def check_timeout_and_reset(self):
        now = time.time()
        if self.reset_callback and (now - self.last_update > self.idle_timeout_secs):
            print("⌛ Screen idle timeout — restoring welcome screen")
            self.reset_callback()
            self.last_update = now  # avoid repeated resets
