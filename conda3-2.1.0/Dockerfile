# Copied from 
# https://github.com/ContinuumIO/docker-images/blob/master/anaconda3/Dockerfile
# on 3/26/15
FROM debian:7.4

MAINTAINER Travis Swicegood

RUN apt-get update && apt-get install -y wget bzip2
RUN echo 'export PATH=/opt/conda/bin:$PATH' > /etc/profile.d/conda.sh && \
    wget --quiet http://repo.continuum.io/anaconda3/Anaconda3-2.1.0-Linux-x86_64.sh && \
    /bin/bash /Anaconda3-2.1.0-Linux-x86_64.sh -b -p /opt/conda && \
    rm /Anaconda3-2.1.0-Linux-x86_64.sh && \
    /opt/conda/bin/conda install --yes conda==3.9.0

ENV PATH /opt/conda/bin:$PATH
