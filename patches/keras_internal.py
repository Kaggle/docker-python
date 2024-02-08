# Copyright 2021 Google LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Access to Keras function with a different internal and external path."""

from tf_keras.src.engine import data_adapter as _data_adapter
from tf_keras.src.models import Functional
from tf_keras.layers import DenseFeatures
from tf_keras.src.utils.dataset_creator import DatasetCreator


unpack_x_y_sample_weight = _data_adapter.unpack_x_y_sample_weight
get_data_handler = _data_adapter.get_data_handler
