FROM nvidia/cuda:9.1-cudnn7-devel-ubuntu16.04 AS nvidia
FROM gcr.io/kaggle-images/python-tensorflow-whl:1.11.0-py36 as tensorflow_whl
FROM gcr.io/kaggle-images/python:staging

# Cuda support
COPY --from=nvidia /etc/apt/sources.list.d/cuda.list /etc/apt/sources.list.d/
COPY --from=nvidia /etc/apt/sources.list.d/nvidia-ml.list /etc/apt/sources.list.d/
COPY --from=nvidia /etc/apt/trusted.gpg /etc/apt/trusted.gpg.d/cuda.gpg

ENV CUDA_VERSION=9.1.85
ENV CUDA_PKG_VERSION=9-1=$CUDA_VERSION-1
LABEL com.nvidia.volumes.needed="nvidia_driver"
LABEL com.nvidia.cuda.version="${CUDA_VERSION}"
ENV PATH=/usr/local/nvidia/bin:/usr/local/cuda/bin:${PATH}
# The stub is useful to us both for built-time linking and run-time linking, on CPU-only systems.
# When intended to be used with actual GPUs, make sure to (besides providing access to the host
# CUDA user libraries, either manually or through the use of nvidia-docker) exclude them. One
# convenient way to do so is to obscure its contents by a bind mount:
#   docker run .... -v /non-existing-directory:/usr/local/cuda/lib64/stubs:ro ...
ENV LD_LIBRARY_PATH="/usr/local/nvidia/lib64:/usr/local/cuda/lib64:/usr/local/cuda/lib64/stubs"
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility
ENV NVIDIA_REQUIRE_CUDA="cuda>=9.0"
RUN apt-get update && apt-get install -y --no-install-recommends \
      cuda-cupti-$CUDA_PKG_VERSION \
      cuda-cudart-$CUDA_PKG_VERSION \
      cuda-libraries-$CUDA_PKG_VERSION \
      cuda-libraries-dev-$CUDA_PKG_VERSION \
      cuda-nvml-dev-$CUDA_PKG_VERSION \
      cuda-minimal-build-$CUDA_PKG_VERSION \
      cuda-command-line-tools-$CUDA_PKG_VERSION \
      libcudnn7=7.2.1.38-1+cuda9.0 \
      libcudnn7-dev=7.2.1.38-1+cuda9.0 \
      libnccl2=2.2.12-1+cuda9.1 \
      libnccl-dev=2.2.12-1+cuda9.1 && \
    ln -s /usr/local/cuda-9.1 /usr/local/cuda && \
    ln -s /usr/local/cuda/lib64/stubs/libcuda.so /usr/local/cuda/lib64/stubs/libcuda.so.1

# Reinstall packages with a separate version for GPU support
# Tensorflow
COPY --from=tensorflow_whl /tmp/tensorflow_gpu/*.whl /tmp/tensorflow_gpu/
RUN pip uninstall -y tensorflow && \
    pip install /tmp/tensorflow_gpu/tensorflow*.whl && \
    rm -rf /tmp/tensorflow_gpu && \
    conda uninstall -y pytorch-cpu torchvision-cpu && \
    conda install -y pytorch torchvision -c pytorch

# Install GPU-only packages
RUN pip install pycuda
