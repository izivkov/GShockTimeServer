import glob
import re
import sys
from pathlib import Path

import gpiod

from . import errors, platform

__version__ = "0.0.5"


CHIP_GLOB = "/dev/gpiochip*"


# Deprecated
friendly_errors: bool = False


@errors.collect
def check_pins_available(chip: gpiod.Chip, pins, fatal: bool = True) -> bool:
    """Check if a list of pins are in use on a given gpiochip device.

    If any pins are used: raises a helpful list of pins and their consumer if fatal == True, otherwise returns False.

    """
    if pins is None:
        return True

    used = 0

    for label, pin in pins.items():
        if isinstance(pin, str):
            try:
                pin = chip.line_offset_from_id(pin)
            except OSError:
                yield errors.GPIOError(f"{label}: (line {pin}) not found!")
                continue

        line_info = chip.get_line_info(pin)

        if line_info.used:
            used += 1
            yield errors.GPIOError(f"{label}: (line {pin}, {line_info.name}) currently claimed by {line_info.consumer}")

    if used and fatal:
        raise errors.ErrorDigest("some pins we need are in use!")

    return used == 0


@errors.collect
def find_chip_by_label(labels: (list[str], tuple[str], str), pins: dict[str, (int, str)] = None, fatal: bool = True):
    """Try to find a gpiochip device matching one of a set of labels.

    Raise a RuntimeError with a friendly error digest if one is not found.

    If no suitable gpiochip is found: raises a helpful digest of errors if fatal == True, otherwise returns None.

    """
    if isinstance(labels, str):
        labels = (labels,)

    for path in glob.glob(CHIP_GLOB):
        if gpiod.is_gpiochip_device(path):
            try:
                label = gpiod.Chip(path).get_info().label
            except PermissionError:
                yield errors.GPIOError(f"{path}: Permission error!")
                continue

            if re.match("|".join(labels), label):
                chip = gpiod.Chip(path)
                if check_pins_available(chip, pins):
                    return chip
            else:
                yield errors.GPIONotFound(f"{path}: this is not the GPIO we're looking for! ({label})")

    if fatal:
        raise errors.ErrorDigest("suitable gpiochip device not found!")

    return None


@errors.collect
def find_chip_by_pins(pins: (list[str], tuple[str], str), ignore_claimed: bool = False, fatal: bool = True):
    """Try to find a gpiochip device that includes all of the named pins.

    Does not care whether pins are in use or not.

    "pins" can be a single string, a list/tuple or a comma-separated string of names.

    If no suitable gpiochip is found: raises a helpful digest of errors if fatal == True, otherwise returns None.

    """
    if isinstance(pins, int):
        pins = (pins,)

    if isinstance(pins, str):
        if "," in pins:
            pins = [pin.strip() for pin in pins.split(",")]
        else:
            pins = (pins,)

    for path in glob.glob(CHIP_GLOB):
        if gpiod.is_gpiochip_device(path):
            try:
                chip = gpiod.Chip(path)
            except PermissionError:
                yield errors.GPIOError(f"{path}: Permission error!")
                continue

            label = chip.get_info().label
            failed = False

            for pin_id in pins:
                if isinstance(pin_id, int):
                    failed = True
                    yield errors.GPIOError(f'{path}: {pin_id} is an int and has been skipped, did you mean "PIN{pin_id}" or "GPIO{pin_id}"?')
                    continue

                try:
                    offset = chip.line_offset_from_id(pin_id)
                    yield errors.GPIOFound(f"{pin_id}: (line {offset}) found - {path} ({label})!")
                except OSError:
                    failed = True
                    yield errors.GPIONotFound(f"{pin_id}: not found - {path} ({label})!")
                    continue

                line_info = chip.get_line_info(offset)

                if not ignore_claimed and line_info.used:
                    failed = True
                    yield errors.GPIOError(f"{pin_id}: (line {offset}, {line_info.name}) currently claimed by {line_info.consumer}")

            if not failed:
                return chip

    if fatal:
        raise errors.ErrorDigest("suitable gpiochip not found!")

    return None


def find_chip_by_platform():
    labels = platform.get_gpiochip_labels()
    return find_chip_by_label(labels)


def get_pin(pin, label, settings):
    # Do nothing if given a user specified LineRequest/offset tuple
    if isinstance(pin, tuple):
        return pin

    if isinstance(pin, int):
        chip = find_chip_by_platform()
        line_offset = pin
    else:
        chip = find_chip_by_pins(pin)
        line_offset = chip.line_offset_from_id(pin)

    consumer = Path(sys.argv[0]).stem
    lines = chip.request_lines(consumer=f"{consumer}-{label}", config={line_offset: settings})
    return lines, line_offset


def get_pins_for_platform(platforms):
    this_platform = platform.get_name()

    result = []

    for check_platform, pins in platforms.items():
        if this_platform.startswith(check_platform):
            for user_label, (pin, settings) in pins.items():
                result.append(get_pin(pin, user_label, settings))

    return result
