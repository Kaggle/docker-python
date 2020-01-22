ARG BASE_TAG=staging

FROM nvidia/cuda:10.0-cudnn7-devel-ubuntu16.04 AS nvidia
FROM gcr.io/kaggle-images/python-tensorflow-whl:2.1.0-py36 as tensorflow_whl
FROM gcr.io/kaggle-images/python:${BASE_TAG}

ADD clean-layer.sh  /tmp/clean-layer.sh

# Cuda support
COPY --from=nvidia /etc/apt/sources.list.d/cuda.list /etc/apt/sources.list.d/
COPY --from=nvidia /etc/apt/sources.list.d/nvidia-ml.list /etc/apt/sources.list.d/
COPY --from=nvidia /etc/apt/trusted.gpg /etc/apt/trusted.gpg.d/cuda.gpg

# Ensure the cuda libraries are compatible with the custom Tensorflow wheels.
# TODO(b/120050292): Use templating to keep in sync or COPY installed binaries from it.
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
ENV LD_LIBRARY_PATH="/usr/local/nvidia/lib64:/usr/local/cuda/lib64:/usr/local/cuda/lib64/stubs"
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
    ln -s /usr/local/cuda/lib64/stubs/libcuda.so /usr/local/cuda/lib64/stubs/libcuda.so.1 && \
    /tmp/clean-layer.sh

# Install OpenCL (required by LightGBM GPU version)
RUN apt-get install -y ocl-icd-libopencl1 && \
    /tmp/clean-layer.sh

# Install JAX
ENV JAX_PYTHON_VERSION=cp36
ENV JAX_CUDA_VERSION=cuda100
ENV JAX_PLATFORM=linux_x86_64
ENV JAX_BASE_URL="https://storage.googleapis.com/jax-releases"

RUN  pip install --upgrade $JAX_BASE_URL/$JAX_CUDA_VERSION/jaxlib-0.1.37-$JAX_PYTHON_VERSION-none-$JAX_PLATFORM.whl && \
     pip install --upgrade jax

# Reinstall packages with a separate version for GPU support.
COPY --from=tensorflow_whl /tmp/tensorflow_gpu/*.whl /tmp/tensorflow_gpu/
RUN pip uninstall -y tensorflow && \
    pip install /tmp/tensorflow_gpu/tensorflow*.whl && \
    rm -rf /tmp/tensorflow_gpu && \
    conda remove --force -y pytorch torchvision torchaudio cpuonly && \
    conda install -y pytorch torchvision torchaudio cudatoolkit=10.0 -c pytorch && \
    pip uninstall -y mxnet && \
    # b/126259508 --no-deps prevents numpy from being downgraded.
    pip install --no-deps mxnet-cu100 && \
    /tmp/clean-layer.sh

# Install GPU-only packages
RUN pip install pycuda && \
    pip install cupy-cuda100 && \
    pip install pynvrtc && \
    /tmp/clean-layer.sh

# Re-add TensorBoard Jupyter extension patch
# b/139212522 re-enable TensorBoard once solution for slowdown is implemented.
# ADD patches/tensorboard/notebook.py /opt/conda/lib/python3.6/site-packages/tensorboard/notebook.py
