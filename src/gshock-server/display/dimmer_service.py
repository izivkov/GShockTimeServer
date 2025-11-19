import threading
import time

class DimmerService:
    """
    Auto-dimming and blanking service:
      - 5 minutes: dim to 10%
      - 30 minutes: blank (0%)
    No automatic restore after blanking.
    """
    def __init__(self, display, dim_after=300, blank_after=1800):
        self.display = display
        self.dim_after = dim_after        # default 5 minutes
        self.blank_after = blank_after    # default 30 minutes
        self._stop = False
        self._thread = None
        self._last_activity = time.time()
        self._current_state = "normal"    # normal / dimmed / blanked

    def notify_activity(self):
        """Reset activity timer and restore if blanked/dimmed."""
        self._last_activity = time.time()

    def start(self):
        if self._thread is None:
            self._stop = False
            self._thread = threading.Thread(target=self._loop, daemon=True)
            self._thread.start()

    def stop(self):
        self._stop = True

    def restore_brightness(self, percent=100):
        """External call: restore brightness to given % after blank/dim."""
        self.display.set_brightness(percent)
        self._current_state = "normal"
        self._last_activity = time.time()

    def _loop(self):
        while not self._stop:
            now = time.time()
            elapsed = now - self._last_activity

            # Step 1 → Dim to 10% after 5 min
            if elapsed >= self.dim_after and elapsed < self.blank_after:
                if self._current_state != "dimmed":
                    self.display.set_brightness(10)
                    self._current_state = "dimmed"

            # Step 2 → Blank screen after 30 min
            elif elapsed >= self.blank_after:
                if self._current_state != "blanked":
                    self.display.set_brightness(0)
                    self._current_state = "blanked"

            # Step 0 → User just interacted → should be normal
            else:
                if self._current_state != "normal":
                    # Don't restore brightness automatically, but reset state
                    self._current_state = "normal"

            time.sleep(1)
