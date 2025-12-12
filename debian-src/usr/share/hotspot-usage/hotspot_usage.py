# #!/usr/bin/env python3

# """
# Hotspot Usage Monitor (Datally-like) - Python GTK3 app
# """

# import gi, os, json, time
# gi.require_version("Gtk", "3.0")

# from gi.repository import Gtk, GLib
# import psutil
# from datetime import date

# APP_NAME = "Hotspot Usage"

# DATA_PATH = os.path.expanduser("~/.local/share/hotspot_usage.json")
# STATE_FILE = os.path.expanduser("~/.config/hotspot-monitor/window.json")
# STATE_PATH = os.path.expanduser("~/.local/share/hotspot-usage/state.json")
# DEFAULT_POS = {"x": 100, "y": 100}

# UPDATE_INTERVAL_MS = 1000  # update every second


# def load_data():
#     try:
#         with open(DATA_PATH, "r") as f:
#             data = json.load(f)
#     except FileNotFoundError:
#         data = {"days": {}}
#     except Exception:
#         data = {"days": {}}

#     if "window_pos" not in data:
#         data["window_pos"] = DEFAULT_POS.copy()
#     return data


# def save_data(data):
#     os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
#     with open(DATA_PATH, "w") as f:
#         json.dump(data, f)


# def save_state_file(speed_down_bps, today_recv, today_sent):
#     """
#     Small state file read by the GNOME Shell extension.
#     """
#     os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
#     state = {
#         "speed_down_bps": speed_down_bps,
#         "today": {
#             "bytes_recv": today_recv,
#             "bytes_sent": today_sent,
#         },
#     }
#     with open(STATE_PATH, "w") as f:
#         json.dump(state, f)


# def nic_choice():
#     # Prefer wifi-like names
#     nics = psutil.net_if_stats().keys()
#     candidates = [n for n in nics if n.startswith("wl") or n.startswith("wlan")]
#     if candidates:
#         return sorted(candidates)[0]

#     # fallback to first non-loopback that is up
#     for n, s in psutil.net_if_stats().items():
#         if n == "lo":
#             continue
#         if s.isup:
#             return n

#     return list(nics)[0] if nics else None


# def bytes_to_human(n):
#     # simple conversion
#     step = 1024.0
#     for unit in ["B", "KB", "MB", "GB", "TB"]:
#         if n < step:
#             return f"{n:0.2f} {unit}"
#         n /= step
#     return f"{n:0.2f} PB"


# class HotspotApp(Gtk.Window):
#     def __init__(self):
#         Gtk.Window.__init__(self, title=APP_NAME)
#         self.set_border_width(12)
#         self.set_default_size(360, 160)

#         self.data = load_data()
#         self._load_window_state()

#         self.today_key = date.today().isoformat()
#         if "days" not in self.data:
#             self.data["days"] = {}
#         if self.today_key not in self.data["days"]:
#             self.data["days"][self.today_key] = {"bytes_sent": 0, "bytes_recv": 0}

#         self.prev_counters = None  # to compute deltas
#         self.session_sent = 0
#         self.session_recv = 0

#         grid = Gtk.Grid(row_spacing=8, column_spacing=8, column_homogeneous=False)
#         self.add(grid)

#         # Interface selection
#         self.if_label = Gtk.Label(label="Interface:")
#         grid.attach(self.if_label, 0, 0, 1, 1)

#         interfaces = list(psutil.net_if_stats().keys())
#         self.if_combo = Gtk.ComboBoxText()
#         for iface in interfaces:
#             self.if_combo.append_text(iface)

#         default_if = nic_choice()
#         if default_if and default_if in interfaces:
#             self.if_combo.set_active(interfaces.index(default_if))
#         else:
#             self.if_combo.set_active(0)

#         self.if_combo.connect("changed", self.on_iface_changed)
#         grid.attach(self.if_combo, 1, 0, 2, 1)

#         # Live speed labels
#         self.down_label = Gtk.Label(label="Download (speed):")
#         grid.attach(self.down_label, 0, 1, 1, 1)

