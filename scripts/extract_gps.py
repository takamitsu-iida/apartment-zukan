#!/usr/bin/env python3
"""画像のEXIF情報から緯度・経度を取得する。"""

import argparse
import sys
from pathlib import Path

try:
    from PIL import ExifTags, Image
except ModuleNotFoundError as error:
    if error.name != "PIL":
        raise
    print("エラー: Pillowが必要です。READMEの手順でインストールしてください。", file=sys.stderr)
    sys.exit(1)


def to_decimal(values, reference, valid_references, limit):
    if (
        reference not in valid_references
        or not isinstance(values, (tuple, list))
        or len(values) != 3
    ):
        raise ValueError("GPS情報が不正です。")

    try:
        degrees, minutes, seconds = map(float, values)
    except (TypeError, ValueError, ZeroDivisionError, OverflowError) as error:
        raise ValueError("GPS情報が不正です。") from error

    if not (0 <= degrees <= limit and 0 <= minutes < 60 and 0 <= seconds < 60):
        raise ValueError("GPS情報が不正です。")

    coordinate = degrees + minutes / 60 + seconds / 3600
    if coordinate > limit:
        raise ValueError("GPS情報が不正です。")
    return -coordinate if reference == valid_references[1] else coordinate


def extract_coordinates(image_path):
    with Image.open(image_path) as image:
        gps = image.getexif().get_ifd(ExifTags.IFD.GPSInfo)

    tags = ExifTags.GPS
    required = (
        tags.GPSLatitudeRef,
        tags.GPSLatitude,
        tags.GPSLongitudeRef,
        tags.GPSLongitude,
    )
    if not all(tag in gps for tag in required):
        raise ValueError("画像に緯度・経度のGPS情報がありません。")

    latitude = to_decimal(
        gps[tags.GPSLatitude], gps[tags.GPSLatitudeRef], ("N", "S"), 90
    )
    longitude = to_decimal(
        gps[tags.GPSLongitude], gps[tags.GPSLongitudeRef], ("E", "W"), 180
    )
    return latitude, longitude


def main():
    parser = argparse.ArgumentParser(description="写真のEXIF情報から緯度・経度を表示します。")
    parser.add_argument("image", type=Path, help="GPS情報を含む元画像のパス")
    args = parser.parse_args()

    try:
        latitude, longitude = extract_coordinates(args.image)
    except (OSError, ValueError) as error:
        parser.exit(1, f"エラー: {args.image}: {error}\n")

    print(f'{{\n  "lat": {latitude:.6f},\n  "lng": {longitude:.6f}\n}}')


if __name__ == "__main__":
    main()
