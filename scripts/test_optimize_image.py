import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import ExifTags, Image, ImageDraw, features
from PIL.TiffImagePlugin import IFDRational


SCRIPT = Path(__file__).with_name("optimize_image.py")


class OptimizeImageTests(unittest.TestCase):
    def run_script(self, source, output=None):
        command = [sys.executable, str(SCRIPT), str(source)]
        if output is not None:
            command.extend(["--output", str(output)])
        return subprocess.run(command, capture_output=True, text=True)

    def test_longest_side_is_limited_without_upscaling(self):
        cases = (
            ((2400, 1200), (1000, 500)),
            ((1200, 2400), (500, 1000)),
            ((320, 160), (320, 160)),
        )
        for size, expected in cases:
            with self.subTest(size=size), tempfile.TemporaryDirectory() as directory:
                source = Path(directory) / "photo.png"
                Image.new("RGB", size).save(source)

                result = self.run_script(source)
                self.assertEqual(result.returncode, 0, result.stderr)
                with Image.open(source.parent / "optimized" / source.name) as image:
                    self.assertEqual(image.size, expected)

    def test_orientation_is_applied_and_exif_is_removed(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "photo.jpg"
            image = Image.new("RGB", (20, 10), "red")
            ImageDraw.Draw(image).rectangle((10, 0, 19, 9), fill="blue")
            exif = Image.Exif()
            exif[274] = 6
            exif[271] = "Test Camera"
            exif[ExifTags.IFD.GPSInfo] = {
                ExifTags.GPS.GPSLatitudeRef: "N",
                ExifTags.GPS.GPSLatitude: (
                    IFDRational(35), IFDRational(24), IFDRational(0)
                ),
                ExifTags.GPS.GPSLongitudeRef: "E",
                ExifTags.GPS.GPSLongitude: (
                    IFDRational(139), IFDRational(35), IFDRational(0)
                ),
            }
            profile = b"test color profile"
            image.save(source, exif=exif, icc_profile=profile, quality=100, subsampling=0)
            original = source.read_bytes()
            with Image.open(source) as original_image:
                self.assertTrue(original_image.getexif().get_ifd(ExifTags.IFD.GPSInfo))

            result = self.run_script(source)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(source.read_bytes(), original)
            with Image.open(source.parent / "optimized" / source.name) as output:
                self.assertEqual(output.size, (10, 20))
                self.assertFalse(output.getexif())
                self.assertNotIn("exif", output.info)
                self.assertEqual(output.info.get("icc_profile"), profile)
                top = output.getpixel((5, 3))
                bottom = output.getpixel((5, 17))
                self.assertGreater(top[0], top[2])
                self.assertGreater(bottom[2], bottom[0])

    def test_palette_transparency_and_custom_output_are_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "palette.png"
            output_path = Path(directory) / "custom" / "result.png"
            image = Image.new("P", (16, 8), 0)
            image.putpalette([255, 0, 0] + [0, 0, 0] * 255)
            exif = Image.Exif()
            exif[271] = "Test Camera"
            image.save(source, transparency=0, exif=exif)

            result = self.run_script(source, output_path)
            self.assertEqual(result.returncode, 0, result.stderr)
            with Image.open(output_path) as output:
                self.assertEqual(output.mode, "RGBA")
                self.assertEqual(output.getpixel((0, 0)), (255, 0, 0, 0))
                self.assertFalse(output.getexif())

    @unittest.skipUnless(features.check("webp"), "Pillow was built without WebP support")
    def test_webp_transparency_and_exif_removal(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "photo.webp"
            image = Image.new("RGBA", (1400, 700), (20, 30, 40, 120))
            exif = Image.Exif()
            exif[271] = "Test Camera"
            image.save(source, lossless=True, exif=exif)

            result = self.run_script(source)
            self.assertEqual(result.returncode, 0, result.stderr)
            with Image.open(source.parent / "optimized" / source.name) as output:
                self.assertEqual(output.size, (1000, 500))
                self.assertEqual(output.getpixel((0, 0))[3], 120)
                self.assertFalse(output.getexif())

    def test_existing_files_are_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "photo.png"
            existing = Path(directory) / "existing.png"
            Image.new("RGB", (20, 10)).save(source)
            existing.write_bytes(b"existing file")
            original = source.read_bytes()

            for output_path in (source, existing):
                with self.subTest(output=output_path):
                    result = self.run_script(source, output_path)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("上書きしません", result.stderr)
                    self.assertEqual(source.read_bytes(), original)
                    self.assertEqual(existing.read_bytes(), b"existing file")

    def test_animated_images_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "animated.png"
            first = Image.new("RGB", (20, 10), "red")
            second = Image.new("RGB", (20, 10), "blue")
            first.save(source, save_all=True, append_images=[second], duration=100, loop=0)

            result = self.run_script(source)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("アニメーション画像", result.stderr)
            self.assertFalse((source.parent / "optimized" / source.name).exists())

    def test_output_format_must_match_input(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "photo.png"
            output = Path(directory) / "result.jpg"
            Image.new("RGB", (20, 10)).save(source)

            result = self.run_script(source, output)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("同じ形式", result.stderr)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
