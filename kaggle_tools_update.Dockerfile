# This Dockerfile is a temporary solution until we
# resolved the broken main build.

# This Dockerfile creates a new image based on our
# current published python image with the latest
# version of the LearnTools library to allow us
# to release new Learn content. It also configures
# pip to work out-of-the-box when internet access
# is enabled.

# Usage:
#   docker rmi gcr.io/kaggle-images/python:pinned
#   docker build --rm -t kaggle/python-build -f kaggle_tools_update.Dockerfile .
#   ./test
#   ./push (if tests are passing)

# Pull the last build manually tagged as "pinned". 
FROM gcr.io/kaggle-images/python:pinned

RUN pip install --upgrade git+https://github.com/Kaggle/learntools