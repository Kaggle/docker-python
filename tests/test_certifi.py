import glob
import os
import ssl
import subprocess
import unittest

import certifi
import pip
import wandb
from packaging.version import Version

SYSTEM_BUNDLE = "/etc/ssl/certs/ca-certificates.crt"


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

    # Covers both the merged bundle and the per-certificate files OpenSSL looks up by hash.
    def test_system_store_patched(self):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        for path in [SYSTEM_BUNDLE, *glob.glob("/etc/ssl/certs/*.pem")]:
            context.load_verify_locations(cafile=path)
        common_names = {
            value
            for cert in context.get_ca_certs()
            for rdn in cert["subject"]
            for key, value in rdn
            if key == "commonName"
        }
        # The other emSign roots are unaffected and should still be trusted.
        self.assertIn("emSign Root CA - G1", common_names)
        self.assertNotIn("emSign ECC Root CA - G3", common_names)

    def test_java_keystore_patched(self):
        listing = subprocess.check_output(
            ["keytool", "-list", "-v", "-cacerts", "-storepass", "changeit"], text=True
        )
        self.assertIn("emSign Root CA - G1", listing)
        self.assertNotIn("emSign ECC Root CA - G3", listing)

    # gcloud, gRPC, and Node vendor unpatched bundles, so they must use the system store.
    # Remove each of these alongside its workaround in Dockerfile.tmpl.
    def test_gcloud_uses_system_store(self):
        path = subprocess.check_output(
            ["gcloud", "config", "get", "core/custom_ca_certs_file"], text=True
        ).strip()
        self.assertEqual(SYSTEM_BUNDLE, path)

    def test_grpc_uses_system_store(self):
        self.assertEqual(SYSTEM_BUNDLE, os.environ.get("GRPC_DEFAULT_SSL_ROOTS_FILE_PATH"))

    def test_node_uses_system_store(self):
        self.assertIn("--use-openssl-ca", os.environ.get("NODE_OPTIONS", ""))
        # Node refuses to start if NODE_OPTIONS contains a flag it doesn't accept.
        subprocess.check_call(["node", "-e", ""])

    def test_wandb_binaries_patched(self):
        bin_dir = os.path.join(os.path.dirname(wandb.__file__), "bin")
        for name in os.listdir(bin_dir):
            with open(os.path.join(bin_dir, name), "rb") as f:
                # Not assertNotIn: its failure message would dump the whole binary.
                self.assertFalse(b"emSign ECC Root CA - G3" in f.read(), name)
