# Mux Clock (`mux-clock`) — for Raspberry Pi

> A terminal world clock — `pyclock.py` renders individual clocks in the style of `tty-clock`, and `clocks` uses `tmux` to display 2 or 2×2 of them simultaneously.

---

## Features

- 🕐 Big-digit terminal clock rendered in pure Python (no dependencies beyond stdlib)
- 🌍 2-pane (vertical) or 2×2 layout via `tmux`
- 🎨 Time-of-day color — automatically shifts from dark red (night) through orange, yellow, green, cyan, and white across the day
- 💡 Blinking colon, seconds display, and configurable scale
- 🌐 Per-pane timezone with city label
- ⚙️ Reference timezone for color — each clock colors itself by its own local time
- 🖥️ Designed for always-on Raspberry Pi terminal displays

---

## Requirements

- Raspberry Pi OS (or any Debian-based Linux)
- Python 3.9 or later — `sudo apt install python3`
- `tmux` — `sudo apt install tmux`

---

## Installation

```bash
# Default — installs to ~/.local/bin
curl -fsSL https://raw.githubusercontent.com/yusungchang/mux-clock/main/install.sh | bash

# Custom location
curl -fsSL https://raw.githubusercontent.com/yusungchang/mux-clock/main/install.sh | INSTALL_DIR=/usr/local/bin bash
```

You can inspect [`install.sh`](install.sh) before running. Both `clocks` and `pyclock.py` are installed side by side in the same directory.

When installing to the default `~/.local/bin`, the installer will add it to your PATH in `~/.bashrc` if not already present. For custom locations, ensure the directory is on your PATH manually.

After installation, open a new terminal or run:

```
source ~/.bashrc
```

---

## Usage

### `clocks` — launch the tmux session

```
clocks [MODE]
```

| Mode | Layout | Timezones |
|------|--------|-----------|
| `4` (default) | 2×2 grid | Seoul · Los Angeles · Singapore · New York |
| `2` | Top / bottom | Seoul · Los Angeles |

```bash
clocks      # 2×2 layout (default)
clocks 4    # 2×2 layout (explicit)
clocks 2    # top/bottom layout
```

Once running, attach to the session at any time with:

```
tmux attach -t clocks
```

### `pyclock.py` — single clock (standalone)

```
pyclock.py [OPTIONS]
```

| Flag | Description |
|------|-------------|
| `-f <fmt>` | Date format string (strftime). Default: `%Y-%m-%d %a %Z` |
| `-B` | Blinking colon |
| `-n` | Don't quit on keypress |
| `-s <1-3>` | Scale factor for digit size (default: `2`) |
| `-S` | Show seconds |
| `-z <TZ>` | Reference timezone for time-of-day color (default: local) |

```bash
# Single clock for Tokyo, scale 1, with seconds
TZ=Asia/Tokyo python3 pyclock.py -n -S -s 1 -z Asia/Tokyo -f "Tokyo        %Y-%m-%d %a %Z"
```

---

## Color Schedule

Colors are driven by the **reference timezone** (`-z`), so each pane reflects its own local time of day.

| Hours | Color | Period |
|-------|-------|--------|
| 00–04 | Dark red | Night |
| 04–06 | Orange | Dawn |
| 06–08 | Yellow | Sunrise |
| 08–11 | Green | Morning |
| 11–13 | Cyan | Midday |
| 13–15 | White | Peak |
| 15–17 | Cyan | Afternoon |
| 17–19 | Green | Evening |
| 19–21 | Yellow | Sunset |
| 21–22 | Orange | Dusk |
| 22–24 | Dark red | Night |

---

## License

MIT © 2026 Yu-Sung Chang — see [LICENSE](LICENSE) for terms.