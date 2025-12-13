# Hotspot Monitor

Hotspot Monitor is a lightweight Linux application that shows real-time
network usage.\
It provides a simple window and an optional top-bar extension for quick
monitoring.

## Features

-   Shows real-time upload and download speed
-   Displays total uploaded and downloaded data
-   Supports resetting the usage counter at any time
-   Includes a GNOME top-bar indicator extension
-   Runs in the background using a systemd user service

## Installation

1.  Download the `.deb` package.

2.  Install it using:

        sudo dpkg -i hotspot-monitor_VERSION_all.deb
        sudo apt --fix-broken install
        ps aux | grep -i hotspot-monitor
        kill <PID> <PID> <PID> <PID>

4.  The application will appear in the system application list.

5.  The GNOME extension will be enabled automatically.

## Running

To start the GUI manually:

    hotspot-gui

The background daemon starts automatically after installation.