#         self.down_value = Gtk.Label(label="0 B/s")
#         grid.attach(self.down_value, 1, 1, 2, 1)

#         self.up_label = Gtk.Label(label="Upload (speed):")
#         grid.attach(self.up_label, 0, 2, 1, 1)

#         self.up_value = Gtk.Label(label="0 B/s")
#         grid.attach(self.up_value, 1, 2, 2, 1)

#         # Session totals (since app started)
#         sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
#         grid.attach(sep, 0, 3, 3, 1)

#         self.sess_down_label = Gtk.Label(label="Session Download:")
#         grid.attach(self.sess_down_label, 0, 4, 1, 1)

#         self.sess_down_value = Gtk.Label(label="0 B")
#         grid.attach(self.sess_down_value, 1, 4, 2, 1)

#         self.sess_up_label = Gtk.Label(label="Session Upload:")
#         grid.attach(self.sess_up_label, 0, 5, 1, 1)

#         self.sess_up_value = Gtk.Label(label="0 B")
#         grid.attach(self.sess_up_value, 1, 5, 2, 1)

#         # Today totals (persisted)
#         sep2 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
#         grid.attach(sep2, 0, 6, 3, 1)

#         self.today_down_label = Gtk.Label(label="Today Download:")
#         grid.attach(self.today_down_label, 0, 7, 1, 1)

#         self.today_down_value = Gtk.Label(label="0 B")
#         grid.attach(self.today_down_value, 1, 7, 2, 1)

#         self.today_up_label = Gtk.Label(label="Today Upload:")
#         grid.attach(self.today_up_label, 0, 8, 1, 1)

#         self.today_up_value = Gtk.Label(label="0 B")
#         grid.attach(self.today_up_value, 1, 8, 2, 1)

#         # Buttons
#         self.reset_btn = Gtk.Button(label="Reset Today")
#         self.reset_btn.connect("clicked", self.on_reset)
#         grid.attach(self.reset_btn, 0, 9, 1, 1)

#         self.quit_btn = Gtk.Button(label="Quit")
#         self.quit_btn.connect("clicked", self.on_destroy)
#         grid.attach(self.quit_btn, 2, 9, 1, 1)

#         # Track and save window position
#         self.connect("configure-event", self.on_configure)
#         self.connect("destroy", self.on_destroy)

#         # Initialize counters
#         self.iface = self.if_combo.get_active_text()
#         self.init_counters()

#         # Run one update immediately so extension sees data fast
#         self.update_loop()

#         # Start periodic update
#         GLib.timeout_add(UPDATE_INTERVAL_MS, self.update_loop)

#     def _load_window_state(self):
#         try:
#             with open(STATE_FILE, "r") as f:
#                 st = json.load(f)
#             if "width" in st and "height" in st:
#                 self.resize(st["width"], st["height"])
#             if "x" in st and "y" in st:
#                 self.move(st["x"], st["y"])
#         except Exception:
#             # fallback: center if no state
#             self.set_position(Gtk.WindowPosition.CENTER)

#     def on_configure(self, window, event):
#         # called when moved or resized
#         x, y = self.get_position()
#         w, h = self.get_size()
#         os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
#         with open(STATE_FILE, "w") as f:
#             json.dump({"x": x, "y": y, "width": w, "height": h}, f)
#         return False

#     def on_destroy(self, *args):
#         self.on_configure(self, None)
#         # keep your existing data save
#         save_data(self.data)
#         Gtk.main_quit()

#     def on_iface_changed(self, combo):
#         self.iface = combo.get_active_text()
#         self.init_counters()

#     def init_counters(self):
#         counters = psutil.net_io_counters(pernic=True)
#         self.prev_counters = counters.get(self.iface, None)
#         if self.prev_counters is None:
#             self.prev_counters = psutil.net_io_counters(pernic=False)
#         # small delay to avoid spike
#         time.sleep(0.05)

