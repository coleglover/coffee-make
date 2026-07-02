#!/usr/bin/env bash
# Install the `coffee` shell function into ~/.zshrc.
# The function dispatches to coffee.py wherever this script lives.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COFFEE_PY="$SCRIPT_DIR/coffee.py"
CONFIG_PY="$SCRIPT_DIR/config.py"

if [ ! -f "$CONFIG_PY" ]; then
  echo "Error: $CONFIG_PY not found."
  echo "Copy config.example.py to config.py and fill in your values first:"
  echo "  cp $SCRIPT_DIR/config.example.py $CONFIG_PY"
  exit 1
fi

# Read PYTHON_PATH from config.py
PYTHON_PATH=$(python3 -c "import sys; sys.path.insert(0, '$SCRIPT_DIR'); import config; print(config.PYTHON_PATH)")

if [ ! -x "$PYTHON_PATH" ]; then
  echo "Warning: PYTHON_PATH from config.py is not executable: $PYTHON_PATH"
  echo "Continuing anyway, but 'coffee' may not run until you fix this."
fi

ZSHRC="$HOME/.zshrc"
touch "$ZSHRC"

# Remove any previous install with the sentinel markers.
python3 - "$ZSHRC" <<'PYEOF'
import sys, re
path = sys.argv[1]
with open(path) as f:
    text = f.read()
text = re.sub(r'\n?# >>> coffee CLI >>>\n.*?# <<< coffee CLI <<<\n?', '\n', text, flags=re.DOTALL)
with open(path, 'w') as f:
    f.write(text)
PYEOF

# Append new function (variables expand; escape $@ so it's literal)
cat >> "$ZSHRC" <<EOF

# >>> coffee CLI >>>
coffee() {
  $PYTHON_PATH $COFFEE_PY "\$@"
}
# <<< coffee CLI <<<
EOF

echo "Installed coffee CLI in $ZSHRC"
echo "  Python:  $PYTHON_PATH"
echo "  Script:  $COFFEE_PY"
echo ""
echo "Now run:  source ~/.zshrc"
echo "Then try: coffee help"
