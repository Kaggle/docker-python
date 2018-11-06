import unittest

from edafa import ClassPredictor

class myPredictor(ClassPredictor):
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)

	def predict_patches(self,patches):
		return 0

class TestEdafa(unittest.TestCase):
	def test_init(self):
		conf = '{"augs":["NO",\
		"FLIP_UD",\
		"FLIP_LR"],\
		"mean":"ARITH"}'
		p = myPredictor(conf)
		pred = p.predict_patches(None)
		self.assertEqual(0, pred)

