
# CUDA 10, Cudnn 7.4.1
FROM tensorflow/tensorflow:1.13.1-gpu-py3-jupyter

ADD clean-layer.sh  /tmp/clean-layer.sh
ADD requirements.txt requirements2.7.txt requirements.system /tmp/

RUN apt-get update && \
    xargs apt-get install -y < /tmp/requirements.system && \
    pip install -r /tmp/requirements.txt && \
    pip2 install -r /tmp/requirements2.7.txt && \
    pip2 install tensorflow-gpu && \
    rm /tmp/requirements.txt /tmp/requirements2.7.txt && \
    /tmp/clean-layer.sh

RUN pip install --upgrade https://github.com/myelintek/lib-mlsteam/releases/download/v0.2/mlsteam-0.2.0-py3-none-any.whl && \
    pip2 install --upgrade https://github.com/myelintek/lib-mlsteam/releases/download/v0.2/mlsteam-0.2.0-py2-none-any.whl

WORKDIR /job_dir
