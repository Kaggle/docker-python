#!/bin/bash

# The following "sed" are to patch the current version of tf-df with
# a fix for keras 3. In essence, replaces the use of package name "tf.keras" with 
# "tf_keras"

sed -i "/import tensorflow_decision_forests as tfdf/a import tf_keras" /opt/conda/lib/python3.10/site-packages/tensorflow_decision_forests/__init__.py && \
sed -i -e "/import tensorflow as tf/a import tf_keras" \
       -e "/from yggdrasil_decision_forests.utils.distribute.implementations.grpc/a from tensorflow_decision_forests.keras import keras_internal" \
       -e '/try:/{:a;N;/backend = tf.keras.backend/!ba;d}'\
       /opt/conda/lib/python3.10/site-packages/tensorflow_decision_forests/keras/core.py && \
sed -i -e "s/from typing import Optional, List, Dict, Any, Union, NamedTuple/from typing import Any, Dict, List, NamedTuple, Optional, Union/g" \
       -e "/import tensorflow as tf/a from tensorflow_decision_forests.keras import keras_internal" \
       -e "/import tensorflow as tf/a import tf_keras" \
       -e '/layers = tf.keras.layers/{:a;N;/backend = tf.keras.backend/!ba;d}' \
       /opt/conda/lib/python3.10/site-packages/tensorflow_decision_forests/keras/core_inference.py && \
find /opt/conda/lib/python3.10/site-packages/tensorflow_decision_forests -type f -exec sed -i \
     -e "s/get_data_handler/keras_internal.get_data_handler/g" \
     -e 's/"models.Functional"/keras_internal.Functional/g' \
     -e "s/tf.keras.utils.unpack_x_y_sample_weight/keras_internal.unpack_x_y_sample_weight/g" \
     -e "s/tf.keras.utils.experimental/keras_internal/g" \
     {} \; && \
sed -i -e "/import tensorflow as tf/a import tf_keras" \
       -e "/from tensorflow_decision_forests.keras import core/a from tensorflow_decision_forests.keras import keras_internal" \
       -e '/layers = tf.keras.layers/{:a;N;/callbacks = tf.keras.callbacks/!ba;d}' \
       /opt/conda/lib/python3.10/site-packages/tensorflow_decision_forests/keras/keras_test.py && \
find /opt/conda/lib/python3.10/site-packages/tensorflow_decision_forests/keras -type f -exec sed -i \
     -e "s/ layers.Input/ tf_keras.layers.Input/g" \
     -e "s/layers.minimum/tf_keras.layers.minimum/g" \
     -e "s/layers.Concatenate/tf_keras.layers.Concatenate/g" \
     -e "s/layers.Dense/tf_keras.layers.Dense/g" \
     -e "s/layers.experimental.preprocessing./tf_keras.layers./g" \
     -e "s/layers.DenseFeatures/keras_internal.layers.DenseFeatures/g" \
     -e "s/models.Model/tf_keras.models.Model/g" {} \; && \
sed -i "s/ models.load_model/ tf_keras.models.load_model/g" /opt/conda/lib/python3.10/site-packages/tensorflow_decision_forests/keras/keras_test.py && \
sed -i "/import tensorflow as tf/a import tf_keras" /opt/conda/lib/python3.10/site-packages/tensorflow_decision_forests/keras/test_runner.py && \
sed -i "/import tensorflow as tf/a import tf_keras" /opt/conda/lib/python3.10/site-packages/tensorflow_decision_forests/keras/wrappers.py && \
sed -i -e "/import tensorflow as tf/a import tf_keras" \
       -e "s/optimizer=optimizers.Adam()/optimizer=tf_keras.optimizers.Adam()/g" \
       /opt/conda/lib/python3.10/site-packages/tensorflow_decision_forests/keras/wrappers_pre_generated.py && \
find /opt/conda/lib/python3.10/site-packages/tensorflow_decision_forests -type f -exec sed -i "s/tf.keras./tf_keras./g" {} \;
