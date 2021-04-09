ARG BASE_TAG=staging

FROM nvidia/cuda:11.0-cudnn8-devel-ubuntu18.04 AS nvidia
FROM gcr.io/kaggle-images/python-tensorflow-whl:2.4.1-py37-2 as tensorflow_whl
FROM gcr.io/kaggle-images/python:${BASE_TAG}

ADD clean-layer.sh  /tmp/clean-layer.sh

# Cuda support
COPY --from=nvidia /etc/apt/sources.list.d/cuda.list /etc/apt/sources.list.d/
COPY --from=nvidia /etc/apt/sources.list.d/nvidia-ml.list /etc/apt/sources.list.d/
COPY --from=nvidia /etc/apt/trusted.gpg /etc/apt/trusted.gpg.d/cuda.gpg
# See b/142337634#comment28
RUN sed -i 's/deb https:\/\/developer.download.nvidia.com/deb http:\/\/developer.download.nvidia.com/' /etc/apt/sources.list.d/*.list

# Ensure the cuda libraries are compatible with the custom Tensorflow wheels.
# TODO(b/120050292): Use templating to keep in sync or COPY installed binaries from it.
ENV CUDA_MAJOR_VERSION=11
ENV CUDA_MINOR_VERSION=0
ENV CUDA_VERSION=$CUDA_MAJOR_VERSION.$CUDA_MINOR_VERSION
LABEL com.nvidia.volumes.needed="nvidia_driver"
LABEL com.nvidia.cuda.version="${CUDA_VERSION}"
ENV PATH=/usr/local/nvidia/bin:/usr/local/cuda/bin:/opt/bin:${PATH}
# The stub is useful to us both for built-time linking and run-time linking, on CPU-only systems.
# When intended to be used with actual GPUs, make sure to (besides providing access to the host
# CUDA user libraries, either manually or through the use of nvidia-docker) exclude them. One
# convenient way to do so is to obscure its contents by a bind mount:
#   docker run .... -v /non-existing-directory:/usr/local/cuda/lib64/stubs:ro ...
ENV LD_LIBRARY_PATH_NO_STUBS="/usr/local/nvidia/lib64:/usr/local/cuda/lib64:$LD_LIBRARY_PATH"
ENV LD_LIBRARY_PATH="/usr/local/nvidia/lib64:/usr/local/cuda/lib64:/usr/local/cuda/lib64/stubs:$LD_LIBRARY_PATH"
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
    ln -s /usr/local/cuda/lib64/stubs/libcuda.so /usr/local/cuda/lib64/stubs/libcuda.so.1 && \
    /tmp/clean-layer.sh

# Install OpenCL & libboost (required by LightGBM GPU version)
RUN apt-get install -y ocl-icd-libopencl1 clinfo libboost-all-dev && \
    mkdir -p /etc/OpenCL/vendors && \
    echo "libnvidia-opencl.so.1" > /etc/OpenCL/vendors/nvidia.icd && \
    /tmp/clean-layer.sh

# When using pip in a conda environment, conda commands should be ran first and then
# the remaining pip commands: https://www.anaconda.com/using-pip-in-a-conda-environment/
# However, because this image is based on the CPU image, this isn't possible but better
# to put them at the top of this file to minize conflicts.
RUN conda remove --force -y pytorch torchvision torchaudio cpuonly && \
    conda install "pytorch=1.7" "torchvision=0.8" "torchaudio=0.7" "torchtext=0.8" "cudf=0.16" "cuml=0.16" cudatoolkit=$CUDA_VERSION && \
    /tmp/clean-layer.sh

# Install LightGBM with GPU
RUN pip uninstall -y lightgbm && \
    cd /usr/local/src && \
    git clone --recursive https://github.com/microsoft/LightGBM && \
    cd LightGBM && \
    git checkout tags/v3.2.0 && \
    mkdir build && cd build && \
    cmake -DUSE_GPU=1 -DOpenCL_LIBRARY=/usr/local/cuda/lib64/libOpenCL.so -DOpenCL_INCLUDE_DIR=/usr/local/cuda/include/ .. && \
    make -j$(nproc) && \
    cd /usr/local/src/LightGBM/python-package && \
    python setup.py install --precompile && \
    mkdir -p /etc/OpenCL/vendors && \
    echo "libnvidia-opencl.so.1" > /etc/OpenCL/vendors/nvidia.icd && \
    /tmp/clean-layer.sh

# Install JAX (Keep JAX version in sync with CPU image)
RUN  pip install jax==0.2.12 jaxlib==0.1.64+cuda$CUDA_MAJOR_VERSION$CUDA_MINOR_VERSION -f https://storage.googleapis.com/jax-releases/jax_releases.html && \
     /tmp/clean-layer.sh

# Reinstall packages with a separate version for GPU support.
COPY --from=tensorflow_whl /tmp/tensorflow_gpu/*.whl /tmp/tensorflow_gpu/
RUN pip uninstall -y tensorflow && \
    pip install /tmp/tensorflow_gpu/tensorflow*.whl && \
    rm -rf /tmp/tensorflow_gpu && \
    pip uninstall -y mxnet && \
    pip install mxnet-cu$CUDA_MAJOR_VERSION$CUDA_MINOR_VERSION && \
    /tmp/clean-layer.sh

 # Reinstall TensorFlow addons (TFA) with GPU support.
COPY --from=tensorflow_whl /tmp/tfa_gpu/*.whl /tmp/tfa_gpu/
RUN pip install /tmp/tfa_gpu/tensorflow*.whl && \
    rm -rf /tmp/tfa_gpu/ && \
    /tmp/clean-layer.sh

# Install GPU-only packages
RUN pip install pycuda && \
    pip install cupy-cuda$CUDA_MAJOR_VERSION$CUDA_MINOR_VERSION && \
    pip install pynvrtc && \
    pip install nnabla-ext-cuda$CUDA_MAJOR_VERSION$CUDA_MINOR_VERSION && \
    /tmp/clean-layer.sh

# Re-add TensorBoard Jupyter extension patch
# b/139212522 re-enable TensorBoard once solution for slowdown is implemented.
# ADD patches/tensorboard/notebook.py /opt/conda/lib/python3.7/site-packages/tensorboard/notebook.py

# Remove the CUDA stubs.
ENV LD_LIBRARY_PATH="$LD_LIBRARY_PATH_NO_STUBS"
