def get_name():
    try:
        model = open("/proc/device-tree/model", "r").read()
        if model.startswith("Raspberry Pi"):
            return model
    except IOError:
        pass

    return None


def get_gpiochip_labels():
    if get_name() is not None:
        return (
            "pinctrl-*",
            # "pinctrl-rp1" - Pi 5 - Bookworm, /dev/gpiochip4 maybe
            # "pinctrl-bcm2711" - Pi 4 - Bullseye, /dev/gpiochip0 maybe
            # "pinctrl-bcm2835"
        )

    return None
