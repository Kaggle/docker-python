import tempfile
import unittest

from wand.exceptions import PolicyError
from wand.image import Image


class TestWand(unittest.TestCase):
    def test_read_png(self):
        with Image(filename='/input/tests/data/dot.png') as img:
            self.assertGreater(img.width, 0)
            self.assertGreater(len(img.make_blob(format='jpeg')), 0)

    def test_read_jpeg(self):
        with Image(filename='/input/tests/data/face.jpg') as img:
            self.assertGreater(img.width, 0)

    def test_read_tiff(self):
        with Image(filename='/input/tests/data/test.tif') as img:
            self.assertGreater(img.width, 0)


class TestImageMagickPolicy(unittest.TestCase):
    """Checks that patches/imagemagick-policy.xml blocks ImageTragick-class coders."""

    def assertBlocked(self, **kwargs):
        with self.assertRaises(PolicyError):
            with Image(**kwargs):
                pass

    def test_pdf_blocked(self):
        self.assertBlocked(filename='/input/tests/data/test.pdf')

    def test_pdf_blob_blocked(self):
        # Content sniffing must not bypass the policy.
        with open('/input/tests/data/test.pdf', 'rb') as f:
            self.assertBlocked(blob=f.read())

    def test_postscript_blocked(self):
        self.assertBlocked(blob=b'%!PS-Adobe-3.0\nshowpage\n')

    def test_indirect_file_read_blocked(self):
        with tempfile.NamedTemporaryFile('w', suffix='.txt') as f:
            f.write('secret')
            f.flush()
            self.assertBlocked(filename='label:@' + f.name)

    def test_text_blocked(self):
        self.assertBlocked(filename='text:/input/tests/data/text.txt')

    def test_mvg_blocked(self):
        self.assertBlocked(blob=b'push graphic-context\nviewbox 0 0 1 1\npop graphic-context\n', format='mvg')

    def test_msl_blocked(self):
        self.assertBlocked(blob=b'<?xml version="1.0"?><image></image>', format='msl')

    def test_url_blocked(self):
        self.assertBlocked(filename='https://www.kaggle.com/static/images/logos/kaggle-logo-transparent-300.png')
