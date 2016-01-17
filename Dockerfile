FROM kaggle/python0:latest

    # Install OpenCV-3 with Python support
RUN cd /usr/local/src/opencv && \
    mkdir build && cd build && \
    cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D WITH_TBB=ON -D WITH_FFMPEG=OFF -D WITH_V4L=ON -D WITH_QT=OFF -D WITH_OPENGL=ON -D PYTHON3_LIBRARY=/opt/conda/lib/libpython3.4m.so -D PYTHON3_INCLUDE_DIR=/opt/conda/include/python3.4m/ -D PYTHON_LIBRARY=/opt/conda/lib/libpython3.4m.so -D PYTHON_INCLUDE_DIR=/opt/conda/include/python3.4m/ .. && \
    make -j $(nproc) && make install && \
    echo "/usr/local/lib" > /etc/ld.so.conf.d/opencv.conf && ldconfig && \
    cp /usr/local/lib/python3.4/site-packages/cv2.cpython-34m.so /opt/conda/lib/python3.4/site-packages/ 


RUN apt-get -y install libgeos-dev && \
    cd /usr/local/src && git clone https://github.com/matplotlib/basemap.git && \
    export GEOS_DIR=/usr/local && \
    cd basemap && python setup.py install && \
    # Pillow (PIL)
    apt-get -y install zlib1g-dev liblcms2-dev libwebp-dev && \
    pip install Pillow && \
    cd /usr/local/src && git clone https://github.com/vitruvianscience/opendeep.git && \
    cd opendeep && python setup.py develop  && \
    # Cartopy and dependencies
    yes | conda install proj4 && \
    pip install packaging && \
    cd /usr/local/src && git clone https://github.com/Toblerity/Shapely.git && \
    cd Shapely && python setup.py install && \
    cd /usr/local/src && git clone https://github.com/SciTools/cartopy.git && \
    cd cartopy && python setup.py install && \
    pip install ibis-framework
    
    # set backend for matplotlib to Agg
RUN matplotlibrc_path=$(python -c "import site, os, fileinput; packages_dir = site.getsitepackages()[0]; print(os.path.join(packages_dir, 'matplotlib', 'mpl-data', 'matplotlibrc'))") && \
    sed -i 's/^backend      : Qt4Agg/backend      : Agg/' $matplotlibrc_path

    # MXNet
RUN cd /usr/local/src && git clone --recursive https://github.com/dmlc/mxnet && \
    cd /usr/local/src/mxnet && cp make/config.mk . && sed -i 's/CC = gcc/CC = gcc-4.8/' config.mk && \
    sed -i 's/CXX = g++/CXX = g++-4.8/' config.mk && \
    sed -i 's/ADD_LDFLAGS =/ADD_LDFLAGS = -lstdc++/' config.mk && \
    make && cd python && python setup.py install

    # h2o
    # (This requires python-software-properties; see the MXNet section above for installation.)
    # Java7 install method from http://www.webupd8.org/2012/06/how-to-install-oracle-java-7-in-debian.html
    # and https://stackoverflow.com/a/19391042
RUN apt-get install -y wget unzip && \
    echo "deb http://ppa.launchpad.net/webupd8team/java/ubuntu precise main" | tee -a /etc/apt/sources.list && \
    echo "deb-src http://ppa.launchpad.net/webupd8team/java/ubuntu precise main" | tee -a /etc/apt/sources.list && \
    apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys EEA14886 && \
    apt-get update && \
    echo debconf shared/accepted-oracle-license-v1-1 select true | debconf-set-selections && \
    echo debconf shared/accepted-oracle-license-v1-1 seen true | debconf-set-selections && \
    apt-get install -y oracle-java7-installer && \
    cd /usr/local/src && mkdir h2o && cd h2o && \
    wget http://h2o-release.s3.amazonaws.com/h2o/latest_stable -O latest && \
    wget --no-check-certificate -i latest -O h2o.zip && rm latest && \
    unzip h2o.zip && rm h2o.zip && cp h2o-*/h2o.jar . && \
    pip install `find . -name "*whl"`

    # Stop ipython nbconvert trying to rewrite its folder hierarchy
RUN mkdir -p /root/.jupyter && touch /root/.jupyter/jupyter_nbconvert_config.py && touch /root/.jupyter/migrated && \
    mkdir -p /.jupyter && touch /.jupyter/jupyter_nbconvert_config.py && touch /.jupyter/migrated && \
    # Keras likes to add a config file in a custom directory when it's
    # first imported. This doesn't work with our read-only filesystem, so we
    # have it done now
    python -c "from keras.models import Sequential"

    # TensorFlow
RUN pip install --upgrade https://storage.googleapis.com/tensorflow/linux/cpu/tensorflow-0.6.0-cp34-none-linux_x86_64.whl
