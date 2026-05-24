"""
Pump relay control.

Wiring: connect the relay signal pin to PUMP_RELAY_PIN (BCM).
Most relay modules are active-low: GPIO LOW turns the relay ON.
If your relay is active-high, swap the LOW/HIGH in _set().
"""
from __future__ import annotations
import time
import logging
from config import PUMP_RELAY_PIN

log = logging.getLogger(__name__)

_gpio_ready = False


def _init_gpio() -> None:
    global _gpio_ready
    if _gpio_ready:
        return
    # TODO: uncomment when relay is wired
    # import RPi.GPIO as GPIO
    # GPIO.setmode(GPIO.BCM)
    # GPIO.setup(PUMP_RELAY_PIN, GPIO.OUT)
    # GPIO.output(PUMP_RELAY_PIN, GPIO.HIGH)  # start with pump OFF (active-low)
    _gpio_ready = True


def _set(on: bool) -> None:
    _init_gpio()
    state = "ON" if on else "OFF"
    log.info(f"[pump] {state}")
    # TODO: uncomment when relay is wired
    # import RPi.GPIO as GPIO
    # GPIO.output(PUMP_RELAY_PIN, GPIO.LOW if on else GPIO.HIGH)


def run_cycle(on_min: int, off_min: int) -> None:
    """Run one pump cycle: on for on_min, then off for off_min."""
    log.info(f"[pump] cycle start: {on_min}min on / {off_min}min off")
    _set(True)
    time.sleep(on_min * 60)
    _set(False)
    time.sleep(off_min * 60)
    log.info("[pump] cycle complete")


def turn_on() -> None:
    _set(True)


def turn_off() -> None:
    _set(False)


def cleanup() -> None:
    turn_off()
    # TODO: uncomment when relay is wired
    # import RPi.GPIO as GPIO
    # GPIO.cleanup()
