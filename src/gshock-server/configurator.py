import os
from configparser import ConfigParser

class Configurator:
    def __init__(self, path=None) -> None:
        default_dir = os.path.join(os.path.expanduser("~"), ".config", "gshock")
        default_path = os.path.join(default_dir, "config.ini")

        self.path = path or default_path

        # Ensure directory exists
        os.makedirs(os.path.dirname(self.path), exist_ok=True)

        self.config = ConfigParser()

        # Load existing file if present
        if os.path.exists(self.path):
            self.config.read(self.path)

        if not self.config.has_section("main"):
            self.config.add_section("main")
            self._save()

    def get(self, key):
        self.config.read(self.path)
        try:
            return self.config.get("main", key)
        except Exception:
            return None

    def set(self, key, value):
        self.config.set("main", key, value)
        self._save()

    def _save(self):
        with open(self.path, "w") as f:
            self.config.write(f)

conf = Configurator()
