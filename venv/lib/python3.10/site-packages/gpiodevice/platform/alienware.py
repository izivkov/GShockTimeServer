def get_name():
    try:
        model = open("/sys/devices/virtual/dmi/id/board_name", "r").read()
        if model.startswith("Alienware m15"):
            return model
    except IOError:
        pass

    return None


def get_gpiochip_labels():
    if get_name() is not None:
        return ("INT3450:00",)

    return None
