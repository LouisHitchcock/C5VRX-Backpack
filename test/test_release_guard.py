"""Ensure release packaging rejects private identity and missing metadata."""
import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import unittest

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("package_c5vrx", root / "tools/package_c5vrx.py")
packager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(packager)


class ReleaseGuardTest(unittest.TestCase):
    def check_image(self, options, compiled=b""):
        # Minimal one-segment ESP32 image with options at the upstream offset.
        header = bytes([0xE9, 1]) + bytes(22)
        payload = b"DATA" + compiled
        data = header + struct.pack("<II", 0, len(payload)) + payload
        end = ((len(data) + 16) & ~15) + 32
        data += bytes(end - len(data)) + json.dumps(options).encode() + b"\0"
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "firmware.bin"
            path.write_bytes(data)
            return packager.verify_unbound(path)

    def test_generic_metadata_is_allowed(self):
        opts = {"product-name": "test", "flash-discriminator": 1}
        self.assertEqual(self.check_image(opts), opts)

    def test_identity_and_credentials_are_refused(self):
        for key in ("uid", "wifi-ssid", "wifi-password", "unknown"):
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.check_image({"product-name": "test", "flash-discriminator": 1, key: [1, 2, 3]})

    def test_missing_metadata_is_refused(self):
        for options in ({}, [], {"product-name": "test"}):
            with self.subTest(options=options), self.assertRaises(ValueError):
                self.check_image(options)

    def test_compiled_phrase_is_refused_even_without_uid(self):
        with self.assertRaises(ValueError):
            self.check_image({"product-name": "test", "flash-discriminator": 1},
                             b'-DMY_BINDING_PHRASE="test-only-placeholder"')


if __name__ == "__main__":
    unittest.main()
