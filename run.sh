#!/bin/bash
# JournalMatch launcher for macOS / Linux

set -e

echo ""
echo " ================================================"
echo "   JournalMatch  |  Journal Recommendation Tool"
echo " ================================================"
echo ""

# ── Find Python 3 ─────────────────────────────────────────────────────────────
PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        ver=$("$cmd" -c "import sys; print(sys.version_info.major)" 2>/dev/null)
        if [ "$ver" = "3" ]; then
            PYTHON="$cmd"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo " ERROR: Python 3 was not found on this computer."
    echo ""
    echo " macOS:  Install from https://www.python.org/downloads/"
    echo "         or run:  brew install python"
    echo " Linux:  sudo apt install python3  (Ubuntu/Debian)"
    echo "         sudo dnf install python3  (Fedora)"
    echo ""
    exit 1
fi

echo " Python found: $($PYTHON --version)"
echo ""

# ── Install / verify dependencies ─────────────────────────────────────────────
echo " [1/2] Checking dependencies..."
echo "       (First run downloads ~2 GB of AI libraries."
echo "        This can take 5-10 minutes. Subsequent runs start in seconds.)"
echo ""

"$PYTHON" -m pip install -r requirements.txt -q --disable-pip-version-check

echo " Dependencies ready."
echo ""

# ── Open browser after a short delay ──────────────────────────────────────────
(
    sleep 5
    # macOS
    open http://localhost:5000 2>/dev/null && exit
    # Linux with desktop
    xdg-open http://localhost:5000 2>/dev/null && exit
    true
) &

# ── Start the server ──────────────────────────────────────────────────────────
echo " [2/2] Starting JournalMatch..."
echo ""
echo "  +--------------------------------------------------+"
echo "  |                                                  |"
echo "  |   Your browser will open automatically.          |"
echo "  |   If it does not, open:  http://localhost:5000   |"
echo "  |                                                  |"
echo "  |   To stop the tool, press Ctrl+C                 |"
echo "  |                                                  |"
echo "  +--------------------------------------------------+"
echo ""

"$PYTHON" app.py
