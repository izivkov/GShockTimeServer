import os

DEBUG = os.getenv("GPIODEVICE_DEBUG", None) is not None


class ErrorDigest(RuntimeError):
    pass


class GPIOBaseError:
    def __init__(self, message: str, icon: str = " "):
        self.icon = icon
        self.message = message

    def __str__(self):
        return f"  {self.icon}  {self.message}"

    def __repr__(self):
        return str(self)


class GPIOError(GPIOBaseError):
    def __init__(self, message: str, icon: str = "⚠️ "):
        GPIOBaseError.__init__(self, message, icon)


class GPIONotFound(GPIOBaseError):
    def __init__(self, message: str, icon: str = "❌"):
        GPIOBaseError.__init__(self, message, icon)


class GPIOFound(GPIOBaseError):
    def __init__(self, message: str, icon: str = "✅"):
        GPIOBaseError.__init__(self, message, icon)


def collect(fn, fatal=False):
    def wrapper(*args, **kwargs):
        errors = []

        i = iter(fn(*args, **kwargs))

        while True:
            try:
                errors.append(next(i))
            except StopIteration as e:
                return e.value
            except ErrorDigest as e:
                msg = f"{e}\n" + "\n".join([str(e) for e in errors])
                if DEBUG:
                    raise RuntimeError(msg) from None
                else:
                    raise SystemExit(f"Woah there, {msg}")

    return wrapper
