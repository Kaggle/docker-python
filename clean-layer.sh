#!/bin/bash
#
# This scripts should be called at the end of each RUN command
# in the Dockerfiles.
#
# Each RUN command creates a new layer that is stored separately.
# At the end of each command, we should ensure we clean up downloaded
# archives and source files used to produce binary to reduce the size
# of the layer.
set -e
set -x

# Delete files that pip caches when installing a package.
rm -rf /root/.cache/pip/*
# Delete old downloaded archive files 
apt-get autoremove -y
# Delete downloaded archive files
apt-get clean
# Ensures the current working directory won't be deleted
cd /usr/local/src/
# Delete source files used for building binaries
rm -rf /usr/local/src/*
# Delete conda downloaded tarballs
conda clean -y --tarballs
