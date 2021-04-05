FROM nvidia/cuda:11.0-cudnn8-devel-ubuntu18.04 AS nvidia
FROM gcr.io/deeplearning-platform-release/base-cpu:m66

# Avoid interactive configuration prompts/dialogs during apt-get.
ENV DEBIAN_FRONTEND=noninteractive

# This is necessary to for apt to access HTTPS sources
RUN apt-get update && \
    apt-get install apt-transport-https

# Cuda support
COPY --from=nvidia /etc/apt/sources.list.d/cuda.list /etc/apt/sources.list.d/
COPY --from=nvidia /etc/apt/sources.list.d/nvidia-ml.list /etc/apt/sources.list.d/
COPY --from=nvidia /etc/apt/trusted.gpg /etc/apt/trusted.gpg.d/cuda.gpg
# See b/142337634#comment28
RUN sed -i 's/deb https:\/\/developer.download.nvidia.com/deb http:\/\/developer.download.nvidia.com/' /etc/apt/sources.list.d/*.list

# Ensure the cuda libraries are compatible with the GPU image.
# TODO(b/120050292): Use templating to keep in sync.
ENV CUDA_MAJOR_VERSION=11
ENV CUDA_MINOR_VERSION=0
ENV CUDA_VERSION=$CUDA_MAJOR_VERSION.$CUDA_MINOR_VERSION
LABEL com.nvidia.volumes.needed="nvidia_driver"
LABEL com.nvidia.cuda.version="${CUDA_VERSION}"
ENV PATH=/usr/local/nvidia/bin:/usr/local/cuda/bin:${PATH}
# The stub is useful to us both for built-time linking and run-time linking, on CPU-only systems.
# When intended to be used with actual GPUs, make sure to (besides providing access to the host
# CUDA user libraries, either manually or through the use of nvidia-docker) exclude them. One
# convenient way to do so is to obscure its contents by a bind mount:
#   docker run .... -v /non-existing-directory:/usr/local/cuda/lib64/stubs:ro ...
ENV LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/usr/local/nvidia/lib64:/usr/local/cuda/lib64:/usr/local/cuda/lib64/stubs:$LD_LIBRARY_PATH"
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility
ENV NVIDIA_REQUIRE_CUDA="cuda>=$CUDA_MAJOR_VERSION.$CUDA_MINOR_VERSION"
RUN apt-get update && apt-get install -y --no-install-recommends \
      cuda-cupti-$CUDA_VERSION \
      cuda-cudart-$CUDA_VERSION \
      cuda-cudart-dev-$CUDA_VERSION \
      cuda-libraries-$CUDA_VERSION \
      cuda-libraries-dev-$CUDA_VERSION \
      cuda-nvml-dev-$CUDA_VERSION \
      cuda-minimal-build-$CUDA_VERSION \
      cuda-command-line-tools-$CUDA_VERSION \
      libcudnn8=8.0.4.30-1+cuda$CUDA_VERSION \
      libcudnn8-dev=8.0.4.30-1+cuda$CUDA_VERSION \
      libnccl2=2.7.8-1+cuda$CUDA_VERSION \
      libnccl-dev=2.7.8-1+cuda$CUDA_VERSION && \
    ln -s /usr/local/cuda-$CUDA_VERSION /usr/local/cuda && \
    ln -s /usr/local/cuda/lib64/stubs/libcuda.so /usr/local/cuda/lib64/stubs/libcuda.so.1

# Use Bazelisk to ensure the proper bazel version is used.
RUN cd /usr/local/src && \
    wget --no-verbose "https://github.com/bazelbuild/bazelisk/releases/download/v1.7.4/bazelisk-linux-amd64" && \
    mv bazelisk-linux-amd64 /usr/local/bin/bazel && \
    chmod u+x /usr/local/bin/bazel

# Fetch TensorFlow & install dependencies.
RUN cd /usr/local/src && \
    git clone https://github.com/tensorflow/tensorflow && \
    cd tensorflow && \
    git checkout tags/v2.4.1 && \
    pip install keras_applications --no-deps && \
    pip install keras_preprocessing --no-deps

# Create a TensorFlow wheel for CPU
RUN cd /usr/local/src/tensorflow && \
    cat /dev/null | ./configure && \
    bazel build --config=opt \
                --config=v2 \
                --cxxopt="-D_GLIBCXX_USE_CXX11_ABI=0" \
                //tensorflow/tools/pip_package:build_pip_package && \
    bazel-bin/tensorflow/tools/pip_package/build_pip_package /tmp/tensorflow_cpu && \
    bazel clean

# Install TensorFlow CPU wheel which is required to build the GCS & addons libraries.
RUN pip install /tmp/tensorflow_cpu/tensorflow*.whl

# Build TensorFlow addons library against TensorFlow CPU.
RUN cd /usr/local/src/ && \
    git clone https://github.com/tensorflow/addons && \
    cd addons && \
    git checkout tags/v0.12.1 && \
    python ./configure.py && \
    bazel build --enable_runfiles build_pip_pkg && \
    bazel-bin/build_pip_pkg /tmp/tfa_cpu && \
    bazel clean

# Build tensorflow_gcs_config library against TensorFlow CPU.
ADD tensorflow-gcs-config /usr/local/src/tensorflow_gcs_config/
RUN cd /usr/local/src/tensorflow_gcs_config && \
    apt-get install -y libcurl4-openssl-dev && \
    python setup.py bdist_wheel -d /tmp/tensorflow_gcs_config && \
    bazel clean

# Create a tensorflow wheel for GPU/cuda
ENV TF_NEED_CUDA=1
ENV TF_CUDA_VERSION=$CUDA_MAJOR_VERSION.$CUDA_MINOR_VERSION
# 3.7 (K80), 6.0 (P100), 7.0 (V100), 7.5 (T4): https://developer.nvidia.com/cuda-gpus
ENV TF_CUDA_COMPUTE_CAPABILITIES=3.7,6.0,7.0,7.5
ENV TF_CUDNN_VERSION=8
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

# Install TensorFlow GPU wheel which to build addons against.
RUN pip install /tmp/tensorflow_gpu/tensorflow*.whl

# Build TensorFlow addons library against TensorFlow GPU.
ENV CUDA_TOOLKIT_PATH=/usr/local/cuda
ENV CUDNN_INSTALL_PATH=/usr/lib/x86_64-linux-gnu
RUN cd /usr/local/src/addons && \
    python ./configure.py && \
    bazel build --enable_runfiles build_pip_pkg && \
    bazel-bin/build_pip_pkg /tmp/tfa_gpu && \
    bazel clean

# Print out the built .whl files
RUN ls -R /tmp/tensorflow*
