#!/bin/bash
cd /opt
xargs apt-get install -y < /tmp/requirements.opencv3
# checkout opencv
git clone https://github.com/opencv/opencv.git
cd opencv
git checkout 3.4.0
cd ..
# checkout opencv_contrib
git clone https://github.com/opencv/opencv_contrib.git
cd opencv_contrib
git checkout 3.4.0
cd ..
# cmake
cd opencv
mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE \
      -D CMAKE_INSTALL_PREFIX=/usr/local \
      -D INSTALL_C_EXAMPLES=ON \
      -D INSTALL_PYTHON_EXAMPLES=ON \
      -D WITH_TBB=ON \
      -D WITH_V4L=ON \
      -D WITH_OPENGL=ON \
      -D WITH_FFMPEG=ON \
      -D WITH_QT=OFF \
      -D WITH_GTK=OFF \
      -D OPENCV_EXTRA_MODULES_PATH=../../opencv_contrib/modules \
      -D BUILD_EXAMPLES=ON ..
# make in parallel
make -j
make install
sh -c 'echo "/usr/local/lib" >> /etc/ld.so.conf.d/opencv.conf'
ldconfig
