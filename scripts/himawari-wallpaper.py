#!/usr/bin/env python3
import io
import json
import math
import os
import subprocess
import sys
import urllib.request
import urllib.error
from PIL import Image

TILES = int(os.environ.get("HIMAWARI_TILES", "20"))
TILE_SIZE = 550

BBOX_SOUTH = float(os.environ.get("HIMAWARI_BBOX_SOUTH", "24.0"))
BBOX_WEST  = float(os.environ.get("HIMAWARI_BBOX_WEST",  "122.0"))
BBOX_NORTH = float(os.environ.get("HIMAWARI_BBOX_NORTH", "46.5"))
BBOX_EAST  = float(os.environ.get("HIMAWARI_BBOX_EAST",  "146.5"))

ASPECT_W = float(os.environ.get("HIMAWARI_ASPECT_W", "16"))
ASPECT_H = float(os.environ.get("HIMAWARI_ASPECT_H", "10"))
PADDING = float(os.environ.get("HIMAWARI_PADDING", "1.35"))

OUT_DIR = os.path.expanduser("~/Pictures/HimawariWallpaper")
OUT = os.path.join(OUT_DIR, "himawari_wallpaper.jpg")
TMP = os.path.join(OUT_DIR, "himawari_wallpaper.tmp.jpg")

SOURCES = [
    (
        "https://himawari8-dl.nict.go.jp/himawari8/img/D531106/latest.json",
        "https://himawari8-dl.nict.go.jp/himawari8/img/D531106",
    ),
    (
        "https://himawari8.nict.go.jp/img/D531106/latest.json",
        "https://himawari8.nict.go.jp/img/D531106",
    ),
    (
        "https://himawari9.nict.go.jp/img/D531106/latest.json",
        "https://himawari9.nict.go.jp/img/D531106",
    ),
]

HEADERS = {"User-Agent": "Mozilla/5.0 himawari-wallpaper-macos"}

def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def get_latest():
    last_error = None
    for latest_url, base_url in SOURCES:
        try:
            data = json.loads(fetch(latest_url).decode("utf-8"))
            return data["date"], base_url
        except Exception as e:
            last_error = e
    raise RuntimeError(f"latest.jsonを取得できませんでした: {last_error}")

def geostationary_pixel(lat_deg, lon_deg, image_size):
    sub_lon = math.radians(140.7)

    lat = math.radians(lat_deg)
    lon = math.radians(lon_deg)

    r_eq = 6378.137
    r_pol = 6356.7523
    h = 42164.0

    e2 = (r_eq * r_eq - r_pol * r_pol) / (r_eq * r_eq)
    phi_c = math.atan((r_pol * r_pol / (r_eq * r_eq)) * math.tan(lat))
    r_c = r_pol / math.sqrt(1 - e2 * math.cos(phi_c) * math.cos(phi_c))

    sx = h - r_c * math.cos(phi_c) * math.cos(lon - sub_lon)
    sy = -r_c * math.cos(phi_c) * math.sin(lon - sub_lon)
    sz = r_c * math.sin(phi_c)

    x = math.atan(sy / sx)
    y = math.atan(sz / math.sqrt(sx * sx + sy * sy))

    max_angle = math.radians(8.7)
    radius = image_size * 0.5 * 0.985

    px = image_size / 2 + radius * (x / max_angle)
    py = image_size / 2 - radius * (y / max_angle)

    return int(px), int(py)

def crop_japan(img):
    w, h = img.size

    points = []
    for i in range(9):
        lat = BBOX_SOUTH + (BBOX_NORTH - BBOX_SOUTH) * i / 8
        for j in range(9):
            lon = BBOX_WEST + (BBOX_EAST - BBOX_WEST) * j / 8
            points.append(geostationary_pixel(lat, lon, w))

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]

    left = min(xs)
    right = max(xs)
    top = min(ys)
    bottom = max(ys)

    cx = (left + right) // 2
    cy = (top + bottom) // 2

    crop_w = int((right - left) * PADDING)
    crop_h = int((bottom - top) * PADDING)

    target_aspect = ASPECT_W / ASPECT_H
    current_aspect = crop_w / crop_h

    if current_aspect < target_aspect:
        crop_w = int(crop_h * target_aspect)
    else:
        crop_h = int(crop_w / target_aspect)

    left = cx - crop_w // 2
    top = cy - crop_h // 2

    left = max(0, min(left, w - crop_w))
    top = max(0, min(top, h - crop_h))

    return img.crop((left, top, left + crop_w, top + crop_h))

def main():
    if TILES not in (4, 8, 16, 20):
        raise ValueError("HIMAWARI_TILES は 4, 8, 16, 20 のどれかにしてください")

    os.makedirs(OUT_DIR, exist_ok=True)

    date, base_url = get_latest()
    path_time = date.replace("-", "/").replace(" ", "/").replace(":", "")

    size = TILES * TILE_SIZE
    canvas = Image.new("RGB", (size, size), (0, 0, 0))

    print(f"latest: {date}")
    print(f"full resolution: {size}x{size}")
    print("view: Japan archipelago")
    print(f"padding: {PADDING}")

    for y in range(TILES):
        for x in range(TILES):
            url = f"{base_url}/{TILES}d/{TILE_SIZE}/{path_time}_{x}_{y}.png"
            try:
                tile = Image.open(io.BytesIO(fetch(url))).convert("RGB")
                canvas.paste(tile, (x * TILE_SIZE, y * TILE_SIZE))
                print(f"tile {x},{y} ok")
            except urllib.error.HTTPError as e:
                print(f"tile {x},{y} failed: HTTP {e.code}", file=sys.stderr)
            except Exception as e:
                print(f"tile {x},{y} failed: {e}", file=sys.stderr)

    cropped = crop_japan(canvas)
    cropped = cropped.resize((3840, 2400), Image.LANCZOS)

    cropped.save(TMP, "JPEG", quality=95)
    os.replace(TMP, OUT)

    script = f'tell application "System Events" to set picture of every desktop to "{OUT}"'
    subprocess.run(["osascript", "-e", script], check=False)

    print(f"saved: {OUT}")

if __name__ == "__main__":
    main()
