#!/usr/bin/env bash
# Create a new tool in bin/ from a template and install it.
# Usage: ./new-tool.sh NAME [sh|py]
set -eu
repo=$(cd "$(dirname "$0")" && pwd)
name=${1:?usage: $0 NAME [sh|py]}
ext=${2:-sh}
file="$repo/bin/$name.$ext"

if compgen -G "$repo/bin/$name.*" >/dev/null || command -v "$name" >/dev/null; then
    echo "a tool or command named '$name' already exists" >&2
    exit 1
fi

case $ext in
    sh) cat > "$file" <<EOF
#!/usr/bin/env bash
# deps:
# $name - describe what it does.
set -eu

EOF
    ;;
    py) cat > "$file" <<EOF
#!/usr/bin/env python3
# deps: python3
"""$name - describe what it does."""

import sys


def main():
    pass


if __name__ == "__main__":
    sys.exit(main())
EOF
    ;;
    *) echo "unknown type '$ext' (use sh or py)" >&2; exit 1 ;;
esac

"$repo/install.sh" >/dev/null
echo "created $file, available as '$name'"
