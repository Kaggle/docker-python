ARG BASE_IMAGE

FROM ${BASE_IMAGE} AS builder

ARG PACKAGE_VERSION
ARG CUDA_MAJOR_VERSION
ARG CUDA_MINOR_VERSION

# Make sure we are on the right version of CUDA
RUN update-alternatives --set cuda /usr/local/cuda-$CUDA_MAJOR_VERSION.$CUDA_MINOR_VERSION

# Ensures shared libraries installed with conda can be found by the dynamic link loader.
# For PyTorch, we need specifically mkl.
ENV LIBRARY_PATH="$LIBRARY_PATH:/opt/conda/lib"
ENV LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/opt/conda/lib"

# Instructions: https://jax.readthedocs.io/en/latest/developer.html#building-jaxlib-from-source
RUN sudo ln -s /usr/bin/python3 /usr/bin/python

RUN apt-get update && \ 
    apt-get install -y g++ python3 python3-dev

RUN pip install numpy wheel build

RUN cd /usr/local/src && \
    git clone https://github.com/google/jax && \
    cd jax && \
    git checkout jaxlib-v$PACKAGE_VERSION

RUN cd /usr/local/src/jax && \
    python build/build.py --enable_cuda

# Using multi-stage builds to ensure the output image is very small
# See: https://docs.docker.com/develop/develop-images/multistage-build/
FROM alpine:latest

RUN mkdir -p /tmp/whl/
COPY --from=builder /usr/local/src/jax/dist/*.whl /tmp/whl

# Print out the built .whl file.
RUN ls -lh /tmp/whl/