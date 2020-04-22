# Copyright 2016 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""GCS file system configuration for TensorFlow."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import inspect
import json
import os
import sys

import tensorflow as tf
from tensorflow import errors
from tensorflow.python.framework import dtypes
from tensorflow.python.framework import ops
from tensorflow.python.ops import array_ops
from tensorflow.python.training import training

def _load_library(filename, lib="op"):
  """_load_library"""
  f = inspect.getfile(sys._getframe(1)) # pylint: disable=protected-access

  # Construct filename
  f = os.path.join(os.path.dirname(f), filename)
  filenames = [f]

  # Function to load the library, return True if file system library is loaded
  load_fn = tf.load_op_library if lib == "op" \
      else lambda f: tf.compat.v1.load_file_system_library(f) is None

  # Try to load all paths for file, fail if none succeed
  errs = []
  for f in filenames:
    try:
      l = load_fn(f)
      if l is not None:
        return l
    except errors.NotFoundError as e:
      errs.append(str(e))
  raise NotImplementedError(
      "unable to open file: " +
      "{}, from paths: {}\ncaused by: {}".format(filename, filenames, errs))

_gcs_config_so = _load_library("_gcs_config_ops.so")
gcs_configure_credentials = _gcs_config_so.gcs_configure_credentials
gcs_configure_block_cache = _gcs_config_so.gcs_configure_block_cache

class BlockCacheParams(object):  # pylint: disable=useless-object-inheritance
  """BlockCacheParams is a struct used for configuring the GCS Block Cache."""

  def __init__(self, block_size=None, max_bytes=None, max_staleness=None):
    self._block_size = block_size or 128 * 1024 * 1024
    self._max_bytes = max_bytes or 2 * self._block_size
    self._max_staleness = max_staleness or 0

  @property
  def block_size(self):
    return self._block_size

  @property
  def max_bytes(self):
    return self._max_bytes

  @property
  def max_staleness(self):
    return self._max_staleness

def configure_gcs(credentials=None, block_cache=None, device=None):
  """Configures the GCS file system for a given a session.

  Warning: GCS `credentials` may be transmitted over the network unencrypted.
  Please ensure that the network is trusted before using this function. For
  users running code entirely within Google Cloud, your data is protected by
  encryption in between data centers. For more information, please take a look
  at https://cloud.google.com/security/encryption-in-transit/.

  Args:
    credentials: [Optional.] A JSON string
    block_cache: [Optional.] A BlockCacheParams to configure the block cache .
    device: [Optional.] The device to place the configure ops.
  """
  def configure(credentials, block_cache):
    """Helper function to actually configure GCS."""
    if credentials:
      if isinstance(credentials, dict):
        credentials = json.dumps(credentials)
      creds = gcs_configure_credentials(credentials)
    else:
      creds = tf.constant(0)

    if block_cache:
      cache = gcs_configure_block_cache(
          max_cache_size=block_cache.max_bytes,
          block_size=block_cache.block_size,
          max_staleness=block_cache.max_staleness)
    else:
      cache = tf.constant(0)

    return tf.tuple([creds, cache])

  if device:
    with ops.device(device):
      return configure(credentials, block_cache)
  return configure(credentials, block_cache)

def configure_gcs_from_colab_auth(device='/job:worker/replica:0/task:0/device:CPU:0'):
  """ConfigureColabSession configures the GCS file system in Colab.

  Args:
  """
  # Read from the application default credentials (adc).
  adc_filename = os.environ.get(
      'GOOGLE_APPLICATION_CREDENTIALS', '/content/adc.json')
  with open(adc_filename) as f:
    data = json.load(f)
  return configure_gcs(credentials=data, device=device)


