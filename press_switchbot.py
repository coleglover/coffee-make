"""Press the SwitchBot Bot once via Bluetooth."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.resolve()))

try:
    import config
except ImportError:
    print("Error: config.py not found.", file=sys.stderr)
    print("Copy config.example.py to config.py and fill in your SWITCHBOT_ADDRESS.", file=sys.stderr)
    sys.exit(1)

from bleak import BleakScanner
from switchbot import Switchbot

ADDRESS = config.SWITCHBOT_ADDRESS


async def main():
    print(f"Scanning for SwitchBot at {ADDRESS}...")
    device = await BleakScanner.find_device_by_address(ADDRESS, timeout=15)
    if device is None:
        raise RuntimeError(
            f"Could not find SwitchBot at {ADDRESS}. "
            "Make sure Bluetooth is on and the terminal/host has Bluetooth permission "
            "(System Settings -> Privacy & Security -> Bluetooth)."
        )
    print(f"Found {device.name or 'device'} ({device.address}). Pressing...")
    bot = Switchbot(device)
    await bot.press()
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
