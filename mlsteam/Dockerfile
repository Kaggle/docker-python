# CUDA 10, Cudnn 7.4.1
FROM tensorflow/tensorflow:1.13.1-gpu-py3-jupyter

ENV SHELL /bin/bash
ENV HOME /workspace

ADD clean-layer.sh  /tmp/clean-layer.sh
ADD requirements.txt requirements2.7.txt requirements.system install-trt.sh install-ros.sh install-opencv3.sh requirements.opencv3 /tmp/

RUN sed -i 's/archive.ubuntu.com/tw.archive.ubuntu.com/g' /etc/apt/sources.list && \
    apt-get update && \
    xargs apt-get install -y < /tmp/requirements.system && \
    pip install -r /tmp/requirements.txt && \
    pip2 install -r /tmp/requirements2.7.txt && \
    rm /tmp/requirements.txt /tmp/requirements2.7.txt /tmp/requirements.system && \
    /tmp/clean-layer.sh

RUN pip install --upgrade https://github.com/myelintek/lib-mlsteam/releases/download/v0.2/mlsteam-0.2.0-py3-none-any.whl && \
    pip2 install --upgrade https://github.com/myelintek/lib-mlsteam/releases/download/v0.2/mlsteam-0.2.0-py2-none-any.whl

RUN bash /tmp/install-trt.sh && bash /tmp/install-ros.sh && bash /tmp/install-opencv3.sh

RUN rm -rf /usr/lib/x86_64-linux-gnu/libcuda.so /usr/lib/x86_64-linux-gnu/libcuda.so.1 /tmp/*

WORKDIR /workspace
