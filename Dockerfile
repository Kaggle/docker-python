FROM nvidia/cuda:9.1-cudnn7-devel-ubuntu16.04 AS nvidia

FROM continuumio/anaconda3:5.0.1

# This is necessary to for apt to access HTTPS sources
RUN apt-get update && \
    apt-get install apt-transport-https

COPY --from=nvidia /etc/apt/sources.list.d/cuda.list /etc/apt/sources.list.d/
COPY --from=nvidia /etc/apt/sources.list.d/nvidia-ml.list /etc/apt/sources.list.d/
COPY --from=nvidia /etc/apt/trusted.gpg /etc/apt/trusted.gpg.d/cuda.gpg

# Cuda support.
ENV CUDA_VERSION=9.1.85
ENV CUDA_PKG_VERSION=9-1=$CUDA_VERSION-1
LABEL com.nvidia.volumes.needed="nvidia_driver"
LABEL com.nvidia.cuda.version="${CUDA_VERSION}"
ENV PATH=/usr/local/nvidia/bin:/usr/local/cuda/bin:${PATH}
# The stub is useful to us both for built-time linking and run-time linking, on CPU-only systems.
# When intended to be used with actual GPUs, make sure to (besides providing access to the host
# CUDA user libraries, either manually or through the use of nvidia-docker) exclude them. One
# convenient way to do so is to obscure its contents by a bind mount:
#   docker run .... -v /non-existing-directory:/usr/local/cuda/lib64/stubs:ro ...
ENV LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/usr/local/nvidia/lib64:/usr/local/cuda/lib64:/usr/local/cuda/lib64/stubs"
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility
ENV NVIDIA_REQUIRE_CUDA="cuda>=9.0"
RUN apt-get update && apt-get install -y --no-install-recommends \
      cuda-cudart-$CUDA_PKG_VERSION \
      cuda-libraries-$CUDA_PKG_VERSION \
      cuda-libraries-dev-$CUDA_PKG_VERSION \
      cuda-nvml-dev-$CUDA_PKG_VERSION \
      cuda-minimal-build-$CUDA_PKG_VERSION \
      cuda-command-line-tools-$CUDA_PKG_VERSION \
      libcudnn7=7.0.5.15-1+cuda9.1 \
      libcudnn7-dev=7.0.5.15-1+cuda9.1 && \
    ln -s /usr/local/cuda-9.1 /usr/local/cuda && \
    ln -s /usr/local/cuda/lib64/stubs/libcuda.so /usr/local/cuda/lib64/stubs/libcuda.so.1 && \
    rm -rf /var/lib/apt/lists/*

# Use a fixed apt-get repo to stop intermittent failures due to flaky httpredir connections,
# as described by Lionel Chan at http://stackoverflow.com/a/37426929/5881346
RUN sed -i "s/httpredir.debian.org/debian.uchicago.edu/" /etc/apt/sources.list && \
    apt-get update && apt-get install -y build-essential && \
    # https://stackoverflow.com/a/46498173
    conda update -y conda && conda update -y python && \
    pip install --upgrade pip && \
    apt-get -y install cmake && \
    # Vowpal Rabbit
    #apt-get install -y libboost-program-options-dev zlib1g-dev libboost-python-dev && \
    #cd /usr/lib/x86_64-linux-gnu/ && rm -f libboost_python.a && rm -f libboost_python.so && \
    #ln -sf libboost_python-py34.so libboost_python.so && ln -sf libboost_python-py34.a libboost_python.a && \
    #pip install vowpalwabbit && \
    # Anaconda's scipy is currently behind the main release (1.0)
    pip install scipy --upgrade && \
    pip install seaborn python-dateutil dask pytagcloud pyyaml joblib \
    husl geopy ml_metrics mne pyshp gensim && \
    conda install -y -c conda-forge spacy && python -m spacy download en && \
    python -m spacy download en_core_web_lg && \
    # The apt-get version of imagemagick is out of date and has compatibility issues, so we build from source
    apt-get -y install dbus fontconfig fontconfig-config fonts-dejavu-core fonts-droid ghostscript gsfonts hicolor-icon-theme \
libavahi-client3 libavahi-common-data libavahi-common3 libcairo2 libcap-ng0 libcroco3 \
libcups2 libcupsfilters1 libcupsimage2 libdatrie1 libdbus-1-3 libdjvulibre-text libdjvulibre21 libfftw3-double3 libfontconfig1 \
libfreetype6 libgdk-pixbuf2.0-0 libgdk-pixbuf2.0-common libgomp1 libgraphite2-3 libgs9 libgs9-common libharfbuzz0b libijs-0.35 \
libilmbase6 libjasper1 libjbig0 libjbig2dec0 libjpeg62-turbo liblcms2-2 liblqr-1-0 libltdl7 libmagickcore-6.q16-2 \
libmagickcore-6.q16-2-extra libmagickwand-6.q16-2 libnetpbm10 libopenexr6 libpango-1.0-0 libpangocairo-1.0-0 libpangoft2-1.0-0 \
libpaper-utils libpaper1 libpixman-1-0 libpng12-0 librsvg2-2 librsvg2-common libthai-data libthai0 libtiff5 libwmf0.2-7 \
libxcb-render0 libxcb-shm0 netpbm poppler-data p7zip-full && \
    cd /usr/local/src && \
    wget http://transloadit.imagemagick.org/download/ImageMagick.tar.gz && \
    tar xzf ImageMagick.tar.gz && cd `ls -d ImageMagick-*` && pwd && ls -al && ./configure && \
    make -j $(nproc) && make install && \
    # clean up ImageMagick source files
    cd ../ && rm -rf ImageMagick* 

RUN pip install opencv-python

# Tensorflow source build
ENV TF_NEED_CUDA=1
ENV TF_CUDA_VERSION=9.1
# Precompile for Tesla k80 and p100.  See https://developer.nvidia.com/cuda-gpus.
ENV TF_CUDA_COMPUTE_CAPABILITIES=3.7,6.0
ENV TF_CUDNN_VERSION=7
RUN apt-get update && \
    apt-get install -y python-software-properties zip && \
    echo "deb http://ppa.launchpad.net/webupd8team/java/ubuntu precise main" | tee -a /etc/apt/sources.list && \
    echo "deb-src http://ppa.launchpad.net/webupd8team/java/ubuntu precise main" | tee -a /etc/apt/sources.list && \
    apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys EEA14886 C857C906 2B90D010 && \
    apt-get update && \
    echo debconf shared/accepted-oracle-license-v1-1 select true | debconf-set-selections && \
    echo debconf shared/accepted-oracle-license-v1-1 seen true | debconf-set-selections && \
    apt-get install -y oracle-java8-installer && \
    echo "deb [arch=amd64] http://storage.googleapis.com/bazel-apt stable jdk1.8" | tee /etc/apt/sources.list.d/bazel.list && \
    curl https://bazel.build/bazel-release.pub.gpg | apt-key add - && \
    apt-get update && apt-get install -y bazel && \
    apt-get upgrade -y bazel
RUN cd /usr/local/src && git clone https://github.com/tensorflow/tensorflow && \
    cd tensorflow && cat /dev/null | ./configure && \
    echo "/usr/local/cuda-${TF_CUDA_VERSION}/targets/x86_64-linux/lib/stubs" > /etc/ld.so.conf.d/cuda-stubs.conf && ldconfig && \
    bazel build --config=opt \
                --config=cuda \
                --cxxopt="-D_GLIBCXX_USE_CXX11_ABI=0" \
                //tensorflow/tools/pip_package:build_pip_package && \
    rm /etc/ld.so.conf.d/cuda-stubs.conf && ldconfig && \
    bazel-bin/tensorflow/tools/pip_package/build_pip_package /tmp/tensorflow_pkg && \
    pip install /tmp/tensorflow_pkg/tensorflow*.whl && \
    rm -Rf /tmp/tensorflow_pkg && \
    rm -Rf /root/.cache/bazel

RUN apt-get install -y libfreetype6-dev && \
    apt-get install -y libglib2.0-0 libxext6 libsm6 libxrender1 libfontconfig1 --fix-missing && \
    # textblob
    pip install textblob && \
    #word cloud
    pip install wordcloud && \
    #igraph
    conda install -y -c conda-forge python-igraph && \
    #xgboost
    cd /usr/local/src && mkdir xgboost && cd xgboost && \
    git clone --depth 1 --recursive https://github.com/dmlc/xgboost.git && cd xgboost && \
    make && cd python-package && python setup.py install && \
    pip install lightgbm && \
    #lasagne
    cd /usr/local/src && mkdir Lasagne && cd Lasagne && \
    git clone --depth 1 https://github.com/Lasagne/Lasagne.git && cd Lasagne && \
    pip install -r requirements.txt && python setup.py install && \
    #keras
    cd /usr/local/src && mkdir keras && cd keras && \
    git clone --depth 1 https://github.com/fchollet/keras.git && \
    cd keras && python setup.py install && \
    #keras-rl
    cd /usr/local/src && mkdir keras-rl && cd keras-rl && \
    git clone --depth 1 https://github.com/matthiasplappert/keras-rl.git && \
    cd keras-rl && python setup.py install && \
    #keras-rcnn
    pip install git+https://github.com/broadinstitute/keras-rcnn && \
    #neon
    cd /usr/local/src && \
    git clone --depth 1 https://github.com/NervanaSystems/neon.git && \
    cd neon && pip install -e . && \
    #nolearn
    cd /usr/local/src && mkdir nolearn && cd nolearn && \
    git clone --depth 1 https://github.com/dnouri/nolearn.git && cd nolearn && \
    echo "x" > README.rst && echo "x" > CHANGES.rst && \
    python setup.py install && \
    # Dev branch of Theano
    pip install git+git://github.com/Theano/Theano.git --upgrade --no-deps && \
    # put theano compiledir inside /tmp (it needs to be in writable dir)
    printf "[global]\nbase_compiledir = /tmp/.theano\n" > /.theanorc && \
    cd /usr/local/src &&  git clone --depth 1 https://github.com/pybrain/pybrain && \
    cd pybrain && python setup.py install && \
    # Base ATLAS
    apt-get install -y libatlas-base-dev && \
    cd /usr/local/src && git clone --depth 1 https://github.com/ztane/python-Levenshtein && \
    cd python-Levenshtein && python setup.py install && \
    cd /usr/local/src && git clone --depth 1 https://github.com/arogozhnikov/hep_ml.git && \
    cd hep_ml && pip install .  && \
    # chainer
    pip install chainer && \
    # NLTK Project datasets
    mkdir -p /usr/share/nltk_data && \
    # NLTK Downloader no longer continues smoothly after an error, so we explicitly list
    # the corpuses that work
    python -m nltk.downloader -d /usr/share/nltk_data abc alpino averaged_perceptron_tagger \
    basque_grammars biocreative_ppi bllip_wsj_no_aux \
book_grammars brown brown_tei cess_cat cess_esp chat80 city_database cmudict \
comtrans conll2000 conll2002 conll2007 crubadan dependency_treebank \
europarl_raw floresta gazetteers genesis gutenberg \
ieer inaugural indian jeita kimmo knbc large_grammars lin_thesaurus mac_morpho machado \
masc_tagged maxent_ne_chunker maxent_treebank_pos_tagger moses_sample movie_reviews \
mte_teip5 names nps_chat omw opinion_lexicon paradigms \
pil pl196x porter_test ppattach problem_reports product_reviews_1 product_reviews_2 propbank \
pros_cons ptb punkt qc reuters rslp rte sample_grammars semcor senseval sentence_polarity \
sentiwordnet shakespeare sinica_treebank smultron snowball_data spanish_grammars \
state_union stopwords subjectivity swadesh switchboard tagsets timit toolbox treebank \
twitter_samples udhr2 udhr unicode_samples universal_tagset universal_treebanks_v20 \
vader_lexicon verbnet webtext word2vec_sample wordnet wordnet_ic words ycoe && \
    # Stop-words
    pip install stop-words && \
    # clean up
    rm -rf /root/.cache/pip/* && \
    apt-get autoremove -y && apt-get clean && \
    rm -rf /usr/local/src/*

# Make sure the dynamic linker finds the right libstdc++
ENV LD_LIBRARY_PATH="/opt/conda/lib:${LD_LIBRARY_PATH}"

# Install Basemap via conda temporarily
RUN apt-get update && \
    #apt-get -y install libgeos-dev && \
    #pip install matplotlib && \
    #pip install pyshp && \
    #pip install pyproj && \
    #cd /usr/local/src && git clone https://github.com/matplotlib/basemap.git && \
    #cd basemap/geos-3.3.3 && \
    #export GEOS_DIR=/usr/local && \
    #./configure --prefix=$GEOS_DIR && \
    #make && make install && \
    #cd .. && python setup.py install && \
    conda install basemap && \
    # Pillow (PIL)
    apt-get -y install zlib1g-dev liblcms2-dev libwebp-dev && \
    pip install Pillow

RUN cd /usr/local/src && git clone https://github.com/vitruvianscience/opendeep.git && \
    cd opendeep && python setup.py develop  && \
    # sasl is apparently an ibis dependency
    apt-get -y install libsasl2-dev && \
    # ...as is psycopg2
    apt-get install -y libpq-dev && \
    pip install ibis-framework && \
    # Cartopy plus dependencies
    yes | conda install proj4 && \
    pip install packaging && \
    cd /usr/local/src && git clone https://github.com/Toblerity/Shapely.git && \
    cd Shapely && python setup.py install && \
    cd /usr/local/src && git clone https://github.com/SciTools/cartopy.git && \
    cd cartopy && python setup.py install && \
    # MXNet
    pip install mxnet && \
    # h2o
    # This requires python-software-properties and Java, which were installed above.
    cd /usr/local/src && mkdir h2o && cd h2o && \
    wget http://h2o-release.s3.amazonaws.com/h2o/latest_stable -O latest && \
    wget --no-check-certificate -i latest -O h2o.zip && rm latest && \
    unzip h2o.zip && rm h2o.zip && cp h2o-*/h2o.jar . && \
    pip install `find . -name "*whl"` && \
    # Work around https://github.com/tensorflow/tensorflow/issues/16488
    pip install numpy --upgrade

    # Keras setup
    # Keras likes to add a config file in a custom directory when it's
    # first imported. This doesn't work with our read-only filesystem, so we
    # have it done now.
