def get_name():
    try:
        model = open("/proc/device-tree/model", "r").read()
        if model.startswith("Radxa"):
            return model
    except IOError:
        pass

    return None


def get_gpiochip_labels():
    # Assuming all Radxa boards have five gpiochips
    # https://wiki.radxa.com/Rock4/hardware/gpio
    # https://wiki.radxa.com/Rock5/hardware/5b/gpio
    if get_name() is not None:
        return (
            "gpio0",
            "gpio1",
            "gpio2",
            "gpio3",
            "gpio4",
        )

    return None
