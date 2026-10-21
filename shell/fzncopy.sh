#!/usr/bin/env bash
# Pick a file with fzf (searching from $HOME or $1) and copy its absolute path to the clipboard.
cd "${1:-$HOME}" || exit 1
sel=$(fzf --prompt 'copy path> ') || exit
path=$(realpath -- "$sel")
setsid -f wl-copy -n -- "$path" </dev/null >/dev/null 2>&1
notify-send -t 2000 "Path copied" "$path" 2>/dev/null

