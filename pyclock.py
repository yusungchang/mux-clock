#!/usr/bin/env python3
"""
pyclock.py — terminal clock with circadian color and bold 6×5 digits
"""

VERSION = "@@VERSION@@"

import curses
import time
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

# ------------------------------------------------------------------------------
# 6-wide x 5-tall digits
# Each row is exactly 6 chars: '#' = filled, ' ' = empty
# Rendered with SCALE: each '#' becomes SCALE×SCALE block
# Colon is 2-wide (uses same 5-row structure)
# ------------------------------------------------------------------------------
DIGITS = {
    '0': ["######",
          "##  ##",
          "##  ##",
          "##  ##",
          "######"],

    '1': ["  ####",
          "    ##",
          "    ##",
          "    ##",
          "  ####"],

    '2': ["######",
          "    ##",
          "######",
          "##    ",
          "######"],

    '3': ["######",
          "    ##",
          "######",
          "    ##",
          "######"],

    '4': ["##  ##",
          "##  ##",
          "######",
          "    ##",
          "    ##"],

    '5': ["######",
          "##    ",
          "######",
          "    ##",
          "######"],

    '6': ["######",
          "##    ",
          "######",
          "##  ##",
          "######"],

    '7': ["######",
          "    ##",
          "  ####",
          "  ##  ",
          "  ##  "],

    '8': ["######",
          "##  ##",
          "######",
          "##  ##",
          "######"],

    '9': ["######",
          "##  ##",
          "######",
          "    ##",
          "######"],

    ':': [" ",
          "#",
          " ",
          "#",
          " "],

    ' ': ["      ",
          "      ",
          "      ",
          "      ",
          "      "],
}

# Colon is narrow — 1 col wide in pattern, rendered at SCALE
COLON_WIDTH = 1

SCALE = 2

# ------------------------------------------------------------------------------
# Circadian color schedule  (start_hour, end_hour, xterm-256 color code)
# ------------------------------------------------------------------------------
COLOR_SCHEDULE = [
    ( 0,  4,  88),   # Night      — dark red
    ( 4,  6, 214),   # Dawn       — orange
    ( 6,  8, 226),   # Sunrise    — yellow
    ( 8, 11,  34),   # Morning    — green
    (11, 13,  51),   # Midday     — cyan
    (13, 15, 231),   # Peak       — white
    (15, 17,  51),   # Afternoon  — cyan
    (17, 19,  34),   # Evening    — green
    (19, 21, 226),   # Sunset     — yellow
    (21, 22, 214),   # Dusk       — orange
    (22, 24,  88),   # Night      — dark red
]

COLOR_LABELS = [
    ( 0,  4,  88, "dark red",  "Night    "),
    ( 4,  6, 214, "orange",    "Dawn     "),
    ( 6,  8, 226, "yellow",    "Sunrise  "),
    ( 8, 11,  34, "green",     "Morning  "),
    (11, 13,  51, "cyan",      "Midday   "),
    (13, 15, 231, "white",     "Peak     "),
    (15, 17,  51, "cyan",      "Afternoon"),
    (17, 19,  34, "green",     "Evening  "),
    (19, 21, 226, "yellow",    "Sunset   "),
    (21, 22, 214, "orange",    "Dusk     "),
    (22, 24,  88, "dark red",  "Night    "),
]

# ------------------------------------------------------------------------------
# Usage / help
# ------------------------------------------------------------------------------
def print_usage():
    print(f"pyclock.py {VERSION} — terminal clock with circadian color\n")
    print("Usage: TZ=<timezone> python3 pyclock.py [OPTIONS]\n")
    print("Options:")
    print("  -h         Display this help and color schedule, then exit")
    print("  -v         Display version and exit")
    print("  -f <fmt>   Date format string (strftime). Default: %Y-%m-%d %a %Z")
    print("  -B         Blinking colon")
    print("  -n         Don't quit on keypress")
    print("  -s <1-3>   Scale factor for digit size (default: 2)")
    print("  -S         Show seconds")
    print("  -z <TZ>    Reference timezone for circadian color (default: local)\n")
    print("Examples:")
    print("  python3 pyclock.py -S -B")
    print("  TZ=Asia/Tokyo python3 pyclock.py -n -S -s 1 -z Asia/Tokyo\n")
    print_color_schedule()

def print_version():
    print(f"pyclock.py {VERSION}")

def print_color_schedule():
    ESC = "\033["
    RESET = "\033[0m"
    print("Circadian color schedule:")
    print(f"  {'Hours':<9} {'Period':<12} {'Color':<10}  Sample")
    print(f"  {'-'*9} {'-'*12} {'-'*10}  {'-'*14}")
    for start, end, code, label, period in COLOR_LABELS:
        # Render a colored block swatch using ANSI 256-color
        swatch = f"{ESC}38;5;{code}m██████{RESET}"
        print(f"  {start:02d}–{end:02d}      {period}  {label:<10}  {swatch}")
    print()

