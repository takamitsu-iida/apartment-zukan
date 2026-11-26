#!/usr/bin/env python3
"""画像を縮小してEXIF情報を除去する。"""

import argparse
import sys
from io import BytesIO
from pathlib import Path

try:
    from PIL import Image, ImageOps
except ModuleNotFoundError as error:
    if error.name != "PIL":
        raise
    print("エラー: Pillowが必要です。READMEの手順でインストールしてください。", file=sys.stderr)
    sys.exit(1)


def optimize_image(image_path, output_path):
    with Image.open(image_path) as source:
        source_format = source.format
        if source_format not in ("JPEG", "MPO", "PNG", "WEBP"):
            raise ValueError("JPEG、PNG、WebP形式の画像を指定してください。")
        if source_format != "MPO" and getattr(source, "is_animated", False):
            raise ValueError("アニメーション画像には対応していません。")

        output_format = "JPEG" if source_format == "MPO" else source_format
        if Image.registered_extensions().get(output_path.suffix.lower()) != output_format:
            raise ValueError("出力先には元画像と同じ形式の拡張子を指定してください。")

        icc_profile = source.info.get("icc_profile")
        image = ImageOps.exif_transpose(source)
        if "transparency" in image.info:
            image = image.convert("RGBA")
        elif image.mode == "P":
            image = image.convert("RGB")
        elif image.mode == "1":
            image = image.convert("L")

        image.thumbnail((1000, 1000), Image.Resampling.LANCZOS)
        image.info.clear()

        options = {}
        if icc_profile:
            options["icc_profile"] = icc_profile
        if output_format in ("JPEG", "WEBP"):
            options["quality"] = 85
        if output_format == "JPEG":
            options["optimize"] = True

        with BytesIO() as buffer:
            image.save(buffer, format=output_format, **options)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with output_path.open("xb") as output:
                output.write(buffer.getvalue())


def main():
    parser = argparse.ArgumentParser(description="写真を縮小してEXIF情報を除去します。")
    parser.add_argument("image", type=Path, help="元画像のパス")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="保存先（省略時は元画像のフォルダー内のoptimized/）",
    )
    args = parser.parse_args()
    output_path = args.output or args.image.parent / "optimized" / args.image.name

    try:
        optimize_image(args.image, output_path)
    except FileExistsError as error:
        parser.exit(1, f"エラー: 既存のファイルは上書きしません: {error.filename}\n")
    except (OSError, ValueError) as error:
        parser.exit(1, f"エラー: {error}\n")

    print(f"保存しました: {output_path}")


if __name__ == "__main__":
    main()
