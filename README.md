# tools

Personal scripts for Hyprland (ML4W dotfiles).

| Tool | Key | What it does |
|---|---|---|
| `pdfpick` | SUPER+P | TUI picker that opens PDFs in mupdf-gl |
| `fzncopy` | SUPER+F | fzf file picker, copies the absolute path |

`hypr/custom.lua` holds my window rules and keybinds. ML4W loads `~/.config/hypr/custom.lua`
and leaves it alone on updates.

## Install / after an update

    ./install.sh

Re-links `~/.local/bin/{pdfpick,fzncopy}` and `~/.config/hypr/custom.lua` into this repo,
checks dependencies, and reloads Hyprland.
