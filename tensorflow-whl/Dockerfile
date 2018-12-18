FROM nvidia/cuda:9.2-cudnn7-devel-ubuntu16.04 AS nvidia
FROM continuumio/anaconda3:5.2.0

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
ENV CUDA_VERSION=9.2.148
ENV CUDA_PKG_VERSION=9-2=$CUDA_VERSION-1
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
ENV NVIDIA_REQUIRE_CUDA="cuda>=9.0"
RUN apt-get update && apt-get install -y --no-install-recommends \
      cuda-cupti-$CUDA_PKG_VERSION \
      cuda-cudart-$CUDA_PKG_VERSION \
      cuda-cudart-dev-$CUDA_PKG_VERSION \
      cuda-libraries-$CUDA_PKG_VERSION \
      cuda-libraries-dev-$CUDA_PKG_VERSION \
      cuda-nvml-dev-$CUDA_PKG_VERSION \
      cuda-minimal-build-$CUDA_PKG_VERSION \
      cuda-command-line-tools-$CUDA_PKG_VERSION \
      libcudnn7=7.4.1.5-1+cuda9.2 \
      libcudnn7-dev=7.4.1.5-1+cuda9.2 \
      libnccl2=2.3.7-1+cuda9.2 \
      libnccl-dev=2.3.7-1+cuda9.2 && \
    ln -s /usr/local/cuda-9.2 /usr/local/cuda && \
    ln -s /usr/local/cuda/lib64/stubs/libcuda.so /usr/local/cuda/lib64/stubs/libcuda.so.1 && \
    rm -rf /var/lib/apt/lists/*

# Install bazel
# Tensorflow 1.11 requires the Bazel 0.15: https://www.tensorflow.org/install/source
ENV BAZEL_VERSION=0.15.0
RUN apt-get update && apt-get install -y gnupg zip && \
    echo "deb http://ppa.launchpad.net/webupd8team/java/ubuntu precise main" | tee -a /etc/apt/sources.list && \
    echo "deb-src http://ppa.launchpad.net/webupd8team/java/ubuntu precise main" | tee -a /etc/apt/sources.list && \
    apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys --no-tty EEA14886 C857C906 2B90D010 && \
    apt-get update && \
    echo debconf shared/accepted-oracle-license-v1-1 select true | debconf-set-selections && \
    echo debconf shared/accepted-oracle-license-v1-1 seen true | debconf-set-selections && \
    apt-get install -y oracle-java8-installer && \
    apt-get install -y --no-install-recommends \
      bash-completion \
      zlib1g-dev && \
    # Install Bazel with apt-get once this issue is resolved: https://github.com/bazelbuild/continuous-integration/issues/128
    wget --no-verbose "https://github.com/bazelbuild/bazel/releases/download/${BAZEL_VERSION}/bazel_${BAZEL_VERSION}-linux-x86_64.deb" && \
    dpkg -i bazel_*.deb && \
    rm bazel_*.deb

# Tensorflow doesn't support python 3.7 yet. See https://github.com/tensorflow/tensorflow/issues/20517
RUN conda install -y python=3.6.6 && \
    # Another fix for TF 1.10 https://github.com/tensorflow/tensorflow/issues/21518
    pip install keras_applications==1.0.4 --no-deps && \
    pip install keras_preprocessing==1.0.2 --no-deps

# Fetch tensorflow
RUN cd /usr/local/src && \
    git clone https://github.com/tensorflow/tensorflow && \
    cd tensorflow && \
    git checkout r1.12

# Create a tensorflow wheel for CPU
RUN cd /usr/local/src/tensorflow && \
    cat /dev/null | ./configure && \
    bazel build --config=opt //tensorflow/tools/pip_package:build_pip_package && \
    bazel-bin/tensorflow/tools/pip_package/build_pip_package /tmp/tensorflow_cpu && \
    bazel clean

# Create a tensorflow wheel for GPU/cuda
ENV TF_NEED_CUDA=1
ENV TF_CUDA_VERSION=9.2
ENV TF_CUDA_COMPUTE_CAPABILITIES=3.7,6.0
ENV TF_CUDNN_VERSION=7
ENV TF_NCCL_VERSION=2
ENV NCCL_INSTALL_PATH=/usr/

RUN cd /usr/local/src/tensorflow && \
    # TF_NCCL_INSTALL_PATH is used for both libnccl.so.2 and libnccl.h. Make sure they are both accessible from the same directory.
    ln -s /usr/lib/x86_64-linux-gnu/libnccl.so.2 /usr/lib/ && \
    cat /dev/null | ./configure && \
    echo "/usr/local/cuda-${TF_CUDA_VERSION}/targets/x86_64-linux/lib/stubs" > /etc/ld.so.conf.d/cuda-stubs.conf && ldconfig && \
    bazel build --config=opt \
                --config=cuda \
                --cxxopt="-D_GLIBCXX_USE_CXX11_ABI=0" \
                //tensorflow/tools/pip_package:build_pip_package && \
    rm /etc/ld.so.conf.d/cuda-stubs.conf && ldconfig && \
    bazel-bin/tensorflow/tools/pip_package/build_pip_package /tmp/tensorflow_gpu && \
    bazel clean

# Print out the built .whl files
RUN ls -R /tmp/tensorflow*
