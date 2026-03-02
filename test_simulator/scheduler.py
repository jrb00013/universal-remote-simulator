#!/usr/bin/env python3
"""
Autonomous scheduler: time-of-day rules + presets → automatic button presses.
Sends commands to the simulator API so the "remote" controls the TV without user input.
Run alongside the web server: poetry run python scheduler.py
"""
import json
import time
import threading
import os
import sys

try:
    import requests
except ImportError:
    requests = None

# Config and API
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG_PATH = os.path.join(SCRIPT_DIR, "autonomous_config.json")
API_BASE = os.environ.get("SIMULATOR_API", "http://localhost:5000")
API_BUTTON = f"{API_BASE}/api/button"
CHECK_INTERVAL_SEC = 30
DAY_NAMES = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def send_button(button_code: int, delay_ms: int = 0) -> bool:
    if requests is None:
        return False
    try:
        r = requests.post(
            API_BUTTON,
            json={"button_code": button_code},
            headers={"Content-Type": "application/json"},
            timeout=5,
        )
        if delay_ms > 0:
            time.sleep(delay_ms / 1000.0)
        return r.status_code == 200
    except Exception:
        return False


def apply_preset(presets: list, preset_name: str) -> bool:
    for p in presets:
        if p.get("name") == preset_name:
            for b in p.get("buttons", []):
                code = b.get("button_code")
                delay = b.get("delay_ms", 0)
                if code is not None:
                    send_button(code, delay)
            return True
    return False


def should_run_rule(rule: dict) -> bool:
    now = time.localtime()
    rule_time = rule.get("time", "")
    if not rule_time:
        return False
    try:
        h, m = map(int, rule_time.split(":"))
    except ValueError:
        return False
    days = rule.get("days") or DAY_NAMES
    today = DAY_NAMES[now.tm_wday]
    if today not in [d.lower() for d in days]:
        return False
    # Trigger if we're in the same minute (scheduler runs every CHECK_INTERVAL_SEC)
    return now.tm_hour == h and now.tm_min == m


def run_scheduler(config_path: str):
    config = load_config(config_path)
    presets = config.get("presets", [])
    time_rules = config.get("time_rules", [])
    last_triggered = {}  # (time, preset_name) -> last run minute

    print("[Scheduler] Autonomous scheduler started.")
    print(f"[Scheduler] Config: {config_path}")
    print(f"[Scheduler] API: {API_BASE}")
    print(f"[Scheduler] Rules: {len(time_rules)}, Presets: {len(presets)}")

    while True:
        try:
            now = time.localtime()
            minute_key = (now.tm_hour, now.tm_min)

            for rule in time_rules:
                if rule.get("action") != "apply_preset":
                    continue
                preset_name = rule.get("preset_name")
                if not preset_name:
                    continue
                if not should_run_rule(rule):
                    continue
                key = (minute_key, preset_name)
                if last_triggered.get(key) == minute_key:
                    continue
                last_triggered[key] = minute_key
                print(f"[Scheduler] Trigger: {rule.get('time')} -> preset '{preset_name}'")
                apply_preset(presets, preset_name)

            # Prune old keys to avoid unbounded growth
            if len(last_triggered) > 100:
                last_triggered = {k: v for k, v in list(last_triggered.items())[-50:]}

        except Exception as e:
            print(f"[Scheduler] Error: {e}")

        time.sleep(CHECK_INTERVAL_SEC)


def main():
    config_path = os.environ.get("AUTONOMOUS_CONFIG", DEFAULT_CONFIG_PATH)
    if not os.path.isfile(config_path):
        print(f"[Scheduler] Config not found: {config_path}")
        sys.exit(1)
    if requests is None:
        print("[Scheduler] Install requests: pip install requests")
        sys.exit(1)
    run_scheduler(config_path)


if __name__ == "__main__":
    main()
