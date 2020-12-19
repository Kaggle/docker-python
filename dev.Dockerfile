# This Dockerfile builds an image to quickly iterate on the kaggle libraries.
#
# Create a new image with the latest kaggle librairies using the latest image
# built by CI with a successful test run as the base.
#
# Usage:
#   cd path/to/docker-python
#   docker build -t kaggle/python-dev -f dev.Dockerfile .
#
#   # you can run a container using the image using:
#   docker run -it --rm kaggle/python-dev /bin/bash
#
#   # you can run the tests against this new image using:
#   ./test -i kaggle/python-dev -p test_user_secrets.py
#
FROM gcr.io/kaggle-images/python:staging

ADD patches/kaggle_gcp.py /root/.local/lib/python3.7/site-packages/kaggle_gcp.py
ADD patches/kaggle_secrets.py /root/.local/lib/python3.7/site-packages/kaggle_secrets.py
ADD patches/kaggle_session.py /root/.local/lib/python3.7/site-packages/kaggle_session.py
ADD patches/kaggle_web_client.py /root/.local/lib/python3.7/site-packages/kaggle_web_client.py
ADD patches/kaggle_datasets.py /root/.local/lib/python3.7/site-packages/kaggle_datasets.py
ADD patches/sitecustomize.py /root/.local/lib/python3.7/site-packages/sitecustomize.py