FROM python:3.8

# We need to define the ARG here to get the ARG below the FROM statement to access it within this build context
# See: https://docs.docker.com/engine/reference/builder/#understand-how-arg-and-from-interact
ARG TORCH_VERSION
ARG TENSORFLOW_VERSION
ARG JAX_VERSION
ARG TORCHVISION_VERSION
ARG TORCHTEXT_VERSION
ARG TORCHAUDIO_VERSION

ENV ISTPUVM=1

ADD patches/nbconvert-extensions.tpl /opt/kaggle/nbconvert-extensions.tpl
ADD patches/template_conf.json /opt/kaggle/conf.json

# Add BigQuery client proxy settings, kaggle secrets etc.
ENV PYTHONUSERBASE "/root/.local"
ADD patches/kaggle_secrets.py /root/.local/lib/python3.8/site-packages/kaggle_secrets.py
ADD patches/kaggle_session.py /root/.local/lib/python3.8/site-packages/kaggle_session.py
ADD patches/kaggle_web_client.py /root/.local/lib/python3.8/site-packages/kaggle_web_client.py
ADD patches/kaggle_datasets.py /root/.local/lib/python3.8/site-packages/kaggle_datasets.py

# Disable GCP integrations for now
# ADD patches/kaggle_gcp.py /root/.local/lib/python3.8/site-packages/kaggle_gcp.py

# Disable logging to file (why do we need this?)
# ADD patches/log.py /root/.local/lib/python3.8/site-packages/log.py

# sitecustomize adds significant latency to ipython kernel startup and should only be added if needed
# ADD patches/sitecustomize.py /root/.local/lib/python3.8/site-packages/sitecustomize.py

# Tensorflow wheel:
# When tensorflow is compatible with being installed alongside JAX/Pytorch then we no longer need to include the wheel and can install it directly.
# RUN pip install https://storage.googleapis.com/cloud-tpu-tpuvm-artifacts/tensorflow/tf-${TENSORFLOW_VERSION}/tensorflow-${TENSORFLOW_VERSION}-cp38-cp38-linux_x86_64.whl
# To install offline:
# pip install --no-index --find-links /lib/wheels/sources /lib/wheels/tensorflow-2.9.1-cp38-cp38-linux_x86_64.whl
RUN mkdir -p /lib/wheels && curl --output /lib/wheels/tensorflow-${TENSORFLOW_VERSION}-cp38-cp38-linux_x86_64.whl https://storage.googleapis.com/cloud-tpu-tpuvm-artifacts/tensorflow/tf-${TENSORFLOW_VERSION}/tensorflow-${TENSORFLOW_VERSION}-cp38-cp38-linux_x86_64.whl
RUN curl --output /lib/libtpu.so https://storage.googleapis.com/cloud-tpu-tpuvm-artifacts/libtpu/1.3.0/libtpu.so
RUN pip download -d /lib/wheels/sources /lib/wheels/tensorflow-${TENSORFLOW_VERSION}-cp38-cp38-linux_x86_64.whl

# LIBTPU installed here:
ENV PIP_LIBTPU=/usr/local/lib/python3.8/site-packages/libtpu/libtpu.so
ENV DEFAULT_LIBTPU=/lib/libtpu.so
ENV PYTORCH_LIBTPU=/lib/torch-libtpu.so
ENV JAX_LIBTPU=/lib/jax-libtpu.so

# Install JAX & related packages
# https://cloud.google.com/tpu/docs/jax-quickstart-tpu-vm#install_jax_on_your_cloud_tpu_vm
RUN pip install jax[tpu]==${JAX_VERSION} -f https://storage.googleapis.com/jax-releases/libtpu_releases.html trax flax optax elegy git+https://github.com/deepmind/dm-haiku jraph distrax

RUN cp $PIP_LIBTPU $JAX_LIBTPU

# Install Pytorch & related packages
# https://cloud.google.com/tpu/docs/pytorch-xla-ug-tpu-vm#changing_pytorch_version
# The URL doesn't include patch version. i.e. must use 1.11 instead of 1.11.0
RUN pip install torch==${TORCH_VERSION} torch_xla[tpuvm] -f https://storage.googleapis.com/tpu-pytorch/wheels/tpuvm/torch_xla-${TORCH_VERSION%.*}-cp38-cp38-linux_x86_64.whl torchvision==${TORCHVISION_VERSION} torchtext==${TORCHTEXT_VERSION} torchaudio==${TORCHAUDIO_VERSION}

RUN cp $PIP_LIBTPU $PYTORCH_LIBTPU

# Monkey-patch TF, JAX & PYTORCH to load the correct libtpu.so when they are imported:
RUN sed -i "s|^\(\(.*\)libtpu.configure_library_path.*\)|\1\n\2os.environ['TPU_LIBRARY_PATH'] = '${PYTORCH_LIBTPU}'|" /usr/local/lib/python3.8/site-packages/torch_xla/__init__.py && \
    sed -i "s|^\(\(.*\)libtpu.configure_library_path.*\)|\1\n\2os.environ['TPU_LIBRARY_PATH'] = '${JAX_LIBTPU}'|" /usr/local/lib/python3.8/site-packages/jax/_src/cloud_tpu_init.py

# Packages needed by the Notebook editor:
RUN pip install papermill jupyterlab python-lsp-server[all] jupyterlab-lsp

# Additional useful packages should be added here:
RUN pip install pandas

# Set these env vars so that they don't produce errs calling the metadata server to load them:
ENV TPU_ACCELERATOR_TYPE=v3-8
ENV TPU_PROCESS_ADDRESSES=local

# Metadata
ARG GIT_COMMIT=unknown
ARG BUILD_DATE=unknown

LABEL git-commit=$GIT_COMMIT
LABEL build-date=$BUILD_DATE
ENV GIT_COMMIT=${GIT_COMMIT}
ENV BUILD_DATE=${BUILD_DATE}

LABEL tensorflow-version=$TENSORFLOW_VERSION
LABEL kaggle-lang=python

# Correlate current release with the git hash inside the kernel editor by running `!cat /etc/git_commit`.
RUN echo "$GIT_COMMIT" > /etc/git_commit && echo "$BUILD_DATE" > /etc/build_date
