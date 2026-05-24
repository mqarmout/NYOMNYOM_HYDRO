import os

# ── Server ──────────────────────────────────────────────────────────────────
SERVER_URL    = os.environ.get("NYOMNYOM_URL", "http://192.168.1.x:5000")
USERNAME      = os.environ.get("NYOMNYOM_USER", "")
PASSWORD      = os.environ.get("NYOMNYOM_PASS", "")
COOKIE_FILE   = os.path.join(os.path.dirname(__file__), ".session_cookie")

# ── Polling intervals ────────────────────────────────────────────────────────
SENSOR_INTERVAL_SEC = 300   # post a new reading every 5 minutes
PUMP_POLL_SEC       = 30    # check pump schedule every 30 seconds

# ── GPIO pin assignments (BCM numbering) ─────────────────────────────────────
# Relay: LOW = pump ON (most relay boards are active-low)
PUMP_RELAY_PIN  = 17

# DHT22 air temperature + humidity
DHT_PIN         = 4

# DS18B20 water temperature (one-wire — kernel handles the pin, usually GPIO 4)
# If using the same pin as DHT, move one of them.
DS18B20_PIN     = 4   # only relevant if manually bit-banging; kernel uses /sys

# HC-SR04 ultrasonic water level
TRIG_PIN        = 23
ECHO_PIN        = 24
# Distance in cm from sensor face to reservoir bottom (measure once, set here)
TANK_DEPTH_CM   = 30.0

# Atlas Scientific EZO (I2C addresses — change if you set custom addresses)
ATLAS_PH_I2C_ADDR  = 0x63
ATLAS_EC_I2C_ADDR  = 0x64
