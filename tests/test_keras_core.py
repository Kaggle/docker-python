import unittest

import keras_cv
import keras_core as keras

class TestKerasCV(unittest.TestCase):
    def test_detect(self):
        image = keras.utils.load_img('/input/tests/data/face.jpg')
        image_resized = ops.image.resize(image, (640, 640))[None, ...]

        model = keras_cv.models.YOLOV8Detector.from_preset(
            "yolo_v8_m_pascalvoc",
            bounding_box_format="xywh",
            load_weights=False, # load randomly initialized model from preset architecture with weights
        )
        predictions = model.predict(image_resized)
        self.assertEqual(1000, len(top_classes))