# ------------------------------------------------------------------------------
# Color helpers
# ------------------------------------------------------------------------------
def get_ref_hour(ref_tz):
    try:
        return datetime.now(ZoneInfo(ref_tz)).hour
    except Exception:
        return datetime.now().hour

def get_color_for_hour(hour):
    for start, end, code in COLOR_SCHEDULE:
        if start <= hour < end:
            return code
    return 88

# ------------------------------------------------------------------------------
# Drawing
# ------------------------------------------------------------------------------
def char_display_width(ch):
    """Return the rendered column width of a character at scale 1."""
    if ch == ':':
        return COLON_WIDTH
    pattern = DIGITS.get(ch, DIGITS[' '])
    return len(pattern[0])

def draw_char(stdscr, ch, start_y, start_x, color_pair):
    pattern = DIGITS.get(ch, DIGITS[' '])
    for row_i, row in enumerate(pattern):
        for col_i, cell in enumerate(row):
            if cell == '#':
                for sy in range(SCALE):
                    for sx in range(SCALE):
                        y = start_y + row_i * SCALE + sy
                        x = start_x + col_i * SCALE + sx
                        try:
                            stdscr.addch(y, x, ' ', color_pair | curses.A_REVERSE)
                        except curses.error:
                            pass

def render(stdscr, time_str, date_str, color_pair, blink_colon, show_colon):
    stdscr.erase()
    h, w = stdscr.getmaxyx()

    gap = max(1, SCALE)

    # Calculate total width accounting for variable-width colon
    total_w = sum(char_display_width(ch) * SCALE for ch in time_str)
    total_w += gap * (len(time_str) - 1)

    clock_h = 5 * SCALE
    total_h = clock_h + 2

    start_y = max(0, (h - total_h) // 2)
    start_x = max(0, (w - total_w) // 2)

    x = start_x
    for ch in time_str:
        draw_ch = ' ' if (blink_colon and ch == ':' and not show_colon) else ch
        draw_char(stdscr, draw_ch, start_y, x, color_pair)
        x += char_display_width(draw_ch) * SCALE + gap

    date_y = start_y + clock_h + 1
    date_x = max(0, (w - len(date_str)) // 2)
    try:
        stdscr.addstr(date_y, date_x, date_str, color_pair)
    except curses.error:
        pass

    stdscr.refresh()

# ------------------------------------------------------------------------------
# Main loop
# ------------------------------------------------------------------------------
def main(stdscr, fmt, blink_colon, no_quit, scale, show_seconds, ref_tz):
    global SCALE
    SCALE = scale

    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    stdscr.nodelay(True)

    show_colon = True
    current_color_code = -1
    color_pair = None

    while True:
        ref_hour = get_ref_hour(ref_tz) if ref_tz else time.localtime().tm_hour
        new_color_code = get_color_for_hour(ref_hour)

        if new_color_code != current_color_code:
            current_color_code = new_color_code
            curses.init_pair(1, new_color_code, -1)
            color_pair = curses.color_pair(1)

        now = time.localtime()
        time_str = time.strftime("%H:%M:%S", now) if show_seconds else time.strftime("%H:%M", now)
        date_str = time.strftime(fmt, now)

        render(stdscr, time_str, date_str, color_pair, blink_colon, show_colon)
        show_colon = not show_colon

        for _ in range(5):
            time.sleep(0.1)
            key = stdscr.getch()
            if key != -1 and not no_quit:
                return

# ------------------------------------------------------------------------------
# Argument parsing
# ------------------------------------------------------------------------------
def parse_args():
    args = sys.argv[1:]
    fmt = "%Y-%m-%d %a %Z"
    blink_colon = False
    no_quit = False
    scale = 2
    show_seconds = False
    ref_tz = None

    i = 0
    while i < len(args):
        if args[i] == '-h':
            print_usage()
            sys.exit(0)
        elif args[i] == '-v':
            print_version()
            sys.exit(0)
        elif args[i] == '-f' and i + 1 < len(args):
            fmt = args[i+1]; i += 2
        elif args[i] == '-s' and i + 1 < len(args):
            scale = max(1, int(args[i+1])); i += 2
        elif args[i] == '-z' and i + 1 < len(args):
            ref_tz = args[i+1]; i += 2
        elif args[i] == '-B':
            blink_colon = True; i += 1
        elif args[i] == '-n':
            no_quit = True; i += 1
        elif args[i] == '-S':
            show_seconds = True; i += 1
        else:
            i += 1

    return fmt, blink_colon, no_quit, scale, show_seconds, ref_tz

if __name__ == '__main__':
    fmt, blink_colon, no_quit, scale, show_seconds, ref_tz = parse_args()
    curses.wrapper(main, fmt, blink_colon, no_quit, scale, show_seconds, ref_tz)