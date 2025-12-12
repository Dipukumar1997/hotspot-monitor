#!/usr/bin/env python3

import os, time, json
import psutil
from datetime import date

STATE_PATH = os.path.expanduser("~/.local/share/hotspot-usage/state.json")
UPDATE_INTERVAL = 1.0  # seconds
PREFERRED_IFACE_PREFIX = ("wl", "wlan", "enp", "eth")

def safe_load():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def safe_save(d):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    tmp = STATE_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(d, f)
    os.replace(tmp, STATE_PATH)

def choose_iface():
    stats = psutil.net_if_stats()
    ifaces = stats.keys()
    for p in PREFERRED_IFACE_PREFIX:
        for name in sorted(ifaces):
            if name.startswith(p) and stats[name].isup:
                return name
    for name, st in stats.items():
        if name == "lo":
            continue
        if st.isup:
            return name
    return next(iter(ifaces), None)

def main():
    iface = choose_iface()
    if iface is None:
        print("No interface found")
        return

    prev = psutil.net_io_counters(pernic=True).get(iface)
    if prev is None:
        prev = psutil.net_io_counters()

    state = safe_load()
    today_key = date.today().isoformat()
    if "today" not in state or state.get("today_day") != today_key:
        state["today"] = {"bytes_recv": 0, "bytes_sent": 0}
        state["today_day"] = today_key

    state.setdefault("iface", iface)
    state.setdefault("speed_down_bps", 0)
    state.setdefault("speed_up_bps", 0)
    state.setdefault("last_updated", int(time.time()))
    safe_save(state)

    while True:
        try:
            now = time.time()
            counters = psutil.net_io_counters(pernic=True).get(iface)
            if counters is None:
                iface = choose_iface()
                counters = psutil.net_io_counters(pernic=True).get(iface)
                state["iface"] = iface

            if counters is None:
                time.sleep(UPDATE_INTERVAL)
                continue

            delta_recv = counters.bytes_recv - getattr(prev, "bytes_recv", 0)
            delta_sent = counters.bytes_sent - getattr(prev, "bytes_sent", 0)
            if delta_recv < 0: delta_recv = 0
            if delta_sent < 0: delta_sent = 0

            state["speed_down_bps"] = int(delta_recv / max(UPDATE_INTERVAL, 1e-6))
            state["speed_up_bps"]   = int(delta_sent / max(UPDATE_INTERVAL, 1e-6))

            today_key_now = date.today().isoformat()
            if state.get("today_day") != today_key_now:
                state["today"] = {"bytes_recv": 0, "bytes_sent": 0}
                state["today_day"] = today_key_now

            state["today"]["bytes_recv"] = state["today"].get("bytes_recv", 0) + delta_recv
            state["today"]["bytes_sent"] = state["today"].get("bytes_sent", 0) + delta_sent
            state["last_updated"] = int(now)

            safe_save(state)
            prev = counters
        except Exception:
            pass
        time.sleep(UPDATE_INTERVAL)

if __name__ == "__main__":
    main()
