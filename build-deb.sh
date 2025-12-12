#!/usr/bin/env bash
set -e

# -------- settings you can edit --------
VERSION="1.0-16"       # keep in sync with DEBIAN/control
PKGNAME="hotspot-monitor"
OUT_DEB="${PKGNAME}_${VERSION}_all.deb"
# --------------------------------------

ROOT="$(cd "$(dirname "$0")" && pwd)"
DEBROOT="$ROOT/debian-src"

echo "[*] Preparing debian-src tree"

# Ensure directory structure exists
mkdir -p "$DEBROOT/usr/bin"
mkdir -p "$DEBROOT/usr/share/hotspot-usage"
mkdir -p "$DEBROOT/usr/share/gnome-shell/extensions/hotspot-indicator@hotspot"
mkdir -p "$DEBROOT/usr/share/applications"
mkdir -p "$DEBROOT/usr/lib/systemd/user"
mkdir -p "$DEBROOT/DEBIAN"

# 1) Copy app files
echo "[*] Copying Python app + launcher"
cp "$ROOT/app/hotspot_usage.py" "$DEBROOT/usr/share/hotspot-usage/hotspot_usage.py"
cp "$ROOT/app/daemon.py"        "$DEBROOT/usr/share/hotspot-usage/daemon.py"
cp "$ROOT/app/hotspot-gui"      "$DEBROOT/usr/bin/hotspot-gui"

# 2) Copy shell extension
echo "[*] Copying GNOME shell extension"
cp "$ROOT/shell-extension/hotspot-indicator@hotspot/extension.js" \
   "$DEBROOT/usr/share/gnome-shell/extensions/hotspot-indicator@hotspot/extension.js"
cp "$ROOT/shell-extension/hotspot-indicator@hotspot/indicator.js" \
   "$DEBROOT/usr/share/gnome-shell/extensions/hotspot-indicator@hotspot/indicator.js"
cp "$ROOT/shell-extension/hotspot-indicator@hotspot/metadata.json" \
   "$DEBROOT/usr/share/gnome-shell/extensions/hotspot-indicator@hotspot/metadata.json"

# 3) Make sure maintainer scripts are executable (if present)
echo "[*] Fixing DEBIAN script permissions"
if [ -f "$DEBROOT/DEBIAN/postinst" ]; then
  chmod 755 "$DEBROOT/DEBIAN/postinst"
fi
if [ -f "$DEBROOT/DEBIAN/prerm" ]; then
  chmod 755 "$DEBROOT/DEBIAN/prerm"
fi
chmod 755 "$DEBROOT/usr/bin/hotspot-gui"

# 4) Build .deb
echo "[*] Building $OUT_DEB"
dpkg-deb --build "$DEBROOT" "$OUT_DEB"

echo
echo "[+] Done. Built: $OUT_DEB"
echo "    Install with: sudo dpkg -i $OUT_DEB"
