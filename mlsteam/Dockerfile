
# CUDA 10, Cudnn 7.4.1
FROM tensorflow/tensorflow:1.13.1-gpu-py3-jupyter

ADD clean-layer.sh  /tmp/clean-layer.sh
ADD requirements.txt /tmp/requirements.txt

RUN apt-get install -y libglib2.0-0 libxext6 libsm6 libxrender1 libfontconfig1 --fix-missing && \
    pip install -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt && \
    /tmp/clean-layer.sh

WORKDIR /job_dir
