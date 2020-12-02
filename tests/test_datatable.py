import unittest
import datatable as dt
from datatable.internal import frame_integrity_check
from datatable import ltype

class TestDatatable(unittest.TestCase):    
    def test_fread(self):
        d0 = dt.fread(
            "L,T,U,D\n"
            "true,True,TRUE,1\n"
            "false,False,FALSE,0\n"
            ",,,\n"
        )
        frame_integrity_check(d0)
        assert d0.shape == (3, 4)
        assert d0.ltypes == (ltype.bool,) * 4
        assert d0.to_list() == [[True, False, None]] * 4
