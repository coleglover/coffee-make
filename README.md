# coffee-make

Press your coffee machine's power button from your Mac using a [Switchbot bot](https://ca.switch-bot.com/products/switchbot-bot?_psq=switchbot+bot&_v=1.0). Run it on demand from the terminal, put it on a recurring schedule, or trigger it via Siri (WIP).

## The `coffee` command

Once installed, this repo gives you:

```
coffee make              Press the SwitchBot once now
coffee schedule          Interactively add or update a scheduled time
coffee schedule list     Show the current schedule
coffee schedule clear    Remove all scheduled times
coffee help              Show help
```

Scheduling uses macOS `launchd`, so it survives reboots and needs no third-party service.

## Requirements

- macOS (uses `launchd` for scheduling and CoreBluetooth via `bleak`)
- Python 3.9+
- A SwitchBot Bot within Bluetooth range of your Mac
- Bluetooth permission granted to your terminal app (System Settings → Privacy & Security → Bluetooth)

## Setup

1. **Clone the repo**

   ```
   git clone https://github.com/<you>/coffee-make.git
   cd coffee-make
   ```

2. **Install Python dependencies.** PySwitchbot doesn't work with bleak ≥ 1.0 yet, so pin bleak below it:

   ```
   python3 -m pip install "PySwitchbot" "bleak<1.0"
   ```

3. **Find your bot's Bluetooth address:**

   ```
   python3 scan_switchbot.py
   ```

   Devices likely to be SwitchBots are marked in the output. On macOS the address is a CoreBluetooth UUID; on Linux it's a MAC.

4. **Create your config** and fill it in:

   ```
   cp config.example.py config.py
   ```

   Edit `config.py`:
   - `SWITCHBOT_ADDRESS` — the address from step 3
   - `PYTHON_PATH` — the output of `which python3`

5. **Install the shell command:**

   ```
   bash install_coffee.sh
   source ~/.zshrc
   ```

6. **Test it:**

   ```
   coffee make
   ```

## Scheduling notes

- Times accept `7:00am`, `14:30`, `7am`, etc.
- Days accept `weekdays`, `weekends`, `all`, or a comma list like `mon,wed,fri`.
- `all` overwrites the whole schedule. Anything else only overwrites the days you selected — so a `weekdays` entry and a `weekends` entry coexist.

## Extras (not included in this repo)

- **Siri trigger:** create a macOS Shortcut with a "Run Shell Script" action running `coffee make`, name it "Make a coffee", and Hey Siri picks it up.
- **Trigger from your phone away from home:** put your Mac and iPhone on the same Tailscale network, then use the iOS Shortcuts "Run Script Over SSH" action to run `coffee make`.

## Files this creates on your system

| Path | Purpose |
|---|---|
| `~/.zshrc` (appended block) | `coffee()` shell function |
| `~/.<LAUNCHD_LABEL>.schedule.json` | your saved schedule |
| `~/Library/LaunchAgents/<LAUNCHD_LABEL>.plist` | launchd job |
| `/tmp/coffee.log`, `/tmp/coffee.err` | scheduled-run logs |

To uninstall: `coffee schedule clear`, then remove the `# >>> coffee CLI >>>` block from `~/.zshrc`.

