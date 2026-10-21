#!/usr/bin/env python3
# deps: python3 mupdf-gl
"""pdfpick - a glow-style TUI that lists PDF files and opens the chosen one in mupdf-gl.

Usage:
    pdfpick [DIRECTORY] [-a]

    DIRECTORY   where to search (default: current directory)
    -a          include hidden files and directories

Keys:
    type        filter by file name / path
    Up/Down     move (also Ctrl-P / Ctrl-N)
    PgUp/PgDn   move a page
    Enter       open the selected PDF using the current mode
    Shift-N     mode: new window, then quit pdfpick (default)
    Shift-R     mode: replace the last window pdfpick opened, keep pdfpick open
    Shift-K     mode: new window, keep pdfpick open
    Backspace   delete filter character
    Ctrl-U      clear filter
    Esc         quit
"""

import curses
import os
import shutil
import subprocess
import sys
import time

VIEWER = "mupdf-gl"
MODES = {
    "N": ("new", "new window, quit"),
    "R": ("replace", "replace window"),
    "K": ("keep", "new window, keep open"),
}
PID_FILE = os.path.join(os.environ.get("XDG_RUNTIME_DIR") or os.path.expanduser("~/.cache"),
                        "pdfpick.pid")


def find_pdfs(root, show_hidden):
    pdfs = []
    for dirpath, dirnames, filenames in os.walk(root):
        if not show_hidden:
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        dirnames.sort()
        for name in sorted(filenames):
            if name.lower().endswith(".pdf") and (show_hidden or not name.startswith(".")):
                full = os.path.join(dirpath, name)
                try:
                    st = os.stat(full)
                except OSError:
                    continue
                pdfs.append((full, st.st_size, st.st_mtime))
    return pdfs


def human_size(n):
    for unit in ("B", "K", "M", "G"):
        if n < 1024:
            return f"{n:.0f}{unit}" if unit == "B" else f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}T"


def human_age(mtime):
    secs = time.time() - mtime
    for limit, div, unit in ((60, 1, "s"), (3600, 60, "m"), (86400, 3600, "h"),
                             (86400 * 30, 86400, "d"), (86400 * 365, 86400 * 30, "mo")):
        if secs < limit:
            return f"{int(secs // div)}{unit} ago"
    return f"{int(secs // (86400 * 365))}y ago"


def matches(query, path):
    """Every space-separated word in the query must appear in the path (case-insensitive)."""
    p = path.lower()
    return all(word in p for word in query.lower().split())


def close_last_viewer():
    """Kill the viewer pdfpick opened last, if it is still running."""
    try:
        with open(PID_FILE) as f:
            pid = int(f.read().strip())
        with open(f"/proc/{pid}/comm") as f:
            if f.read().strip() != VIEWER:
                return  # pid was reused by something else
        os.kill(pid, 15)
    except (OSError, ValueError):
        pass


def open_pdf(path, replace=False):
    if replace:
        close_last_viewer()
    proc = subprocess.Popen(
        [VIEWER, path],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,  # keep viewer running after pdfpick exits
    )
    try:
        os.makedirs(os.path.dirname(PID_FILE), exist_ok=True)
        with open(PID_FILE, "w") as f:
            f.write(str(proc.pid))
    except OSError:
        pass


