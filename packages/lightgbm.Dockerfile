ARG BASE_IMAGE

FROM ${BASE_IMAGE} AS builder

ARG PACKAGE_VERSION
ARG CUDA_MAJOR_VERSION
ARG CUDA_MINOR_VERSION

# May need to build this...

# Make sure we are on the right version of CUDA
RUN update-alternatives --set cuda /usr/local/cuda-$CUDA_MAJOR_VERSION.$CUDA_MINOR_VERSION

# Build instructions: https://lightgbm.readthedocs.io/en/latest/GPU-Tutorial.html#build-lightgbm
RUN apt-get update && \
    apt-get install -y build-essential cmake libboost-dev libboost-system-dev libboost-filesystem-dev clinfo nvidia-opencl-dev opencl-headers

RUN cd /usr/local/src && \
    git clone --recursive https://github.com/microsoft/LightGBM && \
    cd LightGBM && \
    git checkout tags/v$PACKAGE_VERSION && \
    ./build-python.sh bdist_wheel  --gpu --opencl-library=/usr/local/cuda/lib64/libOpenCL.so --opencl-include-dir=/usr/local/cuda/include/

# Using multi-stage builds to ensure the output image is very small
# See: https://docs.docker.com/develop/develop-images/multistage-build/
FROM alpine:latest

RUN mkdir -p /tmp/whl/
COPY --from=builder /usr/local/src/LightGBM/dist/*.whl /tmp/whl

# Print out the built .whl file.
RUN ls -lh /tmp/whl/