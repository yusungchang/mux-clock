#!/usr/bin/env python3
"""
pyclock.py — tty-clock replacement with proper pane-aware centering
Usage: TZ=Asia/Seoul python3 pyclock.py [-f "format"] [-B] [-n] [-s scale] [-S] [-z TZ]
  -f format  date format string (strftime)
  -B         blinking colon
  -n         don't quit on keypress
  -s [1-3]   scale factor for digit size (default 2)
  -S         show seconds
  -z TZ      reference timezone for day/night color (default: local TZ)

Color schedule:
  22-04  Dark red  #88   Night
  04-06  Orange    #214  Dawn
  06-08  Yellow    #226  Sunrise
  08-11  Green     #34   Morning
  11-13  Cyan      #51   Midday
  13-15  White     #231  Peak
  15-17  Cyan      #51   Afternoon
  17-19  Green     #34   Evening
  19-21  Yellow    #226  Sunset
  21-22  Orange    #214  Dusk
  22-24  Dark red  #88   Night
"""

import curses
import time
import sys
import os
from datetime import datetime
from zoneinfo import ZoneInfo

DIGITS = {
    '0': ["###", "# #", "# #", "# #", "###"],
    '1': ["  #", "  #", "  #", "  #", "  #"],
    '2': ["###", "  #", "###", "#  ", "###"],
    '3': ["###", "  #", "###", "  #", "###"],
    '4': ["# #", "# #", "###", "  #", "  #"],
    '5': ["###", "#  ", "###", "  #", "###"],
    '6': ["###", "#  ", "###", "# #", "###"],
    '7': ["###", "  #", "  #", "  #", "  #"],
    '8': ["###", "# #", "###", "# #", "###"],
    '9': ["###", "# #", "###", "  #", "###"],
    ':': ["   ", " # ", "   ", " # ", "   "],
    ' ': ["   ", "   ", "   ", "   ", "   "],
}

SCALE = 2

COLOR_SCHEDULE = [
    ( 0,  4,  88),   # Night      - dark red
    ( 4,  6, 214),   # Dawn       - orange
    ( 6,  8, 226),   # Sunrise    - yellow
    ( 8, 11,  34),   # Morning    - green
    (11, 13,  51),   # Midday     - cyan
    (13, 15, 231),   # Peak       - white
    (15, 17,  51),   # Afternoon  - cyan
    (17, 19,  34),   # Evening    - green
    (19, 21, 226),   # Sunset     - yellow
    (21, 22, 214),   # Dusk       - orange
    (22, 24,  88),   # Night      - dark red
]

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

    char_w = 3 * SCALE
    gap = SCALE

    total_w = len(time_str) * (char_w + gap) - gap
    clock_h = 5 * SCALE
    total_h = clock_h + 2

    start_y = (h - total_h) // 2
    start_x = (w - total_w) // 2

    x = start_x
    for ch in time_str:
        draw_ch = ' ' if (blink_colon and ch == ':' and not show_colon) else ch
        draw_char(stdscr, draw_ch, start_y, x, color_pair)
        x += char_w + gap

    date_y = start_y + clock_h + 1
    date_x = (w - len(date_str)) // 2
    try:
        stdscr.addstr(date_y, max(0, date_x), date_str, color_pair)
    except curses.error:
        pass

    stdscr.refresh()

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
        if args[i] == '-f' and i + 1 < len(args):
            fmt = args[i+1]
            i += 2
        elif args[i] == '-s' and i + 1 < len(args):
            scale = max(1, int(args[i+1]))
            i += 2
        elif args[i] == '-z' and i + 1 < len(args):
            ref_tz = args[i+1]
            i += 2
        elif args[i] == '-B':
            blink_colon = True
            i += 1
        elif args[i] == '-n':
            no_quit = True
            i += 1
        elif args[i] == '-S':
            show_seconds = True
            i += 1
        else:
            i += 1

    return fmt, blink_colon, no_quit, scale, show_seconds, ref_tz

if __name__ == '__main__':
    fmt, blink_colon, no_quit, scale, show_seconds, ref_tz = parse_args()
    curses.wrapper(main, fmt, blink_colon, no_quit, scale, show_seconds, ref_tz)