ARG BASE_IMAGE

FROM ${BASE_IMAGE} AS builder

ARG PACKAGE_VERSION
ARG TORCHAUDIO_VERSION
ARG TORCHTEXT_VERSION
ARG TORCHVISION_VERSION

# TORCHVISION_VERSION is mandatory
RUN test -n "$TORCHVISION_VERSION"

# Build instructions: https://github.com/pytorch/pytorch#from-source
RUN conda install astunparse numpy ninja pyyaml mkl mkl-include setuptools cmake cffi typing_extensions future six requests dataclasses

# By default, it uses the version from version.txt which includes the `a0` (alpha zero) suffix and part of the git hash.
# This causes dependency conflicts like these: https://paste.googleplex.com/4786486378496000
ENV PYTORCH_BUILD_VERSION=$PACKAGE_VERSION
ENV PYTORCH_BUILD_NUMBER=1

ENV TORCH_CUDA_ARCH_LIST="3.7;6.0;7.0+PTX;7.5+PTX"
ENV FORCE_CUDA=1
RUN cd /usr/local/src && \
    git clone --recursive https://github.com/pytorch/pytorch && \
    cd pytorch && \
    git checkout tags/v$PACKAGE_VERSION && \
    git submodule sync && \
    git submodule update --init --recursive --jobs 0 && \
    python setup.py bdist_wheel

# Install torch which is required before we can build other torch* packages.
RUN pip install /usr/local/src/pytorch/dist/*.whl

# Build torchaudio
# Instructions: https://github.com/pytorch/audio#from-source
# See comment above for PYTORCH_BUILD_VERSION.
ENV BUILD_VERSION=$TORCHAUDIO_VERSION
RUN cd /usr/local/src && \
    git clone https://github.com/pytorch/audio && \
    cd audio && \
    git checkout tags/v$TORCHAUDIO_VERSION && \
    git submodule sync && \
    git submodule update --init --recursive --jobs 0 && \
    python setup.py bdist_wheel

# Build torchtext
# Instructions: https://github.com/pytorch/text#building-from-source
# See comment above for PYTORCH_BUILD_VERSION.
ENV BUILD_VERSION=$TORCHTEXT_VERSION
RUN cd /usr/local/src && \
    git clone https://github.com/pytorch/text && \
    cd text && \
    git checkout tags/v$TORCHTEXT_VERSION && \
    git submodule sync && \
    git submodule update --init --recursive --jobs 0 && \
    python setup.py bdist_wheel

# Build torchvision.
# Instructions: https://github.com/pytorch/vision/tree/main#installation
# See comment above for PYTORCH_BUILD_VERSION.
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
COPY --from=builder /usr/local/src/text/dist/*.whl /tmp/whl
COPY --from=builder /usr/local/src/vision/dist/*.whl /tmp/whl

# Print out the built .whl file.
RUN ls -lh /tmp/whl/