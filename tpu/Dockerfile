ARG BASE_IMAGE

FROM $BASE_IMAGE

# We need to define the ARG here to get the ARG below the FROM statement to access it within this build context
# See: https://docs.docker.com/engine/reference/builder/#understand-how-arg-and-from-interact
ARG PYTHON_WHEEL_VERSION
ARG PYTHON_VERSION_PATH
ARG TF_LINUX_WHEEL_VERSION
ARG TORCH_LINUX_WHEEL_VERSION
ARG TORCH_VERSION
ARG TENSORFLOW_VERSION
ARG TF_LIBTPU_VERSION
ARG JAX_VERSION
ARG TORCHVISION_VERSION
ARG TORCHTEXT_VERSION
ARG TORCHAUDIO_VERSION

ENV ISTPUVM=1

ADD tpu/clean-layer.sh  /tmp/clean-layer.sh
ADD patches/nbconvert-extensions.tpl /opt/kaggle/nbconvert-extensions.tpl
ADD patches/template_conf.json /opt/kaggle/conf.json

# Add BigQuery client proxy settings, kaggle secrets etc.
ENV PYTHONUSERBASE "/root/.local"
ADD patches/kaggle_secrets.py /root/.local/lib/${PYTHON_VERSION_PATH}/site-packages/kaggle_secrets.py
ADD patches/kaggle_session.py /root/.local/lib/${PYTHON_VERSION_PATH}/site-packages/kaggle_session.py
ADD patches/kaggle_web_client.py /root/.local/lib/${PYTHON_VERSION_PATH}/site-packages/kaggle_web_client.py
ADD patches/kaggle_datasets.py /root/.local/lib/${PYTHON_VERSION_PATH}/site-packages/kaggle_datasets.py

# Disable GCP integrations for now
# ADD patches/kaggle_gcp.py /root/.local/lib/${PYTHON_VERSION_PATH}/site-packages/kaggle_gcp.py

# Disable logging to file (why do we need this?)
# ADD patches/log.py /root/.local/lib/${PYTHON_VERSION_PATH}/site-packages/log.py

# sitecustomize adds significant latency to ipython kernel startup and should only be added if needed
# ADD patches/sitecustomize.py /root/.local/lib/${PYTHON_VERSION_PATH}/site-packages/sitecustomize.py

# Prereqs
# This is needed for cv2 (opencv-python):
# https://stackoverflow.com/questions/55313610/importerror-libgl-so-1-cannot-open-shared-object-file-no-such-file-or-directo
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

# Install all the packages together for maximum compatibility.

# Install Tensorflow.

# Install Pytorch & related packages
# https://cloud.google.com/tpu/docs/pytorch-xla-ug-tpu-vm#changing_pytorch_version
# The URL doesn't include patch version. i.e. must use 1.11 instead of 1.11.0
# We need to keep the numpy version the same as the installed tf one but compatible with other installs.

# Install JAX & related packages
# https://cloud.google.com/tpu/docs/jax-quickstart-tpu-vm#install_jax_on_your_cloud_tpu_vm

# Packages needed by the Notebook editor

# Additional useful packages should be added here

RUN pip install tensorflow_hub https://storage.googleapis.com/cloud-tpu-tpuvm-artifacts/tensorflow/tf-${TENSORFLOW_VERSION}/tensorflow-${TENSORFLOW_VERSION}-${PYTHON_WHEEL_VERSION}-${PYTHON_WHEEL_VERSION}-${TF_LINUX_WHEEL_VERSION}.whl tensorflow-probability tensorflow-io \
    torch~=${TORCH_VERSION} https://storage.googleapis.com/pytorch-xla-releases/wheels/tpuvm/torch_xla-${TORCH_VERSION}+libtpu-${PYTHON_WHEEL_VERSION}-${PYTHON_WHEEL_VERSION}-${TORCH_LINUX_WHEEL_VERSION}.whl torchvision==${TORCHVISION_VERSION} torchtext==${TORCHTEXT_VERSION} torchaudio==${TORCHAUDIO_VERSION} \
    jax[tpu]==${JAX_VERSION} -f https://storage.googleapis.com/jax-releases/libtpu_releases.html trax flax optax git+https://github.com/deepmind/dm-haiku jraph distrax \
    papermill jupyterlab python-lsp-server[all] "jupyter-lsp==1.5.1" \
    pandas matplotlib opencv-python-headless librosa accelerate diffusers scikit-learn transformers \
    seaborn timm albumentations einops pyarrow fastparquet opencv-python \
    kagglehub && \
    /tmp/clean-layer.sh

# b/318672157 Install Keras 3 for loading models.
# We ignore dependencies for now since tf2.15 should work despite pip saying it won't.
RUN pip install --no-dependencies "keras>3" keras-cv keras-nlp && \
    /tmp/clean-layer.sh

# Tensorflow libtpu:
RUN curl --output /lib/libtpu.so https://storage.googleapis.com/cloud-tpu-tpuvm-artifacts/libtpu/${TF_LIBTPU_VERSION}/libtpu.so

# Kaggle Model Hub patches:
ADD patches/kaggle_module_resolver.py /usr/local/lib/${PYTHON_VERSION_PATH}/site-packages/tensorflow_hub/kaggle_module_resolver.py
RUN sed -i '/from tensorflow_hub import uncompressed_module_resolver/a from tensorflow_hub import kaggle_module_resolver' /usr/local/lib/${PYTHON_VERSION_PATH}/site-packages/tensorflow_hub/config.py
RUN sed -i '/_install_default_resolvers()/a \ \ registry.resolver.add_implementation(kaggle_module_resolver.KaggleFileResolver())' /usr/local/lib/${PYTHON_VERSION_PATH}/site-packages/tensorflow_hub/config.py

# Monkey-patch the default TPU to the local (TPU VM).
RUN sed -i 's/tpu=None,/tpu="local",/' /usr/local/lib/${PYTHON_VERSION_PATH}/site-packages/tensorflow/python/distribute/cluster_resolver/tpu/tpu_cluster_resolver.py

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
