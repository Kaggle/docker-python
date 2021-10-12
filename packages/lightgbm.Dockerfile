ARG BASE_IMAGE

FROM ${BASE_IMAGE} AS builder

ARG PACKAGE_VERSION

# Build instructions: https://lightgbm.readthedocs.io/en/latest/GPU-Tutorial.html#build-lightgbm
RUN apt-get update && \
    apt-get install -y build-essential cmake libboost-dev libboost-system-dev libboost-filesystem-dev ocl-icd-libopencl1 clinfo

RUN cd /usr/local/src && \
    git clone --recursive https://github.com/microsoft/LightGBM && \
    cd LightGBM && \
    git checkout tags/v$PACKAGE_VERSION && \
    mkdir build && cd build && \
    cmake -DUSE_GPU=1 -DOpenCL_LIBRARY=/usr/local/cuda/lib64/libOpenCL.so -DOpenCL_INCLUDE_DIR=/usr/local/cuda/include/ .. && \
    make -j$(nproc) && \
    cd /usr/local/src/LightGBM/python-package && \
    python setup.py bdist_wheel

# Using multi-stage builds to ensure the output image is very small
# See: https://docs.docker.com/develop/develop-images/multistage-build/
FROM alpine:latest

RUN mkdir -p /tmp/whl/
COPY --from=builder /usr/local/src/LightGBM/python-package/dist/*.whl /tmp/whl

# Print out the built .whl file.
RUN ls -lh /tmp/whl/