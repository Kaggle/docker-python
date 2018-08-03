# This Dockerfile is a temporary solution until we
# resolved the broken main build.

# This Dockerfile creates a new image based on our
# current published python image with the latest
# version of the LearnTools library to allow us
# to release new Learn content. It also configures
# pip to work out-of-the-box when internet access
# is enabled.

# Usage:
#   docker rmi gcr.io/kaggle-images/python:latest
#   docker build --rm -t kaggle/python-build -f kaggle_tools_update.Dockerfile .
#   ./test
#   ./push (if tests are passing)

FROM gcr.io/kaggle-images/python:latest

RUN pip install --upgrade git+https://github.com/Kaggle/learntools

# TODO(dsjang): Remove these lines once the docker image build turns green since they are copied from Dockerfile
# to apply on top of the last green.
# Set up an initialization script to be executed before any other commands initiated by the user.
ADD patches/entrypoint.sh /root/entrypoint.sh
RUN chmod +x /root/entrypoint.sh
# NOTE: ENTRYPOINT set by "FROM <image>" should preceed the our own custom entrypoint.
# Currently tini is set as ENTRYPOINT for the base image, and it can be combined with our entrypoint (https://github.com/krallin/tini).
# ENTRYPOINT gets executed by "docker run <image> <command>" and it runs <command> at the end of its execution.
# Make sure tini exists.
RUN /usr/bin/tini -h > /dev/null
ENTRYPOINT ["/usr/bin/tini", "--", "/root/entrypoint.sh"]