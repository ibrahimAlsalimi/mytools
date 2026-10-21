# tools

Personal scripts for Hyprland (ML4W dotfiles).

## Layout

    bin/          one file per tool        -> ~/.local/bin/<name without extension>
    config/       mirrors ~/.config        -> ~/.config/<same path>
    install.sh    links everything, removes stale links, checks deps, reloads Hyprland
    new-tool.sh   scaffolds a new tool

## Tools

| Tool | Key | What it does |
|---|---|---|
| `pdfpick` | SUPER+P | TUI picker that opens PDFs in mupdf-gl |
| `fzncopy` | SUPER+F | fzf file picker, copies the absolute path |

`config/hypr/custom.lua` holds my window rules and keybinds. ML4W loads
`~/.config/hypr/custom.lua` and leaves it alone on updates, so put binds there,
never in `conf/keybindings/default.lua`.

## Adding a tool

    ./new-tool.sh mytool        # bash, or: ./new-tool.sh mytool py

1. Edit `bin/mytool.sh` and list the commands it needs on its `# deps:` line.
2. Optional: add a keybind in `config/hypr/custom.lua` calling `~/.local/bin/mytool`.
3. Add it to the table above, then `git commit`.

A tool that needs several files: keep the entry point in `bin/` and put the rest in
`lib/<tool>/`, and have the entry point resolve its real path (`readlink -f`) to find them.

## After an update / on a new machine

    ./install.sh
