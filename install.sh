#!/usr/bin/env bash
# Link the tools and Hyprland custom config into place and check dependencies.
# Safe to re-run (e.g. after an ML4W or system update).
set -u
repo=$(cd "$(dirname "$0")" && pwd)
bin="$HOME/.local/bin"

# link SRC DEST: symlink DEST -> SRC, backing up a real file that's in the way
link() {
    if [ -e "$2" ] && [ ! -L "$2" ]; then
        mv -- "$2" "$2.bak.$(date +%Y%m%d%H%M%S)"
        echo "backed up existing $2"
    fi
    ln -sfn -- "$1" "$2"
    echo "linked $2 -> $1"
}

mkdir -p "$bin"
chmod +x "$repo/pdfpick.py" "$repo/shell/fzncopy.sh"
link "$repo/pdfpick.py" "$bin/pdfpick"
link "$repo/shell/fzncopy.sh" "$bin/fzncopy"
link "$repo/hypr/custom.lua" "$HOME/.config/hypr/custom.lua"

missing=0
for cmd in python3 kitty fzf wl-copy notify-send mupdf-gl; do
    if ! command -v "$cmd" >/dev/null; then
        echo "missing dependency: $cmd"
        missing=1
    fi
done
[ "$missing" = 0 ] && echo "all dependencies found"

command -v hyprctl >/dev/null && hyprctl reload >/dev/null && echo "hyprland reloaded"
