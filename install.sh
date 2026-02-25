#!/bin/bash

# ==============================================================================
#  mux-clock - Install Script
#  Downloads the latest release from GitHub and installs both binaries.
#
#  Usage:
#    curl -fsSL https://raw.githubusercontent.com/yusungchang/mux-clock/main/install.sh | bash
#
#  Custom install directory:
#    curl -fsSL .../install.sh | INSTALL_DIR=/usr/local/bin bash
#
#  Installs:
#    - clocks      (tmux launcher)
#    - pyclock.py  (Python clock engine)
# ==============================================================================

set -euo pipefail

REPO="yusungchang/mux-clock"
DEST="${INSTALL_DIR:-$HOME/.local/bin}"
BASHRC="$HOME/.bashrc"

BASE_URL="https://github.com/$REPO/releases/latest/download"

echo "Installing mux-clock to $DEST..."
echo ""

# Ensure destination exists
mkdir -p "$DEST"

# Check requirements (warn only)
if ! command -v python3 &>/dev/null; then
    echo "Warning: python3 is not installed. Please run: sudo apt install python3" >&2
fi

if ! command -v tmux &>/dev/null; then
    echo "Warning: tmux is not installed. Please run: sudo apt install tmux" >&2
fi

# Download clocks
echo "Downloading clocks..."
if ! curl -fsSL "$BASE_URL/clocks" -o "$DEST/clocks"; then
    echo "Error: Failed to download clocks" >&2
    exit 1
fi
chmod +x "$DEST/clocks"
echo "  Installed clocks → $DEST/clocks"

# Download pyclock.py
echo "Downloading pyclock.py..."
if ! curl -fsSL "$BASE_URL/pyclock.py" -o "$DEST/pyclock.py"; then
    echo "Error: Failed to download pyclock.py" >&2
    exit 1
fi
chmod +x "$DEST/pyclock.py"
echo "  Installed pyclock.py → $DEST/pyclock.py"

# Only manage PATH if installing to the default location
if [ "$DEST" = "$HOME/.local/bin" ]; then
    if [ ! -f "$BASHRC" ]; then
        touch "$BASHRC"
    fi

    if ! grep -q '\$HOME/\.local/bin' "$BASHRC" && ! grep -q '~/\.local/bin' "$BASHRC"; then
        cat >> "$BASHRC" <<'BASHRC_EOF'

# Added by mux-clock installer: ensure local bin is on PATH
if [ -d "$HOME/.local/bin" ] && [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    export PATH="$HOME/.local/bin:$PATH"
fi
BASHRC_EOF
        echo ""
        echo "Appended PATH export to $BASHRC"
        echo "Run 'source ~/.bashrc' or open a new terminal to apply PATH changes."
    else
        echo ""
        echo "$BASHRC already contains ~/.local/bin in PATH"
    fi
else
    echo ""
    echo "Installed to custom directory $DEST — ensure it is on your PATH."
fi

echo ""
echo "Done. Run 'clocks' to start, or 'clocks 2' for a 2-pane layout."