ARG BASE_IMAGE_TAG
ARG LIBTPU_IMAGE_TAG
ARG TENSORFLOW_WHL_IMAGE_TAG

FROM gcr.io/cloud-tpu-v2-images/libtpu:${LIBTPU_IMAGE_TAG} as libtpu
FROM gcr.io/kaggle-images/python-tpu-tensorflow-whl:${TENSORFLOW_WHL_IMAGE_TAG} AS tensorflow_whl
FROM gcr.io/kaggle-images/python:${BASE_IMAGE_TAG}

COPY --from=libtpu /libtpu.so /lib

COPY --from=tensorflow_whl /tmp/tensorflow_pkg/tensorflow*.whl /tmp/tensorflow_pkg/
RUN pip install /tmp/tensorflow_pkg/tensorflow*.whl && \
    rm -rf /tmp/tensorflow_pkg

# https://cloud.google.com/tpu/docs/pytorch-xla-ug-tpu-vm#changing_pytorch_version
RUN pip uninstall -y torch
RUN pip uninstall -y torch_xla
RUN pip install torch==1.10
RUN pip install torch_xla[tpuvm] -f https://storage.googleapis.com/tpu-pytorch/wheels/tpuvm/torch_xla-1.10-cp37-cp37m-linux_x86_64.whl

# https://cloud.google.com/tpu/docs/jax-quickstart-tpu-vm#install_jax_on_your_cloud_tpu_vm
RUN pip install "jax[tpu]>=0.2.16" -f https://storage.googleapis.com/jax-releases/libtpu_releases.html