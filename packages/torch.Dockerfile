ARG BASE_IMAGE

FROM ${BASE_IMAGE} AS builder

ARG PACKAGE_VERSION
ARG TORCHAUDIO_VERSION
ARG TORCHVISION_VERSION
ARG CUDA_MAJOR_VERSION
ARG CUDA_MINOR_VERSION

# Make sure we are on the right version of CUDA
RUN update-alternatives --set cuda /usr/local/cuda-$CUDA_MAJOR_VERSION.$CUDA_MINOR_VERSION

# TORCHVISION_VERSION is mandatory
RUN test -n "$TORCHVISION_VERSION"

# Use mamba to speed up conda installs
RUN conda install -c conda-forge mamba

# Build instructions: https://github.com/pytorch/pytorch#from-source
RUN mamba install astunparse numpy ninja pyyaml mkl mkl-include setuptools cmake cffi typing_extensions future six requests dataclasses
RUN mamba install -c pytorch magma-cuda121

# By default, it uses the version from version.txt which includes the `a0` (alpha zero) suffix and part of the git hash.
# This causes dependency conflicts like these: https://paste.googleplex.com/4786486378496000
ENV PYTORCH_BUILD_VERSION=$PACKAGE_VERSION
ENV PYTORCH_BUILD_NUMBER=1

# Ensures shared libraries installed with conda can be found by the dynamic link loader.
# For PyTorch, we need specifically mkl.
ENV LIBRARY_PATH="$LIBRARY_PATH:/opt/conda/lib"
ENV LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/opt/conda/lib"
ENV TORCH_CUDA_ARCH_LIST="6.0;7.0+PTX;7.5+PTX"
ENV FORCE_CUDA=1
RUN cd /usr/local/src && \
    git clone --recursive https://github.com/pytorch/pytorch && \
    cd pytorch && \
    git checkout tags/v$PACKAGE_VERSION && \
    git submodule sync && \
    git submodule update --init --recursive --jobs 1 && \
    python setup.py bdist_wheel

# Install torch which is required before we can build other torch* packages.
RUN pip install /usr/local/src/pytorch/dist/*.whl

# Build torchaudio
# Instructions: https://github.com/pytorch/audio#from-source
# See comment above for PYTORCH_BUILD_VERSION.
ENV BUILD_VERSION=$TORCHAUDIO_VERSION
RUN sudo apt-get update && \
    # ncurses.h is required for this install
    sudo apt-get install libncurses-dev && \
    # Fixing the build: https://github.com/pytorch/audio/issues/666#issuecomment-635928685
    mamba install -c conda-forge ncurses && \
    cd /usr/local/src && \
    git clone https://github.com/pytorch/audio && \
    cd audio && \
    git checkout tags/v$TORCHAUDIO_VERSION && \
    git submodule sync && \
    git submodule update --init --recursive --jobs 1
# https://github.com/pytorch/audio/issues/936#issuecomment-702990346
RUN sed -i 's/set(envs/set(envs\n  "LIBS=-ltinfo"/' /usr/local/src/audio/third_party/sox/CMakeLists.txt 
RUN cd /usr/local/src/audio && python setup.py bdist_wheel

# Build torchvision.
# Instructions: https://github.com/pytorch/vision/tree/main#installation
# See comment above for PYTORCH_BUILD_VERSION.
ENV CUDA_HOME=/usr/local/cuda
ENV BUILD_VERSION=$TORCHVISION_VERSION
RUN cd /usr/local/src && \
    git clone --recursive https://github.com/pytorch/vision && \
    cd vision && \
    git checkout tags/v$TORCHVISION_VERSION && \
    python setup.py bdist_wheel

# Using multi-stage builds to ensure the output image is very small
# See: https://docs.docker.com/develop/develop-images/multistage-build/
FROM alpine:latest

RUN mkdir -p /tmp/whl/
COPY --from=builder /usr/local/src/pytorch/dist/*.whl /tmp/whl
COPY --from=builder /usr/local/src/audio/dist/*.whl /tmp/whl
COPY --from=builder /usr/local/src/vision/dist/*.whl /tmp/whl

# Print out the built .whl file.
RUN ls -lh /tmp/whl/
