import subprocess

def check_package_version(package):
    output = subprocess.check_output("pip show " + package, shell=True)
    for l in output.decode().split("\n"):
        if l.startswith("Version:"):
            return l.strip().split(" ")[1]

# Make sure the google-cloud-bigquery and google-cloud-bigquery-storage are on the same major version
class TestBigQueryStorage(unittest.TestCase):

    def test_bq_and_storage_compatible(self):
        bigquery_version = check_package_version("google-cloud-bigquery")
        bq_storage_verstion = check_package_version("google-cloud-bigquery-storage")
        self.assertEqual(bigquery_version[0], bq_storage_verstion[0])
        