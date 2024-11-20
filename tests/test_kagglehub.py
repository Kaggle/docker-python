import unittest
from unittest import mock

import kagglehub


class TestKagglehub(unittest.TestCase):
    def test_login(self):
        with self.assertLogs('kagglehub', level='INFO') as l:
            with mock.patch("builtins.input") as mock_input:
                with mock.patch("getpass.getpass") as mock_getpass:
                    mock_input.side_effect = ["lastplacelarry"]
                    mock_getpass.return_value = "some-key"

                    kagglehub.login(validate_credentials=False)

                    self.assertIn("credentials set", l.output[0])
