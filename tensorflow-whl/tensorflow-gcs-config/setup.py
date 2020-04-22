from setuptools import setup


setup_kwargs = {
}

from build import compile_bazel
compile_bazel()

setup(
  name='tensorflow-gcs-config',
  version='2.1.7',
  description='TensorFlow operations for configuring access to GCS (Google Compute Storage) resources.',
  long_description='TensorFlow operations for configuring access to GCS (Google Compute Storage) resources.',
  author='Google, Inc.',
  author_email=None,
  url=None,
  packages = ['tensorflow_gcs_config'],
  include_package_data=True,
)
