#!/usr/bin/env python3
"""coffee CLI - control your SwitchBot on demand or on a schedule."""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))

try:
    import config
except ImportError:
    print(f"Error: config.py not found in {SCRIPT_DIR}", file=sys.stderr)
    print("Copy config.example.py to config.py and fill in your values.", file=sys.stderr)
    sys.exit(1)

PYTHON = config.PYTHON_PATH
PRESS_SCRIPT = str(SCRIPT_DIR / "press_switchbot.py")
LABEL = config.LAUNCHD_LABEL

SCHEDULE_FILE = Path.home() / f".{LABEL}.schedule.json"
PLIST_DIR = Path.home() / "Library" / "LaunchAgents"
PLIST = PLIST_DIR / f"{LABEL}.plist"

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
# launchd weekday: 0/7 = Sunday, 1 = Monday, ..., 6 = Saturday
LAUNCHD_WEEKDAY = {"Mon": 1, "Tue": 2, "Wed": 3, "Thu": 4, "Fri": 5, "Sat": 6, "Sun": 0}


# ---------- Schedule storage ----------

def load_schedule() -> dict:
    if SCHEDULE_FILE.exists():
        try:
            return json.loads(SCHEDULE_FILE.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def save_schedule(sched: dict) -> None:
    SCHEDULE_FILE.write_text(json.dumps(sched, indent=2))


# ---------- Parsing ----------

def parse_time(s: str):
    """Accept '7:00am', '07:00', '14:30', '7am', '7'. Return 'HH:MM' or None."""
    s = s.strip().lower().replace(" ", "")
    m = re.match(r'^(\d{1,2})(?::(\d{2}))?(am|pm)?$', s)
    if not m:
        return None
    h = int(m.group(1))
    mi = int(m.group(2) or 0)
    ampm = m.group(3)
    if ampm == "pm" and h < 12:
        h += 12
    if ampm == "am" and h == 12:
        h = 0
    if not (0 <= h <= 23 and 0 <= mi <= 59):
        return None
    return f"{h:02d}:{mi:02d}"


def parse_days(s: str):
    """Accept 'weekdays', 'weekends', 'all', or 'mon,wed,fri'. Return list of day names or None."""
    s = s.strip().lower()
    if s in ("all", "everyday", "every day", "daily"):
        return DAYS[:]
    if s == "weekdays":
        return DAYS[:5]
    if s == "weekends":
        return DAYS[5:]
    out = []
    for token in re.split(r'[,\s]+', s):
        if not token:
            continue
        t = token[:3].capitalize()
        if t in DAYS and t not in out:
            out.append(t)
        else:
            return None
    return out if out else None


# ---------- launchd plist management ----------

def build_plist(sched: dict) -> str:
    intervals = []
    for day in DAYS:
        if day not in sched:
            continue
        h, m = sched[day].split(":")
        intervals.append(
            "        <dict>\n"
            f"            <key>Hour</key><integer>{int(h)}</integer>\n"
            f"            <key>Minute</key><integer>{int(m)}</integer>\n"
            f"            <key>Weekday</key><integer>{LAUNCHD_WEEKDAY[day]}</integer>\n"
            "        </dict>"
        )
    intervals_xml = "\n".join(intervals)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTD/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{LABEL}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{PYTHON}</string>
        <string>{PRESS_SCRIPT}</string>
    </array>
    <key>StartCalendarInterval</key>
    <array>
{intervals_xml}
    </array>
    <key>StandardOutPath</key>
    <string>/tmp/coffee.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/coffee.err</string>
    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
"""


def apply_plist(sched: dict) -> None:
    PLIST_DIR.mkdir(parents=True, exist_ok=True)
    if PLIST.exists():
        subprocess.run(["launchctl", "unload", str(PLIST)], capture_output=True)
    if not sched:
        if PLIST.exists():
            PLIST.unlink()
        return
    PLIST.write_text(build_plist(sched))
    result = subprocess.run(
        ["launchctl", "load", str(PLIST)], capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"  warning: launchctl load said: {result.stderr.strip()}", file=sys.stderr)


# ---------- Display ----------

def format_schedule(sched: dict) -> str:
    if not sched:
        return "  (none)"
    by_time = {}
    for day in DAYS:
        if day in sched:
            by_time.setdefault(sched[day], []).append(day)
    lines = []
    for time, days in sorted(by_time.items()):
        lines.append(f"  {time}  -  {', '.join(days)}")
    return "\n".join(lines)


# ---------- Commands ----------

def cmd_make(args):
    os.execv(PYTHON, [PYTHON, PRESS_SCRIPT])


def cmd_schedule_list(args):
    sched = load_schedule()
    print("Current schedule:")
    print(format_schedule(sched))


def cmd_schedule_clear(args):
    save_schedule({})
    apply_plist({})
    print("Schedule cleared.")


def cmd_schedule(args):
    if args and args[0] == "list":
        return cmd_schedule_list(args[1:])
    if args and args[0] in ("clear", "remove"):
        return cmd_schedule_clear(args[1:])

    sched = load_schedule()
    print("Existing schedule:")
    print(format_schedule(sched))
    print()

    try:
        while True:
            raw = input("What time? (e.g. 7:00am or 14:30, ctrl-c to cancel): ")
            time_ = parse_time(raw)
            if time_:
                break
            print(f"  Couldn't parse '{raw}'. Try '7:00am', '14:30', '7am'.")

        while True:
            raw = input("Which days? [weekdays/weekends/all/mon,wed,fri]: ")
            days = parse_days(raw)
            if days:
                break
            print(f"  Couldn't parse '{raw}'. Try 'weekdays', 'weekends', 'all', or 'mon,wed,fri'.")
    except (KeyboardInterrupt, EOFError):
        print("\nCancelled.")
        return

    # "all" overwrites the whole schedule; otherwise only update chosen days
    if set(days) == set(DAYS):
        sched = {}
    for day in days:
        sched[day] = time_

    save_schedule(sched)
    apply_plist(sched)
    print("\nSaved. Updated schedule:")
    print(format_schedule(sched))
    print()
    print("Logs (when the schedule fires): /tmp/coffee.log and /tmp/coffee.err")


USAGE = """\
coffee - control the SwitchBot above your coffee machine.

Commands:
  coffee make                  Press the SwitchBot once now
  coffee schedule              Interactively add or update a scheduled time
  coffee schedule list         Show the current schedule
  coffee schedule clear        Remove all scheduled times
  coffee help                  Show this message

Examples:
  coffee make
  coffee schedule              # then enter e.g. 7:00am + weekdays
  coffee schedule list

Schedule rules:
  - One time per day.
  - Selecting 'weekdays' or 'weekends' only updates those days.
  - Selecting 'all' overwrites the entire schedule.
  - Selecting specific days (e.g. mon,wed) overwrites just those.

Files:
  ~/.<LAUNCHD_LABEL>.schedule.json               stored schedule
  ~/Library/LaunchAgents/<LAUNCHD_LABEL>.plist   launchd job
  /tmp/coffee.log, /tmp/coffee.err               scheduled-run logs
"""


def main():
    args = sys.argv[1:]
    if not args:
        print(USAGE)
        sys.exit(1)
    cmd, rest = args[0], args[1:]
    if cmd == "make":
        cmd_make(rest)
    elif cmd == "schedule":
        cmd_schedule(rest)
    elif cmd in ("-h", "--help", "help"):
        print(USAGE)
    else:
        print(f"Unknown command: {cmd}\n")
        print(USAGE)
        sys.exit(1)


if __name__ == "__main__":
    main()
