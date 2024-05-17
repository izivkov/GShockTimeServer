from configparser import ConfigParser


class Configurator:
    def __init__(self) -> None:
        self.config = ConfigParser()
        if not self.config.has_section("main"):
            self.config.add_section("main")

    def get(self, key):
        self.config.read("config.ini")

        try:
            value = self.config.get("main", key)
        except Exception:
            return None
        else:
            return value

    def put(self, key, value):
        self.config.set("main", key, value)

        with open("config.ini", "w") as f:
            self.config.write(f)


conf = Configurator()
