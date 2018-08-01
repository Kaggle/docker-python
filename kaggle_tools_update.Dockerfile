# This Dockerfile is a temporary solution until we
# resolved the broken main build.

# This Dockerfile creates a new image based on our
# current published python image with the latest
# version of the LearnTools library to allow us
# to release new Learn content.

# Usage:
#   docker rmi gcr.io/kaggle-images/python:latest
#   docker build --rm -t kaggle/python-build -f kaggle_tools_update.Dockerfile .
#   ./test
#   ./push (if tests are passing)

FROM gcr.io/kaggle-images/python:latest

RUN pip install --upgrade git+https://github.com/Kaggle/learntools
