import unittest

class TestBigQueryStorage(unittest.TestCase):

    def test_ensure_bq_storage_is_not_installed(self):
        # b/183041606#comment5: Ensures bigquery_storage is not installed.
        # bigquery falls back on using regular BQ queries which are supported by the BQ proxy.
        with self.assertRaises(ImportError):
            from google.cloud import bigquery_storage