#     def update_loop(self):
#         try:
#             counters = psutil.net_io_counters(pernic=True)
#             cur = counters.get(self.iface, None)
#             if cur is None:
#                 # interface missing
#                 self.down_value.set_text("N/A")
#                 self.up_value.set_text("N/A")
#                 return True

#             # compute delta since last read (bytes)
#             delta_recv = cur.bytes_recv - self.prev_counters.bytes_recv
#             delta_sent = cur.bytes_sent - self.prev_counters.bytes_sent

#             if delta_recv < 0:
#                 delta_recv = 0
#             if delta_sent < 0:
#                 delta_sent = 0

#             # update prev
#             self.prev_counters = cur

#             # record session totals
#             self.session_recv += delta_recv
#             self.session_sent += delta_sent

#             # update persisted daily totals
#             today = date.today().isoformat()
#             if today != self.today_key:
#                 # new day rollover
#                 self.today_key = today
#                 if today not in self.data["days"]:
#                     self.data["days"][today] = {"bytes_sent": 0, "bytes_recv": 0}

#             self.data["days"][self.today_key]["bytes_recv"] += delta_recv
#             self.data["days"][self.today_key]["bytes_sent"] += delta_sent
#             save_data(self.data)

#             today_recv = self.data["days"][self.today_key]["bytes_recv"]
#             today_sent = self.data["days"][self.today_key]["bytes_sent"]
#             speed_down_bps = delta_recv  # bytes per second over 1s interval

#             # write state for GNOME Shell extension
#             save_state_file(speed_down_bps, today_recv, today_sent)

#             # update labels (speed in B/s)
#             self.down_value.set_text(f"{bytes_to_human(delta_recv)}/s")
#             self.up_value.set_text(f"{bytes_to_human(delta_sent)}/s")

#             self.sess_down_value.set_text(bytes_to_human(self.session_recv))
#             self.sess_up_value.set_text(bytes_to_human(self.session_sent))

#             self.today_down_value.set_text(bytes_to_human(today_recv))
#             self.today_up_value.set_text(bytes_to_human(today_sent))

#         except Exception:
#             # show error in labels
#             self.down_value.set_text("err")
#             self.up_value.set_text("err")

#         return True

#     def on_reset(self, button):
#         # reset today's counters in memory and on disk
#         self.data["days"][self.today_key] = {"bytes_sent": 0, "bytes_recv": 0}
#         save_data(self.data)

#         # reset session counters too
#         self.session_recv = 0
#         self.session_sent = 0

#         # also reset extension state
#         save_state_file(0, 0, 0)

#         # update labels
#         self.sess_down_value.set_text("0 B")
#         self.sess_up_value.set_text("0 B")
#         self.today_down_value.set_text("0 B")
#         self.today_up_value.set_text("0 B")


# def main():
#     app = HotspotApp()
#     app.show_all()
#     Gtk.main()


# if __name__ == "__main__":
#     main()

#!/usr/bin/env python3

"""
Hotspot Usage Monitor (Datally-like) - Python GTK3 app
"""

import gi, os, json, time, sys 
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, GLib
import psutil
from datetime import date

APP_NAME = "Hotspot Usage"

DATA_PATH = os.path.expanduser("~/.local/share/hotspot_usage.json")
STATE_FILE = os.path.expanduser("~/.config/hotspot-monitor/window.json")
STATE_PATH = os.path.expanduser("~/.local/share/hotspot-usage/state.json")
DEFAULT_POS = {"x": 100, "y": 100}

UPDATE_INTERVAL_MS = 1000  # update every second

# ... (load_data, save_data, save_state_file, nic_choice, bytes_to_human remain the same) ...
# I am skipping the unchanged functions for brevity in this response.

