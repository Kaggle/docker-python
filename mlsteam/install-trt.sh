#!/bin/bash

wget -O /tmp/nv-trt.deb http://140.96.29.39:8000/nv-tensorrt-repo-ubuntu1604-cuda10.0-trt5.0.2.6-ga-20181009_1-1_amd64.deb && \
dpkg -i /tmp/nv-trt.deb && \
apt-key add /var/nv-tensorrt-repo-cuda10.0-trt5.0.2.6-ga-20181009/7fa2af80.pub && \
apt-get update && \
apt-get install -y libnvinfer-dev=5.0.2-1+cuda10.0 && \
apt-get install -y libnvinfer5=5.0.2-1+cuda10.0 && \
apt-get install -y libnvinfer-samples=5.0.2-1+cuda10.0 && \
apt-get install -y tensorrt && \
apt-get install -y python3-libnvinfer-dev && \
apt-get install -y uff-converter-tf

