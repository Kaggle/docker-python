ARG BASE_IMAGE

FROM $BASE_IMAGE

# We need to define the ARG here to get the ARG below the FROM statement to access it within this build context
# See: https://docs.docker.com/engine/reference/builder/#understand-how-arg-and-from-interact
ARG PYTHON_WHEEL_VERSION
ARG PYTHON_VERSION_PATH
ARG TORCH_LINUX_WHEEL_VERSION
ARG TORCH_VERSION
ARG TORCHVISION_VERSION
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

# Additional useful packages should be added in the requirements.txt

# Bring in the requirements.txt and replace variables in it:
RUN apt-get install -y gettext
ADD tpu/requirements.txt /kaggle_requirements.txt
RUN envsubst < /kaggle_requirements.txt > /requirements.txt

# Install uv and then install the requirements:
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
RUN export PATH="${HOME}/.local/bin:${PATH}" && uv pip install --system -r /requirements.txt --prerelease=allow --find-links https://storage.googleapis.com/jax-releases/libtpu_releases.html && \
    /tmp/clean-layer.sh
ENV PATH="${HOME}/.local/bin:${PATH}"

# Kaggle Model Hub patches:
ADD patches/kaggle_module_resolver.py /usr/local/lib/${PYTHON_VERSION_PATH}/site-packages/tensorflow_hub/kaggle_module_resolver.py
RUN sed -i '/from tensorflow_hub import uncompressed_module_resolver/a from tensorflow_hub import kaggle_module_resolver' /usr/local/lib/${PYTHON_VERSION_PATH}/site-packages/tensorflow_hub/config.py
RUN sed -i '/_install_default_resolvers()/a \ \ registry.resolver.add_implementation(kaggle_module_resolver.KaggleFileResolver())' /usr/local/lib/${PYTHON_VERSION_PATH}/site-packages/tensorflow_hub/config.py

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

LABEL kaggle-lang=python

# Correlate current release with the git hash inside the kernel editor by running `!cat /etc/git_commit`.
RUN echo "$GIT_COMMIT" > /etc/git_commit && echo "$BUILD_DATE" > /etc/build_date
