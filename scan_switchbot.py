"""Scan for nearby Bluetooth devices to find your SwitchBot's address.

Run once during setup:
    python3 scan_switchbot.py

Look for devices marked as likely SwitchBots. Copy the Address into config.py.
"""
import asyncio
from bleak import BleakScanner


def is_likely_switchbot(device, adv):
    name = (device.name or "").lower()
    if any(k in name for k in ("switchbot", "wohand", "wocurtain", "womini")):
        return True
    # SwitchBot manufacturer ID is 0x0969
    return 0x0969 in (adv.manufacturer_data or {})


async def main():
    print("Scanning for 10 seconds...\n")
    devices = await BleakScanner.discover(timeout=10, return_adv=True)

    pairs = list(devices.values())
    pairs.sort(key=lambda p: (not is_likely_switchbot(*p), (p[0].name or "").lower()))

    for device, adv in pairs:
        marker = "  <-- looks like a SwitchBot" if is_likely_switchbot(device, adv) else ""
        print(f"Name:    {device.name}{marker}")
        print(f"Address: {device.address}")
        if adv.manufacturer_data:
            print(f"Mfr:     {adv.manufacturer_data}")
        print("-" * 40)


if __name__ == "__main__":
    asyncio.run(main())
