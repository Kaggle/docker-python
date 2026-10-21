import subprocess
import unittest

import certifi
import pip
from packaging.version import Version


class TestCertifi(unittest.TestCase):
    # GHSA-6q48-6c7w-9gw2: emSign ECC Root CA - G3 intermediates have compromised keys.
    def test_emsign_ecc_g3_root_removed(self):
        self.assertGreaterEqual(Version(certifi.__version__), Version("2026.10.19"))
        with open(certifi.where()) as f:
            self.assertNotIn("emSign ECC Root CA - G3", f.read())

    def test_pip_vendored_certifi_patched(self):
        self.assertGreaterEqual(Version(pip.__version__), Version("26.2.2"))

    # GHSA-hq85-5cpj-mr62: uv vendors its own CA bundle.
    def test_uv_vendored_certs_patched(self):
        version = subprocess.check_output(["uv", "--version"], text=True).split()[1]
        self.assertGreaterEqual(Version(version), Version("0.13.4"))
