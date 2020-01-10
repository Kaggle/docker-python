FROM nvidia/cuda:10.0-cudnn7-devel-ubuntu16.04 AS nvidia
FROM continuumio/anaconda3:2019.03

# Avoid interactive configuration prompts/dialogs during apt-get.
ENV DEBIAN_FRONTEND=noninteractive

# This is necessary to for apt to access HTTPS sources
RUN apt-get update && \
    apt-get install apt-transport-https

# Cuda support
COPY --from=nvidia /etc/apt/sources.list.d/cuda.list /etc/apt/sources.list.d/
COPY --from=nvidia /etc/apt/sources.list.d/nvidia-ml.list /etc/apt/sources.list.d/
COPY --from=nvidia /etc/apt/trusted.gpg /etc/apt/trusted.gpg.d/cuda.gpg

# Ensure the cuda libraries are compatible with the GPU image.
# TODO(b/120050292): Use templating to keep in sync.
ENV CUDA_VERSION=10.0.130
ENV CUDA_PKG_VERSION=10-0=$CUDA_VERSION-1
LABEL com.nvidia.volumes.needed="nvidia_driver"
LABEL com.nvidia.cuda.version="${CUDA_VERSION}"
ENV PATH=/usr/local/nvidia/bin:/usr/local/cuda/bin:${PATH}
# The stub is useful to us both for built-time linking and run-time linking, on CPU-only systems.
# When intended to be used with actual GPUs, make sure to (besides providing access to the host
# CUDA user libraries, either manually or through the use of nvidia-docker) exclude them. One
# convenient way to do so is to obscure its contents by a bind mount:
#   docker run .... -v /non-existing-directory:/usr/local/cuda/lib64/stubs:ro ...
ENV LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/usr/local/nvidia/lib64:/usr/local/cuda/lib64:/usr/local/cuda/lib64/stubs"
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility
ENV NVIDIA_REQUIRE_CUDA="cuda>=10.0"
RUN apt-get update && apt-get install -y --no-install-recommends \
      cuda-cupti-$CUDA_PKG_VERSION \
      cuda-cudart-$CUDA_PKG_VERSION \
      cuda-cudart-dev-$CUDA_PKG_VERSION \
      cuda-libraries-$CUDA_PKG_VERSION \
      cuda-libraries-dev-$CUDA_PKG_VERSION \
      cuda-nvml-dev-$CUDA_PKG_VERSION \
      cuda-minimal-build-$CUDA_PKG_VERSION \
      cuda-command-line-tools-$CUDA_PKG_VERSION \
      libcudnn7=7.5.0.56-1+cuda10.0 \
      libcudnn7-dev=7.5.0.56-1+cuda10.0 \
      libnccl2=2.4.2-1+cuda10.0 \
      libnccl-dev=2.4.2-1+cuda10.0 && \
    ln -s /usr/local/cuda-10.0 /usr/local/cuda && \
    ln -s /usr/local/cuda/lib64/stubs/libcuda.so /usr/local/cuda/lib64/stubs/libcuda.so.1

# Work to upgrade to Python 3.7 can be found on this branch: https://github.com/Kaggle/docker-python/blob/upgrade-py37/Dockerfile
RUN conda install -y python=3.6.6 && pip install --upgrade pip && pip install numpy

# See _TF_(MIN|MAX)_BAZEL_VERSION at https://github.com/tensorflow/tensorflow/blob/master/configure.py.
ENV BAZEL_VERSION=0.29.1
RUN apt-get install -y gnupg zip openjdk-8-jdk && \
    apt-get install -y --no-install-recommends \
      bash-completion \
      zlib1g-dev && \
    wget --no-verbose "https://github.com/bazelbuild/bazel/releases/download/${BAZEL_VERSION}/bazel_${BAZEL_VERSION}-linux-x86_64.deb" && \
    dpkg -i bazel_*.deb && \
    rm bazel_*.deb

# Fetch tensorflow & install dependencies.
RUN cd /usr/local/src && \
    git clone https://github.com/tensorflow/tensorflow && \
    cd tensorflow && \
    git checkout tags/v2.1.0 && \
    pip install keras_applications --no-deps && \
    pip install keras_preprocessing --no-deps

# Create a tensorflow wheel for CPU
RUN cd /usr/local/src/tensorflow && \
    cat /dev/null | ./configure && \
    bazel build --config=opt --config=v2 //tensorflow/tools/pip_package:build_pip_package && \
    bazel-bin/tensorflow/tools/pip_package/build_pip_package /tmp/tensorflow_cpu && \
    bazel clean

# Create a tensorflow wheel for GPU/cuda
ENV TF_NEED_CUDA=1
ENV TF_CUDA_VERSION=10.0
# 3.7 is for the K80 and 6.0 is for the P100, 7.5 is for the T4: https://developer.nvidia.com/cuda-gpus
ENV TF_CUDA_COMPUTE_CAPABILITIES=3.7,6.0,7.5
ENV TF_CUDNN_VERSION=7
ENV TF_NCCL_VERSION=2
ENV NCCL_INSTALL_PATH=/usr/

RUN cd /usr/local/src/tensorflow && \
    # TF_NCCL_INSTALL_PATH is used for both libnccl.so.2 and libnccl.h. Make sure they are both accessible from the same directory.
    ln -s /usr/lib/x86_64-linux-gnu/libnccl.so.2 /usr/lib/ && \
    cat /dev/null | ./configure && \
    echo "/usr/local/cuda-${TF_CUDA_VERSION}/targets/x86_64-linux/lib/stubs" > /etc/ld.so.conf.d/cuda-stubs.conf && ldconfig && \
    bazel build --config=opt \
                --config=v2 \
                --config=cuda \
                --cxxopt="-D_GLIBCXX_USE_CXX11_ABI=0" \
                //tensorflow/tools/pip_package:build_pip_package && \
    rm /etc/ld.so.conf.d/cuda-stubs.conf && ldconfig && \
    bazel-bin/tensorflow/tools/pip_package/build_pip_package /tmp/tensorflow_gpu && \
    bazel clean

# Print out the built .whl files
RUN ls -R /tmp/tensorflow*
