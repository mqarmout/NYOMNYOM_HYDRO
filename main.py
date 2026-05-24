"""
NYOMNYOM Hydro — Raspberry Pi main loop.

Two threads run concurrently:
  - sensor_thread: reads all sensors and POSTs to /api/hydro/readings every SENSOR_INTERVAL_SEC
  - pump_thread:   polls /api/hydro/pump every PUMP_POLL_SEC, runs the schedule,
                   and handles pending_manual triggers

Run:
    python main.py

Stop with Ctrl+C — the pump is turned off on exit.
"""
import threading
import time
import logging
import sys

import sensors
import pump
import auth
from config import SERVER_URL, SENSOR_INTERVAL_SEC, PUMP_POLL_SEC

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


# ── API helpers ───────────────────────────────────────────────────────────────

def api_get(path: str) -> dict | None:
    session = auth.ensure_session()
    try:
        resp = session.get(f"{SERVER_URL}{path}", timeout=10)
        if resp.status_code == 401:
            log.warning("[api] session expired, re-authenticating")
            auth.invalidate()
            session = auth.ensure_session()
            resp = session.get(f"{SERVER_URL}{path}", timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        log.error(f"[api] GET {path} failed: {e}")
        return None


def api_post(path: str, data: dict) -> bool:
    session = auth.ensure_session()
    try:
        resp = session.post(f"{SERVER_URL}{path}", json=data, timeout=10)
        if resp.status_code == 401:
            log.warning("[api] session expired, re-authenticating")
            auth.invalidate()
            session = auth.ensure_session()
            resp = session.post(f"{SERVER_URL}{path}", json=data, timeout=10)
        resp.raise_for_status()
        return True
    except Exception as e:
        log.error(f"[api] POST {path} failed: {e}")
        return False


def api_put(path: str, data: dict) -> bool:
    session = auth.ensure_session()
    try:
        resp = session.put(f"{SERVER_URL}{path}", json=data, timeout=10)
        resp.raise_for_status()
        return True
    except Exception as e:
        log.error(f"[api] PUT {path} failed: {e}")
        return False


# ── Sensor thread ─────────────────────────────────────────────────────────────

def sensor_loop() -> None:
    log.info(f"[sensors] starting — posting every {SENSOR_INTERVAL_SEC}s")
    while True:
        reading = sensors.read_all()
        non_null = {k: v for k, v in reading.items() if v is not None}
        if non_null:
            ok = api_post("/api/hydro/readings", reading)
            log.info(f"[sensors] posted {list(non_null.keys())} — {'ok' if ok else 'FAILED'}")
        else:
            log.warning("[sensors] all readings are None (hardware not connected)")
        time.sleep(SENSOR_INTERVAL_SEC)


# ── Pump thread ───────────────────────────────────────────────────────────────

def pump_loop() -> None:
    log.info(f"[pump] starting — polling every {PUMP_POLL_SEC}s")
    _in_cycle = False
    _cycle_start = 0.0

    while True:
        schedule = api_get("/api/hydro/pump")
        if schedule is None:
            time.sleep(PUMP_POLL_SEC)
            continue

        enabled     = schedule.get("enabled", False)
        on_min      = int(schedule.get("on_duration_min",  15))
        off_min     = int(schedule.get("off_duration_min", 45))
        pending     = schedule.get("pending_manual", False)
        cycle_sec   = (on_min + off_min) * 60

        # Manual trigger takes priority
        if pending:
            log.info("[pump] manual trigger received")
            # Clear the flag before running so a second trigger isn't ignored
            api_put("/api/hydro/pump", {
                "enabled":          enabled,
                "on_duration_min":  on_min,
                "off_duration_min": off_min,
                "pending_manual":   False,
            })
            pump.run_cycle(on_min, off_min)
            _cycle_start = time.time()
            _in_cycle = True
            continue

        # Scheduled cycling
        if enabled:
            now = time.time()
            if not _in_cycle or (now - _cycle_start) >= cycle_sec:
                log.info(f"[pump] scheduled cycle: {on_min}min on / {off_min}min off")
                pump.run_cycle(on_min, off_min)
                _cycle_start = time.time()
                _in_cycle = True
        else:
            pump.turn_off()
            _in_cycle = False

        time.sleep(PUMP_POLL_SEC)


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    log.info(f"[main] NYOMNYOM Hydro starting — server: {SERVER_URL}")

    t_sensors = threading.Thread(target=sensor_loop, daemon=True, name="sensors")
    t_pump    = threading.Thread(target=pump_loop,   daemon=True, name="pump")

    t_sensors.start()
    t_pump.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log.info("[main] shutting down")
    finally:
        pump.cleanup()
        sys.exit(0)


if __name__ == "__main__":
    main()
