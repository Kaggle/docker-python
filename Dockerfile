FROM kaggle/python1:latest
    
    # set backend for matplotlib to Agg
RUN matplotlibrc_path=$(python -c "import site, os, fileinput; packages_dir = site.getsitepackages()[0]; print(os.path.join(packages_dir, 'matplotlib', 'mpl-data', 'matplotlibrc'))") && \
    sed -i 's/^backend      : Qt4Agg/backend      : Agg/' $matplotlibrc_path

    # Stop ipython nbconvert trying to rewrite its folder hierarchy
RUN mkdir -p /root/.jupyter && touch /root/.jupyter/jupyter_nbconvert_config.py && touch /root/.jupyter/migrated && \
    mkdir -p /.jupyter && touch /.jupyter/jupyter_nbconvert_config.py && touch /.jupyter/migrated && \
    # Stop Matplotlib printing junk to the console on first load
    sed -i "s/^.*Matplotlib is building the font cache using fc-list.*$/# Warning removed by Kaggle/g" /opt/conda/lib/python3.4/site-packages/matplotlib/font_manager.py

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
# NOTE: h2o's "latest_stable" file has gone stale with the 3.6.0.8 release--revert to these
# lines when it's fixed
#    cd /usr/local/src && mkdir h2o && cd h2o && \
#    wget http://h2o-release.s3.amazonaws.com/h2o/latest_stable -O latest && \
#    wget --no-check-certificate -i latest -O h2o.zip && rm latest && \
#    unzip h2o.zip && rm h2o.zip && cp h2o-*/h2o.jar . && \
#    pip install `find . -name "*whl"`
    pip install http://h2o-release.s3.amazonaws.com/h2o/rel-tibshirani/8/Python/h2o-3.6.0.8-py2.py3-none-any.whl

    # TensorFlow
RUN pip install --upgrade https://storage.googleapis.com/tensorflow/linux/cpu/tensorflow-0.6.0-cp34-none-linux_x86_64.whl

    # Keras setup
    # Keras likes to add a config file in a custom directory when it's
    # first imported. This doesn't work with our read-only filesystem, so we
    # have it done now
RUN python -c "from keras.models import Sequential"  && \
    # Switch to TF backend
    sed -i 's/theano/tensorflow/' /.keras/keras.json  && \
    # Re-run it to flush any more disk writes
    python -c "from keras.models import Sequential; from keras import backend; print(backend._BACKEND)"

    # More packages: (please add new pip installs here)
RUN pip install --upgrade mpld3 && \
    pip install mplleaflet && \
    pip install gpxpy

