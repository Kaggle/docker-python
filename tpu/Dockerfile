ARG BASE_IMAGE_TAG
ARG TENSORFLOW_VERSION

FROM gcr.io/kaggle-images/python-tpu-tensorflow-whl:python-${BASE_IMAGE_TAG}-${TENSORFLOW_VERSION} AS tensorflow_whl
FROM gcr.io/kaggle-images/python:${BASE_IMAGE_TAG}

# We need to define the ARG here to get the ARG below the FROM statement to access it within this build context
# See: https://docs.docker.com/engine/reference/builder/#understand-how-arg-and-from-interact
ARG TORCH_VERSION

ENV ISTPUVM=1

COPY --from=tensorflow_whl /tmp/tensorflow_pkg/tensorflow*.whl /tmp/tensorflow_pkg/
RUN pip install /tmp/tensorflow_pkg/tensorflow*.whl && \
    rm -rf /tmp/tensorflow_pkg && \
    /tmp/clean-layer.sh

# LIBTPU installed here:
ENV DEFAULT_LIBTPU=/opt/conda/lib/python3.7/site-packages/libtpu/libtpu.so
ENV PYTORCH_LIBTPU=/opt/conda/lib/python3.7/site-packages/libtpu/torch-libtpu.so
ENV JAX_LIBTPU=/opt/conda/lib/python3.7/site-packages/libtpu/jax-libtpu.so

# https://cloud.google.com/tpu/docs/pytorch-xla-ug-tpu-vm#changing_pytorch_version
RUN pip uninstall -y torch && \
    pip install torch==${TORCH_VERSION} && \
    # The URL doesn't include patch version. i.e. must use 1.11 instead of 1.11.0
    pip install torch_xla[tpuvm] -f https://storage.googleapis.com/tpu-pytorch/wheels/tpuvm/torch_xla-${TORCH_VERSION%.*}-cp37-cp37m-linux_x86_64.whl && \
    cp $DEFAULT_LIBTPU $PYTORCH_LIBTPU && \
    /tmp/clean-layer.sh

# https://cloud.google.com/tpu/docs/jax-quickstart-tpu-vm#install_jax_on_your_cloud_tpu_vm
RUN pip install "jax[tpu]>=0.2.16" -f https://storage.googleapis.com/jax-releases/libtpu_releases.html && \
    cp $DEFAULT_LIBTPU $JAX_LIBTPU && \
    /tmp/clean-layer.sh

# Monkey-patch TF, JAX & PYTORCH to load the correct libtpu.so when they are imported:
RUN sed -i "s|^\(\(.*\)libtpu.configure_library_path.*\)|\1\n\2os.environ['TPU_LIBRARY_PATH'] = '${PYTORCH_LIBTPU}'|" /opt/conda/lib/python3.7/site-packages/torch_xla/__init__.py && \
    sed -i "s|^\(\(.*\)libtpu.configure_library_path.*\)|\1\n\2os.environ['TPU_LIBRARY_PATH'] = '${JAX_LIBTPU}'|" /opt/conda/lib/python3.7/site-packages/jax/_src/cloud_tpu_init.py && \
    sed -i "1s/^/from jax._src.cloud_tpu_init import cloud_tpu_init\ncloud_tpu_init()\n/" /opt/conda/lib/python3.7/site-packages/tensorflow/__init__.py

# Set these env vars so that they don't produce errs calling the metadata server to load them:
ENV TPU_ACCELERATOR_TYPE=v3-8
ENV TPU_PROCESS_ADDRESSES=local