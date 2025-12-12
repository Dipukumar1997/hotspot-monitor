#!/usr/bin/env python3

"""
Hotspot Usage Monitor (Datally-like) - Python GTK3 app

Features:

- Auto-detects network interfaces (prefers wireless: wlan/wlp)
- Shows live upload/download speeds
- Shows total bytes uploaded/downloaded since app start (session)
- Persists daily totals across reboots in ~/.local/share/hotspot_usage.json
- Shows "Today" totals (persisted) and "Since boot" session totals
- Reset button to clear persisted "Today" counters
- Option to choose interface from combobox

Dependencies:

sudo apt install python3-gi gir1.2-gtk-3.0 gir1.2-glib-2.0 python3-psutil

Run:

python3 hotspot_usage.py
"""

import gi, os, json, time
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, GLib
import psutil
from datetime import date

APP_NAME = "Hotspot Usage"

DATA_PATH = os.path.expanduser("~/.local/share/hotspot_usage.json")
STATE_PATH = os.path.expanduser("~/.local/share/hotspot-usage/state.json")

UPDATE_INTERVAL_MS = 1000  # update every second


def load_data():
    try:
        with open(DATA_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"days": {}}
    except Exception:
        return {"days": {}}


def save_data(data):
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w") as f:
        json.dump(data, f)


def save_state_file(speed_down_bps, today_recv, today_sent):
    """
    Small state file read by the GNOME Shell extension.
    """
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    state = {
        "speed_down_bps": speed_down_bps,
        "today": {
            "bytes_recv": today_recv,
            "bytes_sent": today_sent,
        },
    }
    with open(STATE_PATH, "w") as f:
        json.dump(state, f)


def nic_choice():
    # Prefer wifi-like names
    nics = psutil.net_if_stats().keys()
    candidates = [n for n in nics if n.startswith("wl") or n.startswith("wlan")]
    if candidates:
        return sorted(candidates)[0]

    # fallback to first non-loopback that is up
    for n, s in psutil.net_if_stats().items():
        if n == "lo":
            continue
        if s.isup:
            return n

    return list(nics)[0] if nics else None


def bytes_to_human(n):
    # simple conversion
    step = 1024.0
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if n < step:
            return f"{n:0.2f} {unit}"
        n /= step
    return f"{n:0.2f} PB"


