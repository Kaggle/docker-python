ARG BASE_IMAGE

FROM ${BASE_IMAGE} AS builder

ARG PACKAGE_VERSION

# Use Bazelisk to ensure the proper bazel version is used.
RUN cd /usr/local/src && \
    wget --no-verbose "https://github.com/bazelbuild/bazelisk/releases/download/v1.11.0/bazelisk-linux-amd64" && \
    mv bazelisk-linux-amd64 /usr/local/bin/bazel && \
    chmod u+x /usr/local/bin/bazel

# Fetch TensorFlow & install dependencies.
RUN cd /usr/local/src && \
    git clone https://github.com/tensorflow/tensorflow && \
    cd tensorflow && \
    git checkout tags/v${PACKAGE_VERSION} && \
    # TODO(rosbo): Is it really needed?
    pip install keras_applications --no-deps && \
    pip install keras_preprocessing --no-deps

# Create a TensorFlow wheel for TPU
RUN cd /usr/local/src/tensorflow && \
    cat /dev/null | ./configure && \
    bazel build \
            --config=opt \
            --distinct_host_configuration=true \
            --define=framework_shared_object=true \
            --define=with_tpu_support=true \
            --copt=-DLIBTPU_ON_GCE \
        //tensorflow/tools/pip_package:build_pip_package \
            --local_ram_resources=HOST_RAM*.5

RUN cd /usr/local/src/tensorflow && \
    bazel-bin/tensorflow/tools/pip_package/build_pip_package /tmp/tensorflow_pkg

# Build TensorFlow addons library against TensorFlow CPU.
#RUN cd /usr/local/src/ && \
#    git clone https://github.com/tensorflow/addons && \
#    cd addons && \
#    git checkout tags/v0.12.1 && \
#    python ./configure.py && \
#    bazel build --enable_runfiles build_pip_pkg && \
#    bazel-bin/build_pip_pkg /tmp/tfa_cpu && \
#    bazel clean

# Build tensorflow_gcs_config library against TensorFlow CPU.
#ADD tensorflow-gcs-config /usr/local/src/tensorflow_gcs_config/
#RUN cd /usr/local/src/tensorflow_gcs_config && \
#    apt-get install -y libcurl4-openssl-dev && \
#    python setup.py bdist_wheel -d /tmp/tensorflow_gcs_config && \
#    bazel clean

# Use multi-stage builds to minimize image output size.
FROM alpine:latest
COPY --from=builder /tmp/tensorflow_pkg/tensorflow*.whl /tmp/tensorflow_pkg/