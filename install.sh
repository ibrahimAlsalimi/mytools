#!/usr/bin/env bash
# Link every tool and config file from this repo into place and check dependencies.
# Safe to re-run (e.g. after an ML4W or system update, or after adding a tool).
#
#   bin/<name>.<ext>   -> ~/.local/bin/<name>
#   config/<path>      -> ~/.config/<path>
#
# Each file can list the commands it needs on a "deps:" comment line.
set -u
repo=$(cd "$(dirname "$0")" && pwd)
bin="$HOME/.local/bin"

# link SRC DEST: symlink DEST -> SRC, backing up a real file that's in the way
link() {
    if [ -e "$2" ] && [ ! -L "$2" ]; then
        mv -- "$2" "$2.bak.$(date +%Y%m%d%H%M%S)"
        echo "backed up existing $2"
    fi
    mkdir -p -- "$(dirname -- "$2")"
    [ "$(readlink -- "$2")" = "$1" ] && return
    ln -sfn -- "$1" "$2"
    echo "linked $2 -> $1"
}

# tools
for src in "$repo"/bin/*; do
    [ -f "$src" ] || continue
    chmod +x "$src"
    name=$(basename -- "$src")
    link "$src" "$bin/${name%.*}"
done

# configs
while IFS= read -r -d '' src; do
    link "$src" "$HOME/.config/${src#"$repo/config/"}"
done < <(find "$repo/config" -type f -print0)

# remove links in ~/.local/bin that point at tools no longer in the repo
for l in "$bin"/*; do
    [ -L "$l" ] || continue
    target=$(readlink -- "$l")
    case $target in
        "$repo"/*) [ -e "$target" ] || { rm -- "$l"; echo "removed stale link $l"; } ;;
    esac
done

# dependencies
missing=0
for cmd in $(grep -rhoP '(#|--) deps:\K.*' "$repo/bin" "$repo/config" | tr ' ' '\n' | sort -u); do
    if ! command -v "$cmd" >/dev/null; then
        echo "missing dependency: $cmd"
        missing=1
    fi
done
[ "$missing" = 0 ] && echo "all dependencies found"

command -v hyprctl >/dev/null && hyprctl reload >/dev/null && echo "hyprland reloaded"
