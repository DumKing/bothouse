import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location(
    "minimum", Path(__file__).with_name("verify-macos-minimum.py")
)
minimum = importlib.util.module_from_spec(spec)
spec.loader.exec_module(minimum)


class MinimumVersionTests(unittest.TestCase):
    def test_rejects_reported_intel_release_regression(self):
        commands = "Load command 11\n cmd LC_BUILD_VERSION\n sdk 27.0\n minos 27.0\n"
        with self.assertRaisesRegex(ValueError, "requires macOS 27.0"):
            minimum.verify(commands, "12.0")

    def test_accepts_compatible_intel_build(self):
        commands = "Load command 11\n cmd LC_BUILD_VERSION\n sdk 27.0\n minos 15.0\n"
        self.assertEqual(minimum.verify(commands, "15.0"), ["15.0"])

    def test_legacy_load_command(self):
        commands = "Load command 9\n cmd LC_VERSION_MIN_MACOSX\n version 12.0\n sdk 15.0\n"
        self.assertEqual(minimum.verify(commands, "15.0"), ["12.0"])

    def test_missing_target_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "No macOS deployment target"):
            minimum.verify("Load command 1\n cmd LC_UUID\n", "15.0")


if __name__ == "__main__":
    unittest.main()
