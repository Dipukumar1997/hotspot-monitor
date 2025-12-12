import St from 'gi://St';
import GLib from 'gi://GLib';
import Clutter from 'gi://Clutter';
import GObject from 'gi://GObject';
import * as PanelMenu from 'resource:///org/gnome/shell/ui/panelMenu.js';

const STATE_FILE = GLib.get_home_dir() + '/.local/share/hotspot-usage/state.json';

function human(n) {
    let step = 1024.0;
    let units = ['B', 'KB', 'MB', 'GB', 'TB'];
    let v = n;
    for (let i = 0; i < units.length; i++) {
        if (v < step)
            return `${v.toFixed(2)} ${units[i]}`;
        v = v / step;
    }
    return `${v.toFixed(2)} PB`;
}

export const HotspotIndicator = GObject.registerClass(
class HotspotIndicator extends PanelMenu.Button {
    _init() {
        super._init(0.0, 'Hotspot Indicator');

        this._label = new St.Label({
            text: '…',
            y_align: Clutter.ActorAlign.CENTER,
        });
        this.add_child(this._label);

        this.connect('button-press-event', () => {
            // GLib.spawn_command_line_async('/usr/local/bin/hotspot-gui');
            GLib.spawn_command_line_async('hotspot-gui');
        });

        this._timeoutId = GLib.timeout_add_seconds(
            GLib.PRIORITY_DEFAULT,
            1,
            () => {
                this._refresh();
                return GLib.SOURCE_CONTINUE;
            }
        );

        this._refresh();
    }

    _refresh() {
        try {
            let [ok, contents] = GLib.file_get_contents(STATE_FILE);
            if (!ok)
                return;

            let txt = new TextDecoder().decode(contents);
            let obj = JSON.parse(txt);

            let today = obj.today || {};
            let down = obj.speed_down_bps || 0;
            let totalToday = (today.bytes_recv || 0) + (today.bytes_sent || 0);

            let downH = human(down) + '/s';
            let totalH = human(totalToday);

            this._label.text = `↓ ${downH}  |  Today ${totalH}`;
        } catch (e) {
            this._label.text = '↓ - | Today -';
        }
    }

    vfunc_destroy() {
        if (this._timeoutId) {
            GLib.source_remove(this._timeoutId);
            this._timeoutId = 0;
        }
        super.vfunc_destroy();
    }
});

