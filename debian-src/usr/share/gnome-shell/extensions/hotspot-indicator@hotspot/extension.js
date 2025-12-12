import { Extension } from 'resource:///org/gnome/shell/extensions/extension.js';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import { HotspotIndicator } from './indicator.js';

export default class HotspotIndicatorExtension extends Extension {
    enable() {
        this._indicator = new HotspotIndicator();
        Main.panel.addToStatusArea('hotspot-indicator', this._indicator, 1, 'right');
    }

    disable() {
        if (this._indicator) {
            this._indicator.destroy();
            this._indicator = null;
        }
    }
}
