# Copyright 2019 The TensorFlow Authors. All Rights Reserved.
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
# =============================================================================

from __future__ import print_function

import os
import re
import sys
import tensorflow as tf

def write_config():
  """Retrive compile and link information from tensorflow and write to .bazelrc."""

  cflags = tf.sysconfig.get_compile_flags()

  inc_regex = re.compile("^-I")
  opt_regex = re.compile("^-D")

  include_list = []
  opt_list = []

  for arg in cflags:
    if inc_regex.match(arg):
      include_list.append(arg)
    elif opt_regex.match(arg):
      opt_list.append(arg)
    else:
      print("WARNING: Unexpected cflag item {}".format(arg))


  if len(include_list) != 1:
    print("ERROR: Expected a single include directory in " +
          "tf.sysconfig.get_compile_flags()")
    exit(1)


  library_regex = re.compile("^-l")
  libdir_regex = re.compile("^-L")

  library_list = []
  libdir_list = []

  lib = tf.sysconfig.get_link_flags()

  for arg in lib:
    if library_regex.match(arg):
      library_list.append(arg)
    elif libdir_regex.match(arg):
      libdir_list.append(arg)
    else:
      print("WARNING: Unexpected link flag item {}".format(arg))

  if len(library_list) != 1 or len(libdir_list) != 1:
    print("ERROR: Expected exactly one lib and one libdir in" +
          "tf.sysconfig.get_link_flags()")
    exit(1)

  try:

    with open(".bazelrc", "w") as bazel_rc:
      for opt in opt_list:
        bazel_rc.write('build --copt="{}"\n'.format(opt))

      bazel_rc.write('build --action_env TF_HEADER_DIR="{}"\n'
                     .format(include_list[0][2:]))

      bazel_rc.write('build --action_env TF_SHARED_LIBRARY_DIR="{}"\n'
                     .format(libdir_list[0][2:]))
      library_name = library_list[0][2:]
      if library_name.startswith(":"):
        library_name = library_name[1:]
      else:
        library_name = "lib" + library_name + ".so"
      bazel_rc.write('build --action_env TF_SHARED_LIBRARY_NAME="{}"\n'
                     .format(library_name))
      bazel_rc.close()
  except OSError:
    print("ERROR: Writing .bazelrc")
    exit(1)


def compile_bazel():
  write_config()

  if os.system('rm -f tensorflow_gcs_config/*.so && bazel build -c dbg //tensorflow_gcs_config:_gcs_config_ops.so && cp bazel-bin/tensorflow_gcs_config/_gcs_config_ops.so tensorflow_gcs_config/') != 0:
    raise Exception('Failed to build C extension.')
