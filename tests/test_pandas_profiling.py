import json
import unittest

import pandas as pd
from pandas_profiling import ProfileReport


class TestPandasProfiling(unittest.TestCase):
    def setUp(self):
        self.data = pd.DataFrame(data={"col1": [1, 2], "col2": [3, 4]})
        self.report = ProfileReport(self.data)
    
    def test_html_report_repr(self):
        assert repr(self.report) == ""

    def test_json_report(self):
        report_json = self.report.to_json()
        data = json.loads(report_json)
        assert set(data.keys()) == {
            "analysis",
            "correlations",
            "duplicates",
            "alerts",
            "missing",
            "package",
            "sample",
            "scatter",
            "table",
            "variables",
        }
