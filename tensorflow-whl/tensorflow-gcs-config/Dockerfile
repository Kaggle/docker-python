FROM tensorflow/tensorflow:custom-op

ARG TF_VERSION
ARG UID
ARG GID
ARG USERNAME="build"
ARG CONDA_ADD_PACKAGES=""
ARG BAZEL_VERSION=0.24.1
ARG BAZEL_OS=linux

RUN apt-get update && \
    apt-get install -y \
    git \
    curl \
    nano \
    unzip \
    ffmpeg \
    dnsutils

RUN groupadd -g ${GID} ${USERNAME}
RUN useradd -d /home/${USERNAME} -ms /bin/bash -g ${USERNAME} -G root -u $UID ${USERNAME}
USER ${USERNAME}

WORKDIR /home/${USERNAME}

RUN curl -sL https://github.com/bazelbuild/bazel/releases/download/${BAZEL_VERSION}/bazel-${BAZEL_VERSION}-installer-${BAZEL_OS}-x86_64.sh -o bazel-install.sh && \
    bash -x bazel-install.sh --user && \
    rm bazel-install.sh

ARG CONDA_OS=Linux

# Miniconda - Python 3.6, 64-bit, x86, latest
RUN curl -sL https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -o mconda-install.sh && \
    bash -x mconda-install.sh -b -p miniconda && \
    rm mconda-install.sh

ENV PATH="/home/${USERNAME}/miniconda/bin:$PATH"

RUN conda create -y -q -n tensorflow-gcs-config python=3.6 ${CONDA_ADD_PACKAGES}

RUN echo ". /miniconda/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "source activate tensorflow-gcs-config" >> ~/.bashrc

ARG PIP_ADD_PACKAGES=""

RUN /bin/bash -c "source activate tensorflow-gcs-config && python -m pip install -U \
    pytest \
    pylint \
    boto3 \
    twine \
    google-cloud-pubsub==0.39.1 \
    pandas \
    fastavro \
    'tensorflow>=2' \
    ${PIP_ADD_PACKAGES} \
    "

# This just forces a new fetch of the latest TF binary if the version changes.
RUN /bin/bash -c "echo ${TF_VERSION}"
RUN /bin/bash -c "source activate tensorflow-gcs-config && python -m pip install -U 'tensorflow>=2'"

RUN bazel help > /dev/null