def draw(scr, root, items, query, sel, top, status, mode):
    scr.erase()
    h, w = scr.getmaxyx()

    def put(y, x, text, attr=0):
        if 0 <= y < h and x < w:
            try:
                scr.addnstr(y, x, text, w - x - 1, attr)
            except curses.error:
                pass

    # header
    put(0, 1, " pdfpick ", curses.color_pair(1) | curses.A_BOLD)
    mode_label = f" mode: {MODES[mode][1]} "
    put(0, 11, mode_label, curses.color_pair(3) | curses.A_REVERSE | curses.A_BOLD)
    put(0, 12 + len(mode_label), f"{len(items)} PDFs in {root}", curses.color_pair(4))
    # filter line
    put(2, 1, "Find: ", curses.color_pair(2) | curses.A_BOLD)
    put(2, 7, query + "█", curses.A_BOLD)

    list_top = 4
    rows = max(1, (h - list_top - 2) // 3)  # each entry uses 3 lines, like glow
    for i in range(rows):
        idx = top + i
        if idx >= len(items):
            break
        full, size, mtime = items[idx]
        rel = os.path.relpath(full, root)
        name = os.path.basename(full)
        y = list_top + i * 3
        if idx == sel:
            put(y, 1, "│", curses.color_pair(2) | curses.A_BOLD)
            put(y + 1, 1, "│", curses.color_pair(2) | curses.A_BOLD)
            put(y, 3, name, curses.color_pair(2) | curses.A_BOLD)
            put(y + 1, 3, f"{rel}  ·  {human_size(size)}  ·  {human_age(mtime)}", curses.color_pair(3))
        else:
            put(y, 3, name, curses.A_BOLD)
            put(y + 1, 3, f"{rel}  ·  {human_size(size)}  ·  {human_age(mtime)}", curses.color_pair(4))

    if not items:
        put(list_top, 3, "No matching PDF files.", curses.color_pair(4))

    # footer
    help_text = "↑/↓ move • enter open • shift+N/R/K mode • type to filter • ctrl-u clear • esc quit"
    put(h - 1, 1, status or help_text, curses.color_pair(4))
    scr.refresh()
    return rows


def run(scr, root, pdfs):
    curses.curs_set(0)
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_MAGENTA)
    curses.init_pair(2, curses.COLOR_MAGENTA, -1)
    curses.init_pair(3, curses.COLOR_CYAN, -1)
    curses.init_pair(4, 8 if curses.COLORS > 8 else curses.COLOR_WHITE, -1)

    query, sel, top, status, mode = "", 0, 0, "", "N"
    while True:
        items = [p for p in pdfs if matches(query, os.path.relpath(p[0], root))]
        sel = max(0, min(sel, len(items) - 1))
        h, _ = scr.getmaxyx()
        rows = max(1, (h - 6) // 3)
        if sel < top:
            top = sel
        elif sel >= top + rows:
            top = sel - rows + 1

        draw(scr, root, items, query, sel, top, status, mode)
        status = ""
        key = scr.get_wch()

        if key in ("\x1b",):
            return
        elif key in (curses.KEY_UP, "\x10"):
            sel -= 1
        elif key in (curses.KEY_DOWN, "\x0e"):
            sel += 1
        elif key == curses.KEY_PPAGE:
            sel -= rows
        elif key == curses.KEY_NPAGE:
            sel += rows
        elif key == curses.KEY_HOME:
            sel = 0
        elif key == curses.KEY_END:
            sel = len(items) - 1
        elif key in ("\n", "\r", curses.KEY_ENTER):
            if items:
                name = os.path.basename(items[sel][0])
                action = MODES[mode][0]
                open_pdf(items[sel][0], replace=(action == "replace"))
                if action == "new":
                    return
                status = (f"Replaced window with {name}" if action == "replace"
                          else f"Opened {name} in {VIEWER}")
        elif key in (curses.KEY_BACKSPACE, "\x7f", "\b"):
            query = query[:-1]
            sel = top = 0
        elif key == "\x15":  # Ctrl-U
            query = ""
            sel = top = 0
        elif key == curses.KEY_RESIZE:
            pass
        elif key in MODES:  # Shift-N / Shift-R / Shift-K
            mode = key
            status = f"Mode: {MODES[mode][1]}"
        elif isinstance(key, str) and key.isprintable():
            query += key
            sel = top = 0


def main():
    args = sys.argv[1:]
    if "-h" in args or "--help" in args:
        print(__doc__)
        return
    show_hidden = "-a" in args
    args = [a for a in args if a != "-a"]
    root = os.path.abspath(os.path.expanduser(args[0] if args else "."))

    if not os.path.isdir(root):
        sys.exit(f"pdfpick: not a directory: {root}")
    if not shutil.which(VIEWER):
        sys.exit(f"pdfpick: {VIEWER} not found in PATH")

    print(f"Searching for PDFs in {root} ...", end="\r", flush=True)
    pdfs = find_pdfs(root, show_hidden)
    os.environ.setdefault("ESCDELAY", "25")  # make Esc respond instantly
    try:
        curses.wrapper(run, root, pdfs)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
