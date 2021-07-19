import unittest

import torch
import torchvision.transforms as transforms
import torchvision.transforms.functional as F


class TestTorchvision(unittest.TestCase):
    def test_float_to_float(self):
        input_dtype=torch.float32
        output_dtype=torch.float64
        input_image = torch.tensor((0.0, 1.0), dtype=input_dtype)
        transform = transforms.ConvertImageDtype(output_dtype)
        transform_script = torch.jit.script(F.convert_image_dtype)

        output_image = transform(input_image)
        output_image_script = transform_script(input_image, output_dtype)

        # TODO(b/181966788) Uncomment after upgrade to pytorch 1.9.0 is done.
        # torch.testing.assert_close(output_image_script, output_image, rtol=0.0, atol=1e-6)

        actual_min, actual_max = output_image.tolist()

        self.assertAlmostEqual(0, actual_min)
        self.assertAlmostEqual(1, actual_max)