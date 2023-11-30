import unittest
from unittest import mock

import kagglehub


class TestKagglehub(unittest.TestCase):
    def test_login(self):
        with self.assertLogs('kagglehub', level='INFO') as l:
            with mock.patch("builtins.input") as mock_input:
                mock_input.side_effect = ["lastplacelarry", "some-key"]
                # Disabling credentials validation since network access is disabled in unittest.
                kagglehub.login(validate_credentials=False)

                self.assertIn("credentials set", l.output[0])
            


        