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