ARG BASE_IMAGE

FROM $BASE_IMAGE

# We need to define the ARG here to get the ARG below the FROM statement to access it within this build context
# See: https://docs.docker.com/engine/reference/builder/#understand-how-arg-and-from-interact
ARG PYTHON_WHEEL_VERSION
ARG PYTHON_VERSION_PATH
ARG TENSORFLOW_VERSION
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

# Prereqs
# This is needed for cv2 (opencv-python):
# https://stackoverflow.com/questions/55313610/importerror-libgl-so-1-cannot-open-shared-object-file-no-such-file-or-directo
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

# Install all the packages together for maximum compatibility.
# Additional useful packages should be added in the requirements.txt
# Bring in the requirements.txt and replace variables in it:
RUN apt-get install -y gettext
ADD tpu/requirements.in /kaggle_requirements.in
RUN envsubst < /kaggle_requirements.in > /requirements.in

# Install uv and then install the requirements:
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
RUN export PATH="${HOME}/.local/bin:${PATH}" && \
    uv pip compile --system --prerelease=allow \
        --verbose \
        --upgrade \
        --find-links=https://storage.googleapis.com/jax-releases/libtpu_releases.html \
        --find-links=https://storage.googleapis.com/libtpu-releases/index.html \
        --find-links=https://storage.googleapis.com/libtpu-wheels/index.html \
        --find-links=https://download.pytorch.org/whl/torch_stable.html \
        --emit-find-links \
        --no-emit-package pip \
        --no-emit-package setuptools \
        --output-file /requirements.txt \
        /requirements.in && \
    uv pip install --system --prerelease=allow --force-reinstall \
        -r /requirements.txt && \
    uv cache clean && \
    /tmp/clean-layer.sh
ENV PATH="~/.local/bin:${PATH}"

# Kaggle Model Hub patches:
ADD patches/kaggle_module_resolver.py /usr/local/lib/${PYTHON_VERSION_PATH}/site-packages/tensorflow_hub/kaggle_module_resolver.py
RUN sed -i '/from tensorflow_hub import uncompressed_module_resolver/a from tensorflow_hub import kaggle_module_resolver' /usr/local/lib/${PYTHON_VERSION_PATH}/site-packages/tensorflow_hub/config.py
RUN sed -i '/_install_default_resolvers()/a \ \ registry.resolver.add_implementation(kaggle_module_resolver.KaggleFileResolver())' /usr/local/lib/${PYTHON_VERSION_PATH}/site-packages/tensorflow_hub/config.py

# Set these env vars so that they don't produce errs calling the metadata server to load them:
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
