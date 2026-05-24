"""
Sensor reading functions — all stubbed until hardware is wired.

Recommended hardware for each metric
─────────────────────────────────────────────────────────────────────────────
pH           Atlas Scientific EZO pH circuit (I2C)           ~$50
             Budget: Gravity analog pH sensor + ADS1115 ADC  ~$15
EC (ppm)     Atlas Scientific EZO EC circuit (I2C)           ~$50
             Budget: Gravity TDS sensor + ADS1115 ADC        ~$10
Water temp   DS18B20 waterproof probe (one-wire via GPIO 4)  ~$5
Water level  HC-SR04 ultrasonic sensor above reservoir       ~$3
Air temp     DHT22 (single GPIO pin)                         ~$5
Humidity     DHT22 (same chip as air temp)                   included above

Atlas EZO circuits are the best choice for pH and EC — they handle
temperature compensation, calibration storage, and give stable I2C readings.
If budget is a concern, the Gravity analog sensors work but need an ADC chip
(ADS1115 is easy to use via I2C) and manual calibration.

All functions return None when hardware is not available, so the server
accepts partial readings gracefully.
"""
from __future__ import annotations
from config import TANK_DEPTH_CM, ATLAS_PH_I2C_ADDR, ATLAS_EC_I2C_ADDR, DHT_PIN, TRIG_PIN, ECHO_PIN

# ── pH ───────────────────────────────────────────────────────────────────────

def read_ph() -> float | None:
    """Return pH value (e.g. 6.2). Target range: 5.5–6.5."""
    # TODO: uncomment when Atlas EZO pH is wired via I2C
    # import smbus2, time
    # bus = smbus2.SMBus(1)
    # bus.write_i2c_block_data(ATLAS_PH_I2C_ADDR, 0, list(b'R\00'))
    # time.sleep(0.9)
    # data = bus.read_i2c_block_data(ATLAS_PH_I2C_ADDR, 0, 7)
    # return float(bytes(data[1:]).split(b'\x00')[0])
    return None


# ── EC (ppm) ─────────────────────────────────────────────────────────────────

def read_ec_ppm() -> float | None:
    """Return EC in ppm (µS/cm × 0.5 conversion). Target: 800–1400 ppm for most crops."""
    # TODO: uncomment when Atlas EZO EC is wired via I2C
    # import smbus2, time
    # bus = smbus2.SMBus(1)
    # bus.write_i2c_block_data(ATLAS_EC_I2C_ADDR, 0, list(b'R\00'))
    # time.sleep(0.6)
    # data = bus.read_i2c_block_data(ATLAS_EC_I2C_ADDR, 0, 10)
    # ec_us = float(bytes(data[1:]).split(b'\x00')[0])
    # return ec_us * 0.5   # convert µS/cm → ppm (500 scale)
    return None


# ── Water temperature ────────────────────────────────────────────────────────

def read_water_temp() -> float | None:
    """Return water temperature in °C. Target: 18–24°C."""
    # TODO: uncomment when DS18B20 is wired (requires w1-gpio + w1-therm kernel modules)
    # The kernel exposes the reading at /sys/bus/w1/devices/28-*/w1_slave
    # import glob
    # files = glob.glob('/sys/bus/w1/devices/28-*/w1_slave')
    # if not files:
    #     return None
    # with open(files[0]) as f:
    #     lines = f.readlines()
    # if lines[0].strip()[-3:] != 'YES':
    #     return None
    # temp_raw = lines[1].split('t=')[1]
    # return float(temp_raw) / 1000.0
    return None


# ── Water level ──────────────────────────────────────────────────────────────

def read_water_level_pct() -> float | None:
    """
    Return reservoir fill level as a percentage (0–100).
    Uses HC-SR04 ultrasonic sensor mounted above the reservoir.
    Measures distance to water surface; calculates fill % from TANK_DEPTH_CM.
    """
    # TODO: uncomment when HC-SR04 is wired to TRIG_PIN / ECHO_PIN
    # import RPi.GPIO as GPIO, time
    # GPIO.setmode(GPIO.BCM)
    # GPIO.setup(TRIG_PIN, GPIO.OUT)
    # GPIO.setup(ECHO_PIN, GPIO.IN)
    # GPIO.output(TRIG_PIN, False)
    # time.sleep(0.1)
    # GPIO.output(TRIG_PIN, True)
    # time.sleep(0.00001)
    # GPIO.output(TRIG_PIN, False)
    # pulse_start = pulse_end = time.time()
    # while GPIO.input(ECHO_PIN) == 0:
    #     pulse_start = time.time()
    # while GPIO.input(ECHO_PIN) == 1:
    #     pulse_end = time.time()
    # distance_cm = (pulse_end - pulse_start) * 17150  # speed of sound / 2
    # GPIO.cleanup()
    # fill_cm = TANK_DEPTH_CM - distance_cm
    # return max(0.0, min(100.0, (fill_cm / TANK_DEPTH_CM) * 100))
    return None


# ── Air temperature + humidity ───────────────────────────────────────────────

def read_air_temp_humidity() -> tuple[float | None, float | None]:
    """Return (air_temp_celsius, humidity_percent). Uses DHT22."""
    # TODO: uncomment when DHT22 is wired to DHT_PIN
    # pip install adafruit-circuitpython-dht
    # import adafruit_dht, board
    # dht = adafruit_dht.DHT22(getattr(board, f'D{DHT_PIN}'))
    # try:
    #     return dht.temperature, dht.humidity
    # except RuntimeError:
    #     return None, None
    return None, None


# ── Convenience: read everything at once ─────────────────────────────────────

def read_all() -> dict:
    air_temp, humidity = read_air_temp_humidity()
    return {
        "ph":          read_ph(),
        "ec_ppm":      read_ec_ppm(),
        "water_temp":  read_water_temp(),
        "water_level": read_water_level_pct(),
        "air_temp":    air_temp,
        "humidity":    humidity,
    }
