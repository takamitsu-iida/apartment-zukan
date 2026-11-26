import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import ExifTags, Image
from PIL.TiffImagePlugin import IFDRational


SCRIPT = Path(__file__).with_name("extract_gps.py")
GPS = ExifTags.GPS


def gps_data(latitude_ref, latitude, longitude_ref, longitude):
    return {
        GPS.GPSLatitudeRef: latitude_ref,
        GPS.GPSLatitude: latitude,
        GPS.GPSLongitudeRef: longitude_ref,
        GPS.GPSLongitude: longitude,
    }


class ExtractGpsTests(unittest.TestCase):
    def run_script(self, path):
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(path)],
            capture_output=True,
            text=True,
        )

    def run_with_image(self, gps=None):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "photo.jpg"
            image = Image.new("RGB", (1, 1))
            if gps is None:
                image.save(path)
            else:
                exif = Image.Exif()
                exif[ExifTags.IFD.GPSInfo] = gps
                image.save(path, exif=exif)
            return self.run_script(path)

    def test_extracts_and_rounds_coordinates_as_json(self):
        gps = gps_data(
            "N",
            (IFDRational(35), IFDRational(24), IFDRational(469, 20)),
            "E",
            (IFDRational(139), IFDRational(35), IFDRational(373, 25)),
        )
        result = self.run_with_image(gps)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout,
            '{\n  "lat": 35.406514,\n  "lng": 139.587478\n}\n',
        )

    def test_southern_and_western_coordinates_are_negative(self):
        gps = gps_data(
            "S",
            (IFDRational(12), IFDRational(30), IFDRational(0)),
            "W",
            (IFDRational(45), IFDRational(15), IFDRational(30)),
        )
        result = self.run_with_image(gps)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout,
            '{\n  "lat": -12.500000,\n  "lng": -45.258333\n}\n',
        )

    def test_zero_coordinates_are_valid(self):
        zero = (IFDRational(0), IFDRational(0), IFDRational(0))
        result = self.run_with_image(gps_data("N", zero, "E", zero))

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, '{\n  "lat": 0.000000,\n  "lng": 0.000000\n}\n')

    def test_missing_gps_is_an_error(self):
        incomplete = {GPS.GPSLatitudeRef: "N"}
        for gps in (None, incomplete):
            with self.subTest(gps=gps):
                result = self.run_with_image(gps)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")
                self.assertIn("GPS情報がありません", result.stderr)

    def test_invalid_gps_is_an_error(self):
        zero = (IFDRational(0), IFDRational(0), IFDRational(0))
        over_limit = (IFDRational(90), IFDRational(1), IFDRational(0))
        for gps in (
            gps_data("X", zero, "E", zero),
            gps_data("N", over_limit, "E", zero),
        ):
            with self.subTest(gps=gps):
                result = self.run_with_image(gps)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")
                self.assertIn("GPS情報が不正です", result.stderr)

    def test_missing_image_is_an_error(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_script(Path(directory) / "missing.jpg")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("エラー:", result.stderr)


if __name__ == "__main__":
    unittest.main()