class HotspotApp(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title=APP_NAME)
        self.set_border_width(12)
        self.set_default_size(360, 160)

        self.data = load_data()
        self.today_key = date.today().isoformat()
        if "days" not in self.data:
            self.data["days"] = {}
        if self.today_key not in self.data["days"]:
            self.data["days"][self.today_key] = {"bytes_sent": 0, "bytes_recv": 0}

        self.prev_counters = None  # to compute deltas
        self.session_sent = 0
        self.session_recv = 0

        grid = Gtk.Grid(row_spacing=8, column_spacing=8, column_homogeneous=False)
        self.add(grid)

        # Interface selection
        self.if_label = Gtk.Label(label="Interface:")
        grid.attach(self.if_label, 0, 0, 1, 1)

        interfaces = list(psutil.net_if_stats().keys())
        self.if_combo = Gtk.ComboBoxText()
        for iface in interfaces:
            self.if_combo.append_text(iface)

        default_if = nic_choice()
        if default_if and default_if in interfaces:
            self.if_combo.set_active(interfaces.index(default_if))
        else:
            self.if_combo.set_active(0)

        self.if_combo.connect("changed", self.on_iface_changed)
        grid.attach(self.if_combo, 1, 0, 2, 1)

        # Live speed labels
        self.down_label = Gtk.Label(label="Download (speed):")
        grid.attach(self.down_label, 0, 1, 1, 1)

        self.down_value = Gtk.Label(label="0 B/s")
        grid.attach(self.down_value, 1, 1, 2, 1)

        self.up_label = Gtk.Label(label="Upload (speed):")
        grid.attach(self.up_label, 0, 2, 1, 1)

        self.up_value = Gtk.Label(label="0 B/s")
        grid.attach(self.up_value, 1, 2, 2, 1)

        # Session totals (since app started)
        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        grid.attach(sep, 0, 3, 3, 1)

        self.sess_down_label = Gtk.Label(label="Session Download:")
        grid.attach(self.sess_down_label, 0, 4, 1, 1)

        self.sess_down_value = Gtk.Label(label="0 B")
        grid.attach(self.sess_down_value, 1, 4, 2, 1)

        self.sess_up_label = Gtk.Label(label="Session Upload:")
        grid.attach(self.sess_up_label, 0, 5, 1, 1)

        self.sess_up_value = Gtk.Label(label="0 B")
        grid.attach(self.sess_up_value, 1, 5, 2, 1)

        # Today totals (persisted)
        sep2 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        grid.attach(sep2, 0, 6, 3, 1)

        self.today_down_label = Gtk.Label(label="Today Download:")
        grid.attach(self.today_down_label, 0, 7, 1, 1)

        self.today_down_value = Gtk.Label(label="0 B")
        grid.attach(self.today_down_value, 1, 7, 2, 1)

        self.today_up_label = Gtk.Label(label="Today Upload:")
        grid.attach(self.today_up_label, 0, 8, 1, 1)

        self.today_up_value = Gtk.Label(label="0 B")
        grid.attach(self.today_up_value, 1, 8, 2, 1)

        # Buttons
        self.reset_btn = Gtk.Button(label="Reset Today")
        self.reset_btn.connect("clicked", self.on_reset)
        grid.attach(self.reset_btn, 0, 9, 1, 1)

        self.quit_btn = Gtk.Button(label="Quit")
        self.quit_btn.connect("clicked", lambda w: Gtk.main_quit())
        grid.attach(self.quit_btn, 2, 9, 1, 1)

        # Initialize counters
        self.iface = self.if_combo.get_active_text()
        self.init_counters()

        # Run one update immediately so extension sees data fast
        self.update_loop()

        # Start periodic update
        GLib.timeout_add(UPDATE_INTERVAL_MS, self.update_loop)

    def on_iface_changed(self, combo):
        self.iface = combo.get_active_text()
        self.init_counters()

    def init_counters(self):
        counters = psutil.net_io_counters(pernic=True)
        self.prev_counters = counters.get(self.iface, None)
        if self.prev_counters is None:
            self.prev_counters = psutil.net_io_counters(pernic=False)

        # small delay to avoid spike
        time.sleep(0.05)

    def update_loop(self):
        try:
            counters = psutil.net_io_counters(pernic=True)
            cur = counters.get(self.iface, None)
            if cur is None:
                # interface missing
                self.down_value.set_text("N/A")
                self.up_value.set_text("N/A")
                return True

            # compute delta since last read (bytes)
            delta_recv = cur.bytes_recv - self.prev_counters.bytes_recv
            delta_sent = cur.bytes_sent - self.prev_counters.bytes_sent

            if delta_recv < 0:
                delta_recv = 0
            if delta_sent < 0:
                delta_sent = 0

            # update prev
            self.prev_counters = cur

            # record session totals
            self.session_recv += delta_recv
            self.session_sent += delta_sent

            # update persisted daily totals
            today = date.today().isoformat()
            if today != self.today_key:
                # new day rollover
                self.today_key = today
                if today not in self.data["days"]:
                    self.data["days"][today] = {"bytes_sent": 0, "bytes_recv": 0}

            self.data["days"][self.today_key]["bytes_recv"] += delta_recv
            self.data["days"][self.today_key]["bytes_sent"] += delta_sent
            save_data(self.data)

            today_recv = self.data["days"][self.today_key]["bytes_recv"]
            today_sent = self.data["days"][self.today_key]["bytes_sent"]
            speed_down_bps = delta_recv  # bytes per second over 1s interval

            # write state for GNOME Shell extension
            save_state_file(speed_down_bps, today_recv, today_sent)

            # update labels (speed in B/s)
            self.down_value.set_text(f"{bytes_to_human(delta_recv)}/s")
            self.up_value.set_text(f"{bytes_to_human(delta_sent)}/s")

            self.sess_down_value.set_text(bytes_to_human(self.session_recv))
            self.sess_up_value.set_text(bytes_to_human(self.session_sent))

            self.today_down_value.set_text(bytes_to_human(today_recv))
            self.today_up_value.set_text(bytes_to_human(today_sent))

        except Exception:
            # show error in labels
            self.down_value.set_text("err")
            self.up_value.set_text("err")

        return True

    def on_reset(self, button):
        # reset today's counters
        self.data["days"][self.today_key] = {"bytes_sent": 0, "bytes_recv": 0}
        save_data(self.data)

        self.session_recv = 0
        self.session_sent = 0
        # also reset extension state
        save_state_file(0, 0, 0)
        self.sess_down_value.set_text("0 B")
        self.sess_up_value.set_text("0 B")
        self.today_down_value.set_text("0 B")
        self.today_up_value.set_text("0 B")
       


def main():
    app = HotspotApp()
    app.connect("destroy", lambda w: Gtk.main_quit())
    app.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
