# Himawari Wallpaper for macOS

A macOS wallpaper updater that downloads Himawari real-time image tiles, stitches them into a high-resolution image, crops a selected region, and sets it as the desktop wallpaper.

## Features

- Downloads Himawari real-time image tiles
- Supports high-resolution 20d tile mode
- Crops to East Asia, Japan, or custom bounding boxes
- Updates the macOS wallpaper automatically
- Avoids macOS wallpaper cache by applying a timestamped copy

## Data source

This project fetches image tiles from NICT Himawari Real-Time Web.

- NICT Himawari Real-Time Web: https://himawari8.nict.go.jp/
- JMA Himawari Real-Time Image: https://www.data.jma.go.jp/mscweb/data/himawari/

Satellite imagery and related data are provided by their respective organizations.
This repository does not redistribute satellite images.

## Install

Install Pillow:

    python3 -m pip install --user pillow

Copy scripts:

    mkdir -p ~/bin
    cp scripts/himawari-wallpaper.py ~/bin/
    cp scripts/apply-himawari-wallpaper.sh ~/bin/
    chmod +x ~/bin/himawari-wallpaper.py
    chmod +x ~/bin/apply-himawari-wallpaper.sh

## Run once: East Asia

    HIMAWARI_TILES=20 \
    HIMAWARI_BBOX_SOUTH=5 \
    HIMAWARI_BBOX_WEST=95 \
    HIMAWARI_BBOX_NORTH=55 \
    HIMAWARI_BBOX_EAST=150 \
    HIMAWARI_PADDING=1.18 \
    python3 ~/bin/himawari-wallpaper.py && ~/bin/apply-himawari-wallpaper.sh

## License

Code is licensed under the MIT License.
Satellite imagery is not covered by this license.
