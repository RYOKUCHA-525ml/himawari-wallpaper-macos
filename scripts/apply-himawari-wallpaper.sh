#!/bin/zsh
set -euo pipefail

DIR="$HOME/Pictures/HimawariWallpaper"
SRC="$DIR/himawari_wallpaper.jpg"
STAMP=$(date +%Y%m%d_%H%M%S)
DST="$DIR/himawari_wallpaper_$STAMP.jpg"

cp "$SRC" "$DST"

osascript <<EOF
tell application "System Events"
  repeat with d in desktops
    set picture of d to "$DST"
  end repeat
end tell
EOF

killall Dock || true

cd "$DIR"
ls -1t himawari_wallpaper_*.jpg 2>/dev/null | tail -n +6 | xargs -I {} rm -f "{}"
