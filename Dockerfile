FROM continuumio/anaconda3:latest

RUN conda install pip statsmodels seaborn python-dateutil nltk -y && \
    pip install pytagcloud pyyaml ggplot theano joblib husl && \
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
    #nolearn
    cd /usr/local/src && mkdir nolearn && cd nolearn && \
    git clone https://github.com/dnouri/nolearn.git && cd nolearn && \
    python setup.py install && \
    # put theano compiledir inside /tmp (it needs to be in writable dir)
    printf "[global]\nbase_compiledir = /tmp/.theano\n" > /.theanorc
    
    # set backend for matplotlibrc to Agg
RUN matplotlibrc_path=$(python -c "import site, os, fileinput; packages_dir = site.getsitepackages()[0]; print(os.path.join(packages_dir, 'matplotlib', 'mpl-data', 'matplotlibrc'))") && \
    sed -i 's/^backend      : Qt4Agg/backend      : Agg/' $matplotlibrc_path
