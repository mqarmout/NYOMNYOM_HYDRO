# NYOMNYOM Hydro — Raspberry Pi

Pi-side scripts for the NYOMNYOM hydroponics tower. Reads sensors, POSTs data
to the NYOMNYOM server, and controls the water pump via a relay.

The server-side API lives in `nyomnyom_server/routes/hydro.py`.

## Hardware shopping list

| Metric | Recommended part | Budget alternative | ~Price |
|---|---|---|---|
| pH | Atlas Scientific EZO pH (I2C) | Gravity analog pH + ADS1115 ADC | $50 / $15 |
| EC (ppm) | Atlas Scientific EZO EC (I2C) | Gravity TDS sensor + ADS1115 ADC | $50 / $10 |
| Water temp | DS18B20 waterproof probe (one-wire) | — | $5 |
| Water level | HC-SR04 ultrasonic (above reservoir) | Float switch | $3 |
| Air temp + humidity | DHT22 | BME280 (I2C, also has pressure) | $5 |
| Pump relay | 5V single-channel relay module | — | $3 |

**Atlas Scientific** circuits are strongly recommended for pH and EC — they
handle temperature compensation and save calibration internally, which matters
a lot for accurate readings in nutrient solution.

## Wiring

```
Pi GPIO (BCM) → component
──────────────────────────
GPIO 4        → DS18B20 data (+ 4.7k pull-up to 3.3V)
GPIO 4        → DHT22 data (move one if sharing pin — use GPIO 27 for DHT)
GPIO 17       → Relay signal (pump)
GPIO 23       → HC-SR04 TRIG
GPIO 24       → HC-SR04 ECHO (use voltage divider: 1k + 2k to 3.3V)
I2C SDA/SCL   → Atlas EZO pH (addr 0x63) + EZO EC (addr 0x64) + ADS1115
```

Enable I2C and one-wire on the Pi:
```bash
sudo raspi-config   # Interface Options → I2C → Enable
                    # Interface Options → 1-Wire → Enable
sudo reboot
```

## Setup

```bash
git clone https://github.com/mqarmout/NYOMNYOM_HYDRO.git
cd NYOMNYOM_HYDRO
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

cp .env.example .env
# edit .env — set NYOMNYOM_URL to your server's LAN IP, add credentials
```

## Running

```bash
source .env && .venv/bin/python main.py
```

Or run as a systemd service so it starts on boot:

```ini
# /etc/systemd/system/nyomnyom-hydro.service
[Unit]
Description=NYOMNYOM Hydro sensor loop
After=network-online.target
Wants=network-online.target

[Service]
User=pi
WorkingDirectory=/home/pi/NYOMNYOM_HYDRO
EnvironmentFile=/home/pi/NYOMNYOM_HYDRO/.env
ExecStart=/home/pi/NYOMNYOM_HYDRO/.venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable nyomnyom-hydro
sudo systemctl start  nyomnyom-hydro
sudo journalctl -fu   nyomnyom-hydro
```

## Configuration

Edit `config.py` to set GPIO pin numbers and polling intervals. All sensor
functions are in `sensors.py` — each one has a stub with commented-out
hardware code ready to uncomment as you add components.

## File overview

```
nyomnyom_hydro/
├── main.py        # entry point — sensor thread + pump thread
├── sensors.py     # all sensor reading functions (stubbed, with hardware notes)
├── pump.py        # relay/GPIO pump control
├── auth.py        # session cookie login + persistence
├── config.py      # server URL, GPIO pins, intervals
├── requirements.txt
└── .env.example
```