def load_data():
    try:
        with open(DATA_PATH, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {"days": {}}
    except Exception:
        data = {"days": {}}

    if "window_pos" not in data:
        data["window_pos"] = DEFAULT_POS.copy()
    return data


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

# class HotspotApp(Gtk.Window):
   
#     def __init__(self):
#         Gtk.Window.__init__(self, title=APP_NAME)
#         self.set_border_width(12)
#         self.set_default_size(360, 160)
        
#         # FIX: Disable window resizing
#         self.set_resizable(False) 

#         self.data = load_data()
#         self._load_window_state()

#         self.today_key = date.today().isoformat()
#         if "days" not in self.data:
#             self.data["days"] = {}
#         if self.today_key not in self.data["days"]:
#             self.data["days"][self.today_key] = {"bytes_sent": 0, "bytes_recv": 0}

#         self.prev_counters = None
#         self.session_sent = 0
#         self.session_recv = 0

#         grid = Gtk.Grid(row_spacing=8, column_spacing=8, column_homogeneous=False)
#         self.add(grid)

#         # Interface selection
#         self.if_label = Gtk.Label(label="Interface:")
#         grid.attach(self.if_label, 0, 0, 1, 1)

#         interfaces = list(psutil.net_if_stats().keys())
#         self.if_combo = Gtk.ComboBoxText()
#         for iface in interfaces:
#             self.if_combo.append_text(iface)

#         default_if = nic_choice()
#         if default_if and default_if in interfaces:
#             self.if_combo.set_active(interfaces.index(default_if))
#         else:
#             self.if_combo.set_active(0)

#         self.if_combo.connect("changed", self.on_iface_changed)
#         grid.attach(self.if_combo, 1, 0, 2, 1)
        
#         # --- FIX: Define ALL labels (UI elements) BEFORE calling update_loop() ---
        
#         # Live speed labels
#         self.down_label = Gtk.Label(label="Download (speed):")
#         grid.attach(self.down_label, 0, 1, 1, 1)
#         self.down_value = Gtk.Label(label="0 B/s") # Defined
#         grid.attach(self.down_value, 1, 1, 2, 1)

#         self.up_label = Gtk.Label(label="Upload (speed):")
#         grid.attach(self.up_label, 0, 2, 1, 1)
#         self.up_value = Gtk.Label(label="0 B/s") # Defined
#         grid.attach(self.up_value, 1, 2, 2, 1)

#         # Session totals
#         sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
#         grid.attach(sep, 0, 3, 3, 1)
#         self.sess_down_label = Gtk.Label(label="Session Download:")
#         grid.attach(self.sess_down_label, 0, 4, 1, 1)
#         self.sess_down_value = Gtk.Label(label="0 B") # Defined
#         grid.attach(self.sess_down_value, 1, 4, 2, 1)
#         self.sess_up_label = Gtk.Label(label="Session Upload:")
#         grid.attach(self.sess_up_label, 0, 5, 1, 1)
#         self.sess_up_value = Gtk.Label(label="0 B") # Defined
#         grid.attach(self.sess_up_value, 1, 5, 2, 1)

#         # Today totals
#         sep2 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
#         grid.attach(sep2, 0, 6, 3, 1)
#         self.today_down_label = Gtk.Label(label="Today Download:")
#         grid.attach(self.today_down_label, 0, 7, 1, 1)
#         self.today_down_value = Gtk.Label(label="0 B") # Defined
#         grid.attach(self.today_down_value, 1, 7, 2, 1)
#         self.today_up_label = Gtk.Label(label="Today Upload:")
#         grid.attach(self.today_up_label, 0, 8, 1, 1)
#         self.today_up_value = Gtk.Label(label="0 B") # Defined
#         grid.attach(self.today_up_value, 1, 8, 2, 1)
        
#         # --- End UI definitions ---

#         # Buttons
#         self.reset_btn = Gtk.Button(label="Reset Today")
#         self.reset_btn.connect("clicked", self.on_reset)
#         grid.attach(self.reset_btn, 0, 9, 1, 1)

#         self.quit_btn = Gtk.Button(label="Quit")
#         self.quit_btn.connect("clicked", self.on_destroy)
#         grid.attach(self.quit_btn, 2, 9, 1, 1)

#         # Track and save window position: Only connect to destroy.
#         self.connect("destroy", self.on_destroy)

#         # Initialize counters 
#         self.iface = self.if_combo.get_active_text()
#         self.init_counters()
        
#         # --- FIX: update_loop is now safe to call as all labels exist ---
#         self.update_loop()
#         GLib.timeout_add(UPDATE_INTERVAL_MS, self.update_loop)

#     def _load_window_state(self):
#         # ... (Loading logic) ...
#         print(f"Attempting to load window state from: {STATE_FILE}", file=sys.stderr)
#         try:
#             with open(STATE_FILE, "r") as f:
#                 # st = json.load(f)
#                 self._state = json.load(f)
#             # print() 
#             # if "width" in st and "height" in st:
#             #     print(st["width"])
#             #     self.resize(st["width"], st["height"])
#             # if "x" in st and "y" in st:
#             #     self.move(st["x"], st["y"])
#             print("Successfully loaded window state.", file=sys.stderr)

#         except FileNotFoundError:
#             print(f"Window state file not found ({STATE_FILE}). Centering window.", file=sys.stderr)
#             self.set_position(Gtk.WindowPosition.CENTER)
#         except Exception as e:
#             print(f"Error loading window state: {e}. Centering window.", file=sys.stderr)
#             self.set_position(Gtk.WindowPosition.CENTER)
            
#     def _save_window_state(self):
#         # Logic to save the final position/size
#         x, y = self.get_position()
#         w, h = self.get_size()
        
#         try:
#             os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
#             with open(STATE_FILE, "w") as f:
#                 json.dump({"x": x, "y": y, "width": w, "height": h}, f)
#             print(f"Final saved window state to {STATE_FILE}: x={x}, y={y}, w={w}, h={h}", file=sys.stderr)
#         except Exception as e:
#             print(f"CRITICAL ERROR saving window state: {e}", file=sys.stderr)
            
#         return False

#     def on_destroy(self, *args):
#         # 1. Capture the final window position/size
#         self._save_window_state() 

#         # 2. Keep existing data save
#         save_data(self.data)
        
#         # 3. Quit the application
#         Gtk.main_quit()
        
#     def on_iface_changed(self, combo):
#         self.iface = combo.get_active_text()
#         self.init_counters()

#     def init_counters(self):
#         counters = psutil.net_io_counters(pernic=True)
#         self.prev_counters = counters.get(self.iface, None)
#         if self.prev_counters is None:
#             self.prev_counters = psutil.net_io_counters(pernic=False)
#         # small delay to avoid spike
#         time.sleep(0.05)

#     def update_loop(self):
#         try:
#             counters = psutil.net_io_counters(pernic=True)
#             cur = counters.get(self.iface, None)
#             if cur is None:
#                 # interface missing
#                 self.down_value.set_text("N/A")
#                 self.up_value.set_text("N/A")
#                 return True

#             # compute delta since last read (bytes)
#             delta_recv = cur.bytes_recv - self.prev_counters.bytes_recv
#             delta_sent = cur.bytes_sent - self.prev_counters.bytes_sent

#             if delta_recv < 0:
#                 delta_recv = 0
#             if delta_sent < 0:
#                 delta_sent = 0

#             # update prev
#             self.prev_counters = cur

#             # record session totals
#             self.session_recv += delta_recv
#             self.session_sent += delta_sent

#             # update persisted daily totals
#             today = date.today().isoformat()
#             if today != self.today_key:
#                 # new day rollover
#                 self.today_key = today
#                 if today not in self.data["days"]:
#                     self.data["days"][today] = {"bytes_sent": 0, "bytes_recv": 0}

#             self.data["days"][self.today_key]["bytes_recv"] += delta_recv
#             self.data["days"][self.today_key]["bytes_sent"] += delta_sent
#             save_data(self.data)

#             today_recv = self.data["days"][self.today_key]["bytes_recv"]
#             today_sent = self.data["days"][self.today_key]["bytes_sent"]
#             speed_down_bps = delta_recv  # bytes per second over 1s interval

#             # write state for GNOME Shell extension
#             save_state_file(speed_down_bps, today_recv, today_sent)

#             # update labels (speed in B/s)
#             self.down_value.set_text(f"{bytes_to_human(delta_recv)}/s")
#             self.up_value.set_text(f"{bytes_to_human(delta_sent)}/s")

#             self.sess_down_value.set_text(bytes_to_human(self.session_recv))
#             self.sess_up_value.set_text(bytes_to_human(self.session_sent))

#             self.today_down_value.set_text(bytes_to_human(today_recv))
#             self.today_up_value.set_text(bytes_to_human(today_sent))

#         except Exception:
#             # show error in labels
#             self.down_value.set_text("err")
#             self.up_value.set_text("err")

#         return True

#     def on_reset(self, button):
#         # reset today's counters in memory and on disk
#         self.data["days"][self.today_key] = {"bytes_sent": 0, "bytes_recv": 0}
#         save_data(self.data)

#         # reset session counters too
#         self.session_recv = 0
#         self.session_sent = 0

#         # also reset extension state
#         save_state_file(0, 0, 0)

#         # update labels
#         self.sess_down_value.set_text("0 B")
#         self.sess_up_value.set_text("0 B")
#         self.today_down_value.set_text("0 B")
#         self.today_up_value.set_text("0 B")

class HotspotApp(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title=APP_NAME)
        self.set_border_width(12)
        self.set_default_size(360, 160)
        self.set_resizable(False)
        # self.set_position(Gtk.WindowPosition.CENTER)
        GLib.idle_add(self._move_to_top_right)


        # ---------- LOAD WINDOW STATE EARLY ----------
        # self._load_window_state()   # Only loads JSON (no move/resize yet!)

        self.data = load_data()
        self.today_key = date.today().isoformat()
        if "days" not in self.data:
            self.data["days"] = {}
        if self.today_key not in self.data["days"]:
            self.data["days"][self.today_key] = {"bytes_sent": 0, "bytes_recv": 0}

        self.prev_counters = None
        self.session_sent = 0
        self.session_recv = 0

        # ---------------- UI ----------------
        grid = Gtk.Grid(row_spacing=8, column_spacing=8)
        self.add(grid)

        self.if_label = Gtk.Label(label="Interface:")
        grid.attach(self.if_label, 0, 0, 1, 1)

        interfaces = list(psutil.net_if_stats().keys())
        self.if_combo = Gtk.ComboBoxText()
        for iface in interfaces:
            self.if_combo.append_text(iface)

        default_if = nic_choice()
        if default_if in interfaces:
            self.if_combo.set_active(interfaces.index(default_if))
        else:
            self.if_combo.set_active(0)

        self.if_combo.connect("changed", self.on_iface_changed)
        grid.attach(self.if_combo, 1, 0, 2, 1)

        # Speed labels
        self.down_label = Gtk.Label(label="Download (speed):")
        self.down_value = Gtk.Label(label="0 B/s")
        grid.attach(self.down_label, 0, 1, 1, 1)
        grid.attach(self.down_value, 1, 1, 2, 1)

        self.up_label = Gtk.Label(label="Upload (speed):")
        self.up_value = Gtk.Label(label="0 B/s")
        grid.attach(self.up_label, 0, 2, 1, 1)
        grid.attach(self.up_value, 1, 2, 2, 1)

        # Session totals
        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        grid.attach(sep, 0, 3, 3, 1)

        self.sess_down_label = Gtk.Label(label="Session Download:")
        self.sess_down_value = Gtk.Label(label="0 B")
        grid.attach(self.sess_down_label, 0, 4, 1, 1)
        grid.attach(self.sess_down_value, 1, 4, 2, 1)

        self.sess_up_label = Gtk.Label(label="Session Upload:")
        self.sess_up_value = Gtk.Label(label="0 B")
        grid.attach(self.sess_up_label, 0, 5, 1, 1)
        grid.attach(self.sess_up_value, 1, 5, 2, 1)

        # Today totals
        sep2 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        grid.attach(sep2, 0, 6, 3, 1)

        self.today_down_label = Gtk.Label(label="Today Download:")
        self.today_down_value = Gtk.Label(label="0 B")
        grid.attach(self.today_down_label, 0, 7, 1, 1)
        grid.attach(self.today_down_value, 1, 7, 2, 1)

        self.today_up_label = Gtk.Label(label="Today Upload:")
        self.today_up_value = Gtk.Label(label="0 B")
        grid.attach(self.today_up_label, 0, 8, 1, 1)
        grid.attach(self.today_up_value, 1, 8, 2, 1)

        # Buttons
        self.reset_btn = Gtk.Button(label="Reset Today")
        self.reset_btn.connect("clicked", self.on_reset)
        grid.attach(self.reset_btn, 0, 9, 1, 1)

        self.quit_btn = Gtk.Button(label="Quit")
        self.quit_btn.connect("clicked", self.on_destroy)
        grid.attach(self.quit_btn, 2, 9, 1, 1)

        self.connect("destroy", self.on_destroy)

        self.iface = self.if_combo.get_active_text()
        self.init_counters()

        self.update_loop()
        GLib.timeout_add(UPDATE_INTERVAL_MS, self.update_loop)

        # ---------- FIX: RESTORE POSITION AFTER THE WINDOW IS MAPPED ----------
        # self.connect("map", self._restore_window_state)


    # ============================================================
    #                WINDOW STATE: LOAD (EARLY)
    # ============================================================
    def _load_window_state(self):
        """Load window state into memory, but DO NOT apply yet."""
        try:
            with open(STATE_FILE, "r") as f:
                self._state = json.load(f)
            print("Loaded window state.")
        except:
            self._state = None
            print("No previous window state. Will center window.")


    def _move_to_top_right(self):
        screen = self.get_screen()
        monitor = screen.get_monitor_at_window(self.get_window())
        geo = screen.get_monitor_geometry(monitor)

        w, h = self.get_size()

        # Calculate top-right position
        x = geo.x + geo.width - w - 10   # 10px margin
        y = geo.y + 10                   # little margin from top

        self.move(x, y)
        return False

    # ============================================================
    #                WINDOW STATE: APPLY (AFTER MAP)
    # ============================================================
    def _restore_window_state(self, *args):
        """Apply window size & position after the window is mapped."""
        if not self._state:
            self.set_position(Gtk.WindowPosition.CENTER)
            return

        st = self._state

        if "width" in st and "height" in st:
            self.resize(st["width"], st["height"])

        if "x" in st and "y" in st:
            self.move(st["x"], st["y"])


    # ============================================================
    #                      SAVE WINDOW STATE
    # ============================================================
    def _save_window_state(self):
        x, y = self.get_position()
        w, h = self.get_size()

        try:
            os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
            with open(STATE_FILE, "w") as f:
                json.dump({"x": x, "y": y, "width": w, "height": h}, f)

            print(f"Saved window: x={x}, y={y}, w={w}, h={h}")
        except Exception as e:
            print("Error saving window:", e)

        return False


    # ============================================================
    #                     DESTROY HANDLER
    # ============================================================
    def on_destroy(self, *args):
        # self._save_window_state()
        save_data(self.data)
        Gtk.main_quit()


    # ============================================================
    #    (Your existing methods remain unchanged below this point)
    # ============================================================
    def on_iface_changed(self, combo):
        self.iface = combo.get_active_text()
        self.init_counters()

    def init_counters(self):
        counters = psutil.net_io_counters(pernic=True)
        self.prev_counters = counters.get(self.iface, None)
        if self.prev_counters is None:
            self.prev_counters = psutil.net_io_counters(pernic=False)
        time.sleep(0.05)

    # def update_loop(self):
    #     try:
    #         counters = psutil.net_io_counters(pernic=True)
    #         cur = counters.get(self.iface, None)
    #         if cur is None:
    #             self.down_value.set_text("N/A")
    #             self.up_value.set_text("N/A")
    #             return True

    #         delta_recv = cur.bytes_recv - self.prev_counters.bytes_recv
    #         delta_sent = cur.bytes_sent - self.prev_counters.bytes_sent
    #         delta_recv = max(delta_recv, 0)
    #         delta_sent = max(delta_sent, 0)

    #         self.prev_counters = cur

    #         self.session_recv += delta_recv
    #         self.session_sent += delta_sent

    #         today = date.today().isoformat()
    #         if today != self.today_key:
    #             self.today_key = today
    #             self.data["days"][today] = {"bytes_sent": 0, "bytes_recv": 0}

    #         self.data["days"][self.today_key]["bytes_recv"] += delta_recv
    #         self.data["days"][self.today_key]["bytes_sent"] += delta_sent
    #         save_data(self.data)

    #         today_recv = self.data["days"][self.today_key]["bytes_recv"]
    #         today_sent = self.data["days"][self.today_key]["bytes_sent"]

    #         save_state_file(delta_recv, today_recv, today_sent)

    #         self.down_value.set_text(f"{bytes_to_human(delta_recv)}/s")
    #         self.up_value.set_text(f"{bytes_to_human(delta_sent)}/s")

    #         self.sess_down_value.set_text(bytes_to_human(self.session_recv))
    #         self.sess_up_value.set_text(bytes_to_human(self.session_sent))
    #         self.today_down_value.set_text(bytes_to_human(today_recv))
    #         self.today_up_value.set_text(bytes_to_human(today_sent))

    #     except Exception:
    #         self.down_value.set_text("err")
    #         self.up_value.set_text("err")

    #     return True

    def update_loop(self):
    try:
        counters = psutil.net_io_counters(pernic=True)
        cur = counters.get(self.iface, None)
        if cur is None:
            self.down_value.set_text("N/A")
            self.up_value.set_text("N/A")
            return True

        delta_recv = cur.bytes_recv - self.prev_counters.bytes_recv
        delta_sent = cur.bytes_sent - self.prev_counters.bytes_sent
        delta_recv = max(delta_recv, 0)
        delta_sent = max(delta_sent, 0)

        self.prev_counters = cur

        # session
        self.session_recv += delta_recv
        self.session_sent += delta_sent

        # ----- DAILY TOTALS (THIS PART MATTERS) -----
        today = date.today().isoformat()
        if today != self.today_key:
            # new day: start from zero
            self.today_key = today
            self.data["days"][today] = {"bytes_sent": 0, "bytes_recv": 0}

        # at this point self.data["days"][self.today_key] may already
        # have been reset to 0 by on_reset(), so just keep adding
        self.data["days"][self.today_key]["bytes_recv"] += delta_recv
        self.data["days"][self.today_key]["bytes_sent"] += delta_sent
        save_data(self.data)

        today_recv = self.data["days"][self.today_key]["bytes_recv"]
        today_sent = self.data["days"][self.today_key]["bytes_sent"]

        # write what the extension reads
        save_state_file(delta_recv, today_recv, today_sent)

        # labels
        self.down_value.set_text(f"{bytes_to_human(delta_recv)}/s")
        self.up_value.set_text(f"{bytes_to_human(delta_sent)}/s")
        self.sess_down_value.set_text(bytes_to_human(self.session_recv))
        self.sess_up_value.set_text(bytes_to_human(self.session_sent))
        self.today_down_value.set_text(bytes_to_human(today_recv))
        self.today_up_value.set_text(bytes_to_human(today_sent))

    except Exception:
        self.down_value.set_text("err")
        self.up_value.set_text("err")
    return True

    def on_reset(self, button):
        self.data["days"][self.today_key] = {"bytes_sent": 0, "bytes_recv": 0}
        save_data(self.data)
        self.session_recv = 0
        self.session_sent = 0
        save_state_file(0, 0, 0)

        self.sess_down_value.set_text("0 B")
        self.sess_up_value.set_text("0 B")
        self.today_down_value.set_text("0 B")
        self.today_up_value.set_text("0 B")

def main():
    app = HotspotApp()
    app.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()