RUN python -c "from keras.models import Sequential"  && \
    # Switch to TF backend
    sed -i 's/theano/tensorflow/' /root/.keras/keras.json  && \
    # Re-run it to flush any more disk writes
    python -c "from keras.models import Sequential; from keras import backend; print(backend._BACKEND)" && \
    # Keras reverts to /tmp from ~ when it detects a read-only file system
    mkdir -p /tmp/.keras && cp /root/.keras/keras.json /tmp/.keras && \
    # Scikit-Learn nightly build
    cd /usr/local/src && git clone https://github.com/scikit-learn/scikit-learn.git && \
    cd scikit-learn && python setup.py build && python setup.py install && \
    # HDF5 support
    conda install h5py && \
    # https://github.com/biopython/biopython
    pip install biopython && \
    # PUDB, for local debugging convenience
    pip install pudb && \
    # Imbalanced-learn
    cd /usr/local/src && git clone https://github.com/scikit-learn-contrib/imbalanced-learn.git && \
    cd imbalanced-learn && python setup.py install && \
    # Convex Optimization library
    # Latest version fails to install, see https://github.com/cvxopt/cvxopt/issues/77
    #    and https://github.com/cvxopt/cvxopt/issues/80
    # pip install cvxopt && \
    # Profiling and other utilities
    pip install line_profiler && \
    pip install orderedmultidict && \
    pip install smhasher && \
    conda install -y -c bokeh datashader && \
    # Boruta (python implementation)
    cd /usr/local/src && git clone https://github.com/danielhomola/boruta_py.git && \
    cd boruta_py && python setup.py install && \
    cd /usr/local/src && git clone git://github.com/nicolashennetier/pyeconometrics.git && \
    cd pyeconometrics && python setup.py install && \
    apt-get install -y graphviz && pip install graphviz && \
    apt-get install -y libgdal1-dev && GDAL_CONFIG=/usr/bin/gdal-config pip install fiona && pip install geopandas && \
    # Pandoc is a dependency of deap
    apt-get install -y pandoc && \
    cd /usr/local/src && git clone git://github.com/scikit-learn-contrib/py-earth.git && \
    cd py-earth && python setup.py install
    #cd /usr/local/src && git clone https://github.com/MTG/essentia.git && cd essentia && \
    #./waf configure --mode=release --build-static --with-python --with-cpptests --with-examples --with-vamp && \
    #./waf && ./waf install && mv /usr/local/lib/python3.6/site-packages/essentia /opt/conda/lib/python3.6
   
    # Install torch and torchvision from source, so we're using the cuda/cudnn libraries installed above.
RUN export CXXFLAGS="-std=c++11" && \
    export CFLAGS="-std=c99" && \
    conda install mkl mkl-include setuptools cmake cffi typing && \
    conda install -c pytorch magma-cuda90 && \
    cd /usr/local/src && \
    git clone -b v0.4.0 --recursive https://github.com/pytorch/pytorch && \
    cd pytorch && \
    python setup.py install && \
    cd /usr/local/src && \
    git clone -b v0.2.1 --recursive https://github.com/pytorch/vision && \
    cd vision && \
    python setup.py install && \
    # PyTorch Audio
    apt-get install -y sox libsox-dev libsox-fmt-all && \
    pip install cffi && \
    cd /usr/local/src && \
    git clone https://github.com/pytorch/audio && \
    cd audio && \
    python setup.py install && \
    # ggpy / ggplot
    pip install git+https://github.com/yhat/ggplot.git && \
    # Basic cuda support library for python.
    pip install pycuda && \
    # ~~~~ CLEAN UP ~~~~
    rm -rf /root/.cache/pip/* && \
    apt-get autoremove -y && apt-get clean && \
    conda clean -i -l -t -y && \
    rm -rf /usr/local/src/*

RUN pip install --upgrade mpld3 && \
    pip install mplleaflet && \
    pip install gpxpy && \
    pip install arrow && \
    pip install vtk && \
    pip install nilearn && \
    pip install nibabel && \
    pip install pronouncing && \
    pip install markovify && \
    pip install rf_perm_feat_import && \
    pip install imgaug && \
    pip install preprocessing && \
    pip install Baker && \
    pip install path.py && \
    pip install Geohash && \
    # https://github.com/vinsci/geohash/issues/4
    sed -i -- 's/geohash/.geohash/g' /opt/conda/lib/python3.6/site-packages/Geohash/__init__.py && \
    pip install deap && \
    pip install tpot && \
    pip install scikit-optimize && \
    pip install haversine && \
    pip install toolz cytoolz && \
    pip install sacred && \
    pip install plotly && \
    pip install git+https://github.com/nicta/dora.git && \
    pip install git+https://github.com/hyperopt/hyperopt.git && \
    # tflean. Deep learning library featuring a higher-level API for TensorFlow. http://tflearn.org
    pip install git+https://github.com/tflearn/tflearn.git && \
    pip install fitter && \
    pip install langid && \
    # Delorean. Useful for dealing with datetime
    pip install delorean && \
    pip install trueskill && \
    pip install heamy && \
    pip install vida && \
    # Useful data exploration libraries (for missing data and generating reports)
    pip install missingno && \
    pip install pandas-profiling && \
    pip install s2sphere && \
    pip install git+https://github.com/fmfn/BayesianOptimization.git && \
    pip install matplotlib-venn && \
    pip install pyldavis && \
    # Pattern not yet Py3 compatible...
    # pip install pattern && \
    pip install git+git://github.com/rasbt/mlxtend.git#egg=mlxtend && \
    pip install altair && \
    pip install pystan && \
    pip install ImageHash && \
    conda install -y ecos && \
    conda install -y CVXcanon && \
    pip install fancyimpute && \
    pip install git+https://github.com/pymc-devs/pymc3 && \
    pip install tifffile && \
    pip install spectral && \
    pip install descartes && \
    pip install geojson && \
    pip install pysal && \
    #conda install -y gdal && \
    pip install pyflux && \
    pip install terminalplot && \
    pip install raccoon && \
    pip install pydicom && \
    pip install wavio && \
    pip install SimpleITK && \
    pip install hmmlearn && \
    pip install bayespy && \
    pip install gplearn && \
    pip install PyAstronomy && \
    pip install squarify && \
    pip install fuzzywuzzy && \
    pip install python-louvain && \
    pip install pyexcel-ods && \
    pip install sklearn-pandas && \
    pip install stemming && \
    conda install -y -c conda-forge fbprophet && \
    conda install -y -c conda-forge -c ioam holoviews geoviews && \
    pip install hypertools && \
    # Nxviz has been causing an installation issue by trying unsuccessfully to remove setuptools.
    #pip install nxviz && \
    pip install py_stringsimjoin && \
    pip install speedml && \
    pip install nibabel && \
    pip install mlens && \
    pip install scikit-multilearn && \
    pip install -e git+http://github.com/tensorflow/cleverhans.git#egg=cleverhans && \
    pip install leven && \
    pip install catboost && \
    #cd /usr/local/src && git clone --depth=1 https://github.com/AxeldeRomblay/MLBox && cd MLBox/python-package && python setup.py install && \
    pip install fastFM && \
    pip install lightfm && \
    pip install paramnb && \
    pip install folium && \
    pip install scikit-plot && \
    pip install dipy && \
    pip install plotnine && \
    pip install git+https://github.com/dvaida/hallucinate.git && \
    pip install scikit-surprise && \
    pip install pymongo && \
    pip install edward && \
    pip install geoplot && \
    pip install eli5 && \
    pip install implicit && \
    pip install dask-ml[xgboost]

RUN pip install kmeans-smote --no-dependencies && \
    # Add google PAIR-code Facets
    cd /opt/ && git clone https://github.com/PAIR-code/facets && cd facets/ && jupyter nbextension install facets-dist/ --user && \
    export PYTHONPATH=$PYTHONPATH:/opt/facets/facets_overview/python/ && \
    pip install --no-dependencies ethnicolr && \
    # Update setuptools and add tensorpack
    pip install --upgrade --ignore-installed setuptools && pip install --no-cache-dir git+git://github.com/ppwwyyxx/tensorpack && \
    pip install pycountry && pip install iso3166 && \
    pip install pydash && \
    pip install kmodes --no-dependencies && \
    pip install librosa && \
    pip install polyglot && \
    pip install mmh3 && \
    pip install fbpca && \
    pip install sentencepiece && \
    pip install cufflinks && \
    pip install glmnet_py && \
    pip install lime && \
    pip install memory_profiler

# Install cython & cysignals before pyfasttext
RUN pip install --upgrade cython && \
    pip install --upgrade cysignals && \
    pip install pyfasttext && \
    pip install ktext && \
    cd /usr/local/src && git clone --depth=1 https://github.com/facebookresearch/fastText.git && cd fastText && pip install . && \
    apt-get install -y libhunspell-dev && pip install hunspell && \
    pip install annoy && \
    pip install category_encoders && \
    pip install google-cloud-bigquery && \
    pip install ortools && \
    pip install scattertext && \
    # Pandas data reader
    pip install pandas-datareader && \
    pip install pykoko && \
    pip install wordsegment && \
    pip install pyahocorasick && \
    pip install wordbatch && \
    pip install emoji && \
    # Add Japanese morphological analysis engine
    pip install janome && \
    pip install wfdb && \
    pip install vecstack && \
    pip install sklearn-contrib-lightning && \
    # yellowbrick machine learning visualization library
    pip install yellowbrick && \
    pip install mlcrate && \
    pip install gym && \
    pip install ray && \
    # Required to display Altair charts in Jupyter notebook
    pip install vega3 && \
    jupyter nbextension install --sys-prefix --py vega3  && \
    # clean up pip cache
    rm -rf /root/.cache/pip/*

# Fast.ai and dependencies
RUN pip install bcolz && \
    pip install bleach && \
    pip install certifi && \
    pip install cycler && \
    pip install decorator && \
    pip install entrypoints && \
    pip install html5lib && \
    pip install ipykernel && \
    pip install ipython && \
    pip install ipython-genutils && \
    pip install ipywidgets && \
    pip install isoweek && \
    pip install jedi && \
    pip install Jinja2 && \
    pip install jsonschema && \
    pip install jupyter && \
    pip install jupyter-client && \
    pip install jupyter-console && \
    pip install jupyter-core && \
    pip install MarkupSafe && \
    pip install matplotlib && \
    pip install mistune && \
    pip install nbconvert && \
    pip install nbformat && \
    pip install notebook && \
    pip install numpy && \
    pip install olefile && \
    pip install opencv-python && \
    pip install --upgrade pandas && \
    pip install pandas_summary && \
    pip install pandocfilters && \
    pip install pexpect && \
    pip install pickleshare && \
    pip install Pillow && \
    pip install prompt-toolkit && \
    pip install ptyprocess && \
    pip install Pygments && \
    pip install pyparsing && \
    pip install python-dateutil==2.6.0 && \
    pip install pytz && \
    pip install PyYAML && \
    pip install pyzmq && \
    pip install qtconsole && \
    pip install scipy && \
    pip install seaborn && \
    pip install simplegeneric && \
    pip install six && \
    pip install terminado && \
    pip install testpath && \
    pip install tornado && \
    pip install tqdm && \
    pip install traitlets && \
    pip install wcwidth && \
    pip install webencodings && \
    pip install widgetsnbextension && \
    cd /usr/local/src && git clone --depth=1 https://github.com/fastai/fastai && \
    cd fastai && python setup.py install && \
    # clean up pip cache
    rm -rf /root/.cache/pip/* && \
    cd && rm -rf /usr/local/src/*

    ###########
    #
    #      NEW CONTRIBUTORS:
    # Please add new pip/apt installs in this block. Don't forget a "&& \" at the end
    # of all non-final lines. Thanks!
    #
    ###########
RUN pip install flashtext && \
    pip install marisa-trie && \
    pip install pyemd && \
    pip install pyupset && \
    pip install -e git+https://github.com/SohierDane/BigQuery_Helper#egg=bq_helper && \
    pip install git+https://github.com/Kaggle/learntools && \
    ##### ^^^^ Add new contributions above here
    # clean up pip cache
    rm -rf /root/.cache/pip/*


# For Facets
ENV PYTHONPATH=$PYTHONPATH:/opt/facets/facets_overview/python/
# For Theano with MKL
ENV MKL_THREADING_LAYER=GNU

# Temporary fixes and patches:
# Temporary patch for Dask getting downgraded, which breaks Keras
RUN pip install --upgrade dask && \
    # Stop jupyter nbconvert trying to rewrite its folder hierarchy
    mkdir -p /root/.jupyter && touch /root/.jupyter/jupyter_nbconvert_config.py && touch /root/.jupyter/migrated && \
    mkdir -p /.jupyter && touch /.jupyter/jupyter_nbconvert_config.py && touch /.jupyter/migrated && \
    # Stop Matplotlib printing junk to the console on first load
    sed -i "s/^.*Matplotlib is building the font cache using fc-list.*$/# Warning removed by Kaggle/g" /opt/conda/lib/python3.6/site-packages/matplotlib/font_manager.py && \
    # Make matplotlib output in Jupyter notebooks display correctly
    mkdir -p /etc/ipython/ && echo "c = get_config(); c.IPKernelApp.matplotlib = 'inline'" > /etc/ipython/ipython_config.py

# Add BigQuery client proxy settings
ENV PYTHONUSERBASE "/root/.local"
ADD patches/sitecustomize.py /root/.local/lib/python3.6/site-packages/sitecustomize.py

# Set backend for matplotlib
ENV MPLBACKEND "agg"

# Customize nbconvert.
ADD patches/nbconvert-extensions.tpl /opt/kaggle/nbconvert-extensions.tpl
