ARG BASE_IMAGE_TAG
ARG LIBTPU_IMAGE_TAG
ARG TENSORFLOW_VERSION
ARG TORCH_VERSION

FROM gcr.io/cloud-tpu-v2-images/libtpu:${LIBTPU_IMAGE_TAG} as libtpu
FROM gcr.io/kaggle-images/python-tpu-tensorflow-whl:python-${BASE_IMAGE_TAG}-${TENSORFLOW_VERSION} AS tensorflow_whl
FROM gcr.io/kaggle-images/python:${BASE_IMAGE_TAG}

ENV ISTPUVM=1

COPY --from=libtpu /libtpu.so /lib

COPY --from=tensorflow_whl /tmp/tensorflow_pkg/tensorflow*.whl /tmp/tensorflow_pkg/
RUN pip install /tmp/tensorflow_pkg/tensorflow*.whl && \
    rm -rf /tmp/tensorflow_pkg && \
    /tmp/clean-layer.sh

# https://cloud.google.com/tpu/docs/pytorch-xla-ug-tpu-vm#changing_pytorch_version
RUN pip uninstall -y torch && \
    pip install torch==${TORCH_VERSION} && \
    pip install torch_xla[tpuvm] -f https://storage.googleapis.com/tpu-pytorch/wheels/tpuvm/torch_xla-${TORCH_VERSION}-cp37-cp37m-linux_x86_64.whl && \
    /tmp/clean-layer.sh

# https://cloud.google.com/tpu/docs/jax-quickstart-tpu-vm#install_jax_on_your_cloud_tpu_vm
RUN pip install "jax[tpu]>=0.2.16" -f https://storage.googleapis.com/jax-releases/libtpu_releases.html && \
    /tmp/clean-layer.sh
