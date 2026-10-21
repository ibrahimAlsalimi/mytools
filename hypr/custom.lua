-- pdfpick (kitty --class pdfpick)
hl.window_rule({
    name = "pdfpick",
    match = {class = "pdfpick"},
    float = true,
    size = "1000 750",
    move = "20 345"  -- left side of the 2560x1440 screen, vertically centered
})
-- MuPDF mupdf-gl has no class, so match its "file.pdf - page/pages" title)
hl.window_rule({
    name = "mupdf-gl",
    match = {class = "^$", title = ".*\\.pdf - [0-9]+/[0-9]+$"},
    float = true,
    size = "1100 1300",
    move = "1440 70"  -- right side of the 2560x1440 screen, 20px from the edge
})

-- Keybinds for my own tools (kept here so ML4W updates don't overwrite them)
hl.bind("SUPER + P", hl.dsp.exec_cmd("kitty --class pdfpick -e " .. os.getenv("HOME") .. "/.local/bin/pdfpick " .. os.getenv("HOME")), { description = "Pick a PDF and open it in MuPDF" })
hl.bind("SUPER + Z", hl.dsp.exec_cmd("kitty ssysr"), { description = "open ssysr" })
hl.bind("SUPER + F", hl.dsp.exec_cmd("kitty --class fzncopy -e " .. os.getenv("HOME") .. "/.local/bin/fzncopy"), { description = "Pick a file with fzf and copy its path" })
