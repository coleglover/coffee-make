"""Configuration for switchbot-coffee.

Copy this file to `config.py` and fill in the values below.
`config.py` is gitignored so your personal values are never pushed.
"""

# Bluetooth address of your SwitchBot Bot.
#   macOS: a CoreBluetooth UUID, e.g. "A099C5F5-C62B-0740-84F9-85D103352494"
#   Linux: a MAC address,        e.g. "F4:12:03:AB:CD:EF"
# Discover yours with:  python3 scan_switchbot.py
SWITCHBOT_ADDRESS = "PUT_YOUR_SWITCHBOT_ADDRESS_HERE"

# Absolute path to the Python interpreter that has PySwitchbot installed.
# Must be absolute (launchd requires it). Find yours with:  which python3
PYTHON_PATH = "/usr/bin/python3"

# launchd job label. Change it if you have multiple bots scheduled on this Mac.
# Also determines the schedule filename (~/.<LAUNCHD_LABEL>.schedule.json).
LAUNCHD_LABEL = "com.switchbot.coffee"
