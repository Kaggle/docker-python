FROM continuumio/anaconda3:latest

RUN conda install pip statsmodels seaborn python-dateutil nltk scikit-learn -y -q && \
    pip install pytagcloud pyyaml ggplot theano joblib husl geopy ml_metrics && \
    apt-get install -y libglib2.0-0 libxext6 libsm6 libxrender1 libfontconfig1 --fix-missing && \
    apt-get update && apt-get install -y git && apt-get install -y build-essential && \
    #word cloud
    pip install git+git://github.com/amueller/word_cloud.git && \
    #xgboost
    cd /usr/local/src && mkdir xgboost && cd xgboost && \
    git clone https://github.com/dmlc/xgboost.git && cd xgboost && \
    make && cd wrapper && python setup.py install && \
    #lasagne
    cd /usr/local/src && mkdir Lasagne && cd Lasagne && \
    git clone https://github.com/Lasagne/Lasagne.git && cd Lasagne && \
    pip install -r requirements.txt && python setup.py install && \
    #keras
    cd /usr/local/src && mkdir keras && cd keras && \
    git clone https://github.com/fchollet/keras.git && \
    cd keras && python setup.py install && \
    #neon
    cd /usr/local/src && \
    git clone https://github.com/NervanaSystems/neon.git && \
    cd neon && pip install -e . && \
    #nolearn
    cd /usr/local/src && mkdir nolearn && cd nolearn && \
    git clone https://github.com/dnouri/nolearn.git && cd nolearn && \
    echo "x" > README.rst && echo "x" > CHANGES.rst && \
    python setup.py install && \
    # put theano compiledir inside /tmp (it needs to be in writable dir)
    printf "[global]\nbase_compiledir = /tmp/.theano\n" > /.theanorc && \
    cd /usr/local/src &&  git clone https://github.com/pybrain/pybrain && \
    cd pybrain && python setup.py install && \
    # Base ATLAS plus tSNE
    apt-get install -y libatlas-base-dev && pip install tsne
    
    # set backend for matplotlibrc to Agg
RUN matplotlibrc_path=$(python -c "import site, os, fileinput; packages_dir = site.getsitepackages()[0]; print(os.path.join(packages_dir, 'matplotlib', 'mpl-data', 'matplotlibrc'))") && \
    sed -i 's/^backend      : Qt4Agg/backend      : Agg/' $matplotlibrc_path

    # Install OpenCV-3 with Python support
    # We build libpng 1.6.17 from source because the apt-get version is too out of
    # date for OpenCV-3.
RUN apt-get -y install cmake imagemagick && \
    apt-get -y install libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev && \
    apt-get -y install libtbb2 libtbb-dev libjpeg-dev libpng-dev libtiff-dev libjasper-dev libdc1394-22-dev && \
    cd /usr/local/src && wget http://downloads.sourceforge.net/libpng/libpng-1.6.17.tar.xz && \
    tar -xf libpng-1.6.17.tar.xz && cd libpng-1.6.17 && \
    ./configure --prefix=/usr --disable-static && make && make install && \
    cd /usr/local/src && git clone https://github.com/Itseez/opencv.git && \
    cd /usr/local/src/opencv && \
    mkdir build && cd build && \
    cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D WITH_TBB=ON -D WITH_FFMPEG=OFF -D BUILD_NEW_PYTHON_SUPPORT=ON -D WITH_V4L=ON -D WITH_QT=ON -D WITH_OPENGL=ON -D PYTHON3_LIBRARY=/opt/conda/lib/libpython3.4m.so -D PYTHON3_INCLUDE_DIR=/opt/conda/include/python3.4m/ .. && \
    make -j $(nproc) && make install && \
    echo "/usr/local/lib" > /etc/ld.so.conf.d/opencv.conf && ldconfig && \
    cp /usr/local/lib/python3.4/site-packages/cv2.cpython-34m.so /opt/conda/lib/python3.4/site-packages/ 

    # matplotlib-toolkits
RUN apt-get -y install libgeos-dev && \
    cd /usr/local/src && git clone https://github.com/matplotlib/basemap.git && \
    export GEOS_DIR=/usr/local && \
    cd basemap && python setup.py install && \
    # Pillow (PIL)
    apt-get -y install zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev && \
    pip install Pillow

