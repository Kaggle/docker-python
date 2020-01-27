ARG BASE_TAG=2019.03
ARG TENSORFLOW_VERSION=2.1.0

FROM gcr.io/kaggle-images/python-tensorflow-whl:${TENSORFLOW_VERSION}-py36 as tensorflow_whl
FROM continuumio/anaconda3:${BASE_TAG}

ADD clean-layer.sh  /tmp/clean-layer.sh
ADD patches/nbconvert-extensions.tpl /opt/kaggle/nbconvert-extensions.tpl

# This is necessary for apt to access HTTPS sources
RUN apt-get update && \
    apt-get install apt-transport-https && \
    /tmp/clean-layer.sh

    # Use a fixed apt-get repo to stop intermittent failures due to flaky httpredir connections,
    # as described by Lionel Chan at http://stackoverflow.com/a/37426929/5881346
RUN sed -i "s/httpredir.debian.org/debian.uchicago.edu/" /etc/apt/sources.list && \
    apt-get update && apt-get install -y build-essential unzip cmake && \
    # Work to upgrade to Python 3.7 can be found on this branch: https://github.com/Kaggle/docker-python/blob/upgrade-py37/Dockerfile
    conda install -y python=3.6.6 && \
    # See b/148097039#comment7
    pip install pip==19.3.1 && \
    /tmp/clean-layer.sh

# The anaconda base image includes outdated versions of these packages. Update them to include the latest version.
RUN pip install seaborn python-dateutil dask && \
    pip install pyyaml joblib pytagcloud husl geopy ml_metrics mne pyshp && \
    pip install spacy && python -m spacy download en && python -m spacy download en_core_web_lg && \
    # The apt-get version of imagemagick is out of date and has compatibility issues, so we build from source
    apt-get -y install dbus fontconfig fontconfig-config fonts-dejavu-core fonts-droid-fallback ghostscript gsfonts hicolor-icon-theme \
    libavahi-client3 libavahi-common-data libavahi-common3 libcairo2 libcap-ng0 libcroco3 \
    libcups2 libcupsfilters1 libcupsimage2 libdatrie1 libdbus-1-3 libdjvulibre-text libdjvulibre21 libfftw3-double3 libfontconfig1 \
    libfreetype6 libgdk-pixbuf2.0-0 libgdk-pixbuf2.0-common libgomp1 libgraphite2-3 libgs9 libgs9-common libharfbuzz0b libijs-0.35 \
    libilmbase12 libjbig0 libjbig2dec0 libjpeg62-turbo liblcms2-2 liblqr-1-0 libltdl7 libmagickcore-6.q16-3 \
    libmagickcore-6.q16-3-extra libmagickwand-6.q16-3 libnetpbm10 libopenexr22 libpango-1.0-0 libpangocairo-1.0-0 libpangoft2-1.0-0 \
    libpaper-utils libpaper1 libpixman-1-0 libpng16-16 librsvg2-2 librsvg2-common libthai-data libthai0 libtiff5 libwmf0.2-7 \
    libxcb-render0 libxcb-shm0 netpbm poppler-data p7zip-full python3-rtree && \
    cd /usr/local/src && \
    # b/141476846 latest ImageMagick version fails to build.
    wget --no-verbose https://github.com/ImageMagick/ImageMagick/archive/7.0.8-65.tar.gz && \
    tar xzf 7.0.8-65.tar.gz && cd `ls -d ImageMagick-*` && pwd && ls -al && ./configure && \
    make -j $(nproc) && make install && \
    /tmp/clean-layer.sh

# Install tensorflow from a pre-built wheel
COPY --from=tensorflow_whl /tmp/tensorflow_cpu/*.whl /tmp/tensorflow_cpu/
RUN pip install /tmp/tensorflow_cpu/tensorflow*.whl && \
    rm -rf /tmp/tensorflow_cpu && \
    /tmp/clean-layer.sh

RUN apt-get install -y libfreetype6-dev && \
    apt-get install -y libglib2.0-0 libxext6 libsm6 libxrender1 libfontconfig1 --fix-missing && \
    pip install gensim && \
    pip install textblob && \
    pip install wordcloud && \
    conda install -y -c conda-forge python-igraph && \
    pip install xgboost && \
    pip install lightgbm && \
    pip install git+git://github.com/Lasagne/Lasagne.git && \
    pip install keras && \
    pip install keras-rl && \
    #keras-rcnn
    pip install git+https://github.com/broadinstitute/keras-rcnn && \
    # version 3.7.1 adds a dependency on entrypoints > 3. This causes a reinstall but fails because
    # it is a distutils package and can't be uninstalled. Once the anaconda image in updated, this
    # pin should be removed.
    pip install flake8==3.6.0 && \
    #neon
    cd /usr/local/src && \
    git clone --depth 1 https://github.com/NervanaSystems/neon.git && \
    cd neon && pip install . && \
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
    pip install hep_ml && \
    # chainer
    pip install chainer && \
    # NLTK Project datasets
    mkdir -p /usr/share/nltk_data && \
    # NLTK Downloader no longer continues smoothly after an error, so we explicitly list
    # the corpuses that work
    # "yes | ..." answers yes to the retry prompt in case of an error. See b/133762095.
    yes | python -m nltk.downloader -d /usr/share/nltk_data abc alpino averaged_perceptron_tagger \
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
    pip install --upgrade scikit-image && \
    /tmp/clean-layer.sh

# Make sure the dynamic linker finds the right libstdc++
ENV LD_LIBRARY_PATH=/opt/conda/lib

RUN apt-get -y install zlib1g-dev liblcms2-dev libwebp-dev libgeos-dev && \
    pip install matplotlib && \
    pip install pyshp && \
    # b/144569992 pyproj 2.4.1 is failing to install because of missing METADATA file.
    pip install pyproj==2.4.0 && \
    conda install basemap && \
    # sasl is apparently an ibis dependency
    apt-get -y install libsasl2-dev && \
    # ...as is psycopg2
    apt-get install -y libpq-dev && \
    pip install ibis-framework && \
    # Cartopy plus dependencies
    yes | conda install proj4 && \
    pip install packaging && \
    pip install shapely && \
    pip install cartopy && \
    pip install mxnet && \
    # b/145358669 remove --upgrade once we upgrade base image which will include numpy >= 1.17
    pip install --upgrade numpy && \
    pip install gluonnlp && \
    pip install gluoncv && \
    # h2o (requires java)
    # requires java
    apt-get install -y default-jdk && \
    cd /usr/local/src && mkdir h2o && cd h2o && \
    wget --no-verbose http://h2o-release.s3.amazonaws.com/h2o/latest_stable -O latest && \
    wget --no-verbose --no-check-certificate -i latest -O h2o.zip && rm latest && \
    unzip h2o.zip && rm h2o.zip && cp h2o-*/h2o.jar . && \
    pip install `find . -name "*whl"` && \
    /tmp/clean-layer.sh

# b/128333086: Set PROJ_LIB to points to the proj4 cartographic library.
ENV PROJ_LIB=/opt/conda/share/proj

# scikit-learn dependencies
RUN pip install scipy && \
    pip install scikit-learn && \
    # HDF5 support
    pip install h5py && \
    pip install biopython && \
    # PUDB, for local debugging convenience
    pip install pudb && \
    pip install imbalanced-learn && \
    # Convex Optimization library
    # Latest version fails to install, see https://github.com/cvxopt/cvxopt/issues/77
    #    and https://github.com/cvxopt/cvxopt/issues/80
    # pip install cvxopt && \
    # Profiling and other utilities
    pip install line_profiler && \
    pip install orderedmultidict && \
    pip install smhasher && \
    pip install bokeh && \
    pip install numba && \
    pip install datashader && \
    # Boruta (python implementation)
    pip install Boruta && \
    cd /usr/local/src && git clone git://github.com/nicolashennetier/pyeconometrics.git && \
    cd pyeconometrics && python setup.py install && \
    apt-get install -y graphviz && pip install graphviz && \
    # Pandoc is a dependency of deap
    apt-get install -y pandoc && \
    pip install git+git://github.com/scikit-learn-contrib/py-earth.git@issue191 && \
    pip install essentia && \
    conda install -y pytorch torchvision torchaudio cpuonly -c pytorch && \
    /tmp/clean-layer.sh

# vtk with dependencies
RUN apt-get install -y libgl1-mesa-glx && \
    pip install vtk && \
    # xvfbwrapper with dependencies
    apt-get install -y xvfb && \
    pip install xvfbwrapper && \
    /tmp/clean-layer.sh

RUN pip install mpld3 && \
    pip install mplleaflet && \
    pip install gpxpy && \
    pip install arrow && \
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
    pip install mlxtend && \
    pip install altair && \
    pip install pystan && \
    pip install ImageHash && \
    pip install ecos && \
    pip install CVXcanon && \
    pip install fancyimpute && \
    pip install git+https://github.com/pymc-devs/pymc3 && \
    pip install tifffile && \
    pip install spectral && \
    pip install descartes && \
    pip install geojson && \
    pip install pysal && \
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
    # b/148383434 remove pip install for holidays once fbprophet is compatible with latest version of holidays.
    pip install holidays==0.9.12 && \
    pip install fbprophet && \
    pip install holoviews && \
    # 1.6.2 is not currently supported by the version of matplotlib we are using.
    # See other comments about why matplotlib is pinned.
    pip install geoviews==1.6.1 && \
    pip install hypertools && \
    pip install py_stringsimjoin && \
    pip install speedml && \
    pip install nibabel && \
    pip install mlens && \
    pip install scikit-multilearn && \
    pip install cleverhans && \
    pip install leven && \
    pip install catboost && \
    #cd /usr/local/src && git clone --depth=1 https://github.com/AxeldeRomblay/MLBox && cd MLBox/python-package && python setup.py install && \
    pip install fastFM && \
    pip install lightfm && \
    pip install paramnb && \
    pip install folium && \
    pip install scikit-plot && \
    # dipy requires the optional fury dependency for visualizations.
    pip install fury dipy && \
    # plotnine 0.5 is depending on matplotlib >= 3.0 which is not compatible with basemap.
    # once basemap support matplotlib, we can unpin this package.
    pip install plotnine==0.4.0 && \
    pip install git+https://github.com/dvaida/hallucinate.git && \
    pip install scikit-surprise && \
    pip install pymongo && \
    pip install edward && \
    pip install geoplot && \
    pip install eli5 && \
    pip install implicit && \
    pip install dask-ml[xgboost] && \
    /tmp/clean-layer.sh

RUN pip install kmeans-smote --no-dependencies && \
    # Add google PAIR-code Facets
    cd /opt/ && git clone https://github.com/PAIR-code/facets && cd facets/ && jupyter nbextension install facets-dist/ --user && \
    export PYTHONPATH=$PYTHONPATH:/opt/facets/facets_overview/python/ && \
    pip install tensorpack && \
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
    pip install memory_profiler && \
    /tmp/clean-layer.sh

# install cython & cysignals before pyfasttext
RUN pip install --upgrade cython && \
    pip install --upgrade cysignals && \
    pip install pyfasttext && \
    # ktext has an explicit dependency on Keras 2.2.4 which is not
    # compatible with TensorFlow 2.0 (support was added in Keras 2.3.0).
    # Add the package back once it is fixed upstream.
    # pip install ktext && \
    pip install fasttext && \
    apt-get install -y libhunspell-dev && pip install hunspell && \
    pip install annoy && \
    # Need to use CountEncoder from category_encoders before it's officially released
    pip install git+https://github.com/scikit-learn-contrib/categorical-encoding.git && \
    pip install google-cloud-automl && \
    # Newer version crashes (latest = 1.14.0) when running tensorflow.
    # python -c "from google.cloud import bigquery; import tensorflow". This flow is common because bigquery is imported in kaggle_gcp.py
    # which is loaded at startup.
    pip install google-cloud-bigquery==1.12.1 && \
    pip install google-cloud-storage && \
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
    # Required to display Altair charts in Jupyter notebook
    pip install vega3 && \
    jupyter nbextension install --sys-prefix --py vega3 && \
    /tmp/clean-layer.sh

# Fast.ai and dependencies
RUN pip install bcolz && \
    pip install bleach && \
    pip install certifi && \
    pip install cycler && \
    pip install decorator && \
    pip install entrypoints && \
    pip install html5lib && \
    # Latest version breaks nbconvert: https://github.com/ipython/ipykernel/issues/422
    pip install ipykernel==5.1.1 && \
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
    pip install mistune && \
    pip install nbconvert && \
    pip install nbformat && \
    pip install notebook==5.5.0 && \
    pip install olefile && \
    pip install opencv-python && \
    # tsfresh doesn't work with pandas 0.24, requires >= 0.25: https://github.com/blue-yonder/tsfresh/blob/0ef9123d68e3544ef0217caf83f63f93ad837a61/requirements.txt#L3
    # b/145358669 remove --upgrade once we upgrade base image which will include pandas >= 0.25 
    pip install --upgrade pandas && \
    pip install pandas_summary && \
    pip install pandocfilters && \
    pip install pexpect && \
    pip install pickleshare && \
    pip install Pillow && \
    pip install ptyprocess && \
    pip install Pygments && \
    pip install pyparsing && \
    pip install pytz && \
    pip install PyYAML && \
    pip install pyzmq && \
    pip install qtconsole && \
    pip install simplegeneric && \
    pip install six && \
    pip install terminado && \
    pip install testpath && \
    # Latest version (6.0) of tornado breaks Jupyter notebook:
    # https://github.com/jupyter/notebook/issues/4439
    pip install tornado==5.0.2 && \
    pip install tqdm && \
    pip install traitlets && \
    pip install wcwidth && \
    pip install webencodings && \
    pip install widgetsnbextension && \
    pip install pyarrow && \
    pip install feather-format && \
    pip install fastai && \
    pip install torchtext && \
    /tmp/clean-layer.sh

# allennlp and dependencies
# TODO: install deps when underlying dependency is fixed. https://github.com/Kaggle/docker-python/issues/548
RUN pip install jsonnet overrides tensorboardX && \
    pip install flask>=1.0.2 flask-cors>=3.0.7 gevent>=1.3.6 && \
    pip install unidecode parsimonious>=0.8.0 sqlparse>=0.2.4 word2number>=1.1 && \
    pip install pytorch-pretrained-bert>=0.6.0 pytorch-transformers==1.1.0 jsonpickle && \
    pip install requests>=2.18 editdistance conllu==0.11 && \
    pip install conllu==1.3.1 ftfy && \
    pip install --no-dependencies allennlp && \
    /tmp/clean-layer.sh

    ###########
    #
    #      NEW CONTRIBUTORS:
    # Please add new pip/apt installs in this block. Don't forget a "&& \" at the end
    # of all non-final lines. Thanks!
    #
    ###########

RUN pip install flashtext && \
    pip install wandb && \
    pip install marisa-trie && \
    pip install pyemd && \
    pip install pyupset && \
    pip install pympler && \
    pip install s3fs && \
    pip install featuretools && \
    pip install -e git+https://github.com/SohierDane/BigQuery_Helper#egg=bq_helper && \
    pip install hpsklearn && \
    pip install keras-tqdm && \
    pip install git+https://github.com/Kaggle/learntools && \
    pip install kmapper && \
    pip install shap && \
    pip install ray && \
    pip install gym && \
    pip install tensorforce && \
    pip install pyarabic && \
    pip install conx && \
    pip install pandasql && \
    pip install trackml && \
    pip install tensorflow_hub && \
    pip install jieba  && \
    pip install git+https://github.com/SauceCat/PDPbox && \
    pip install ggplot && \
    # b/145856222 cesium 0.9.10 forces a downgrade of scikit-learn.
    pip install cesium==0.9.9 && \
    pip install rgf_python && \
    # b/145404107: latest version force specific version of numpy and torch.
    pip install pytext-nlp==0.1.2 && \
    pip install pytext-nlp && \
    pip install tsfresh && \
    pip install pymagnitude && \
    pip install pykalman && \
    pip install optuna && \
    pip install chainercv && \
    pip install chainer-chemistry && \
    pip install plotly_express && \
    pip install albumentations && \
    pip install catalyst && \
    # b/145133331: latest version is causing issue with gcloud.
    pip install rtree==0.8.3 && \
    # b/145133331 osmnx 0.11 requires rtree >= 0.9 which is causing issue with gcloud.
    pip install osmnx==0.10 && \
    apt-get -y install libspatialindex-dev && \
    pip install pytorch-ignite && \
    pip install qgrid && \
    pip install bqplot && \
    pip install earthengine-api && \
    pip install transformers && \
    pip install kaggle-environments && \
    /tmp/clean-layer.sh

# Tesseract and some associated utility packages
RUN apt-get install tesseract-ocr -y && \
    pip install pytesseract && \
    pip install wand==0.5.3 && \
    pip install pdf2image && \
    pip install PyPDF && \
    pip install pyocr && \
    /tmp/clean-layer.sh
ENV TESSERACT_PATH=/usr/bin/tesseract

# Pin Vowpal Wabbit v8.6.0 because 8.6.1 does not build or install successfully
RUN cd /usr/local/src && \
    git clone -b 8.6.0 https://github.com/JohnLangford/vowpal_wabbit.git && \
    ./vowpal_wabbit/python/conda_install.sh && \
    # Reinstall in non-editable mode (without the -e flag)
    pip install vowpal_wabbit/python && \
    /tmp/clean-layer.sh

# For Facets
ENV PYTHONPATH=$PYTHONPATH:/opt/facets/facets_overview/python/
# For Theano with MKL
ENV MKL_THREADING_LAYER=GNU

# Temporary fixes and patches
    # Temporary patch for Dask getting downgraded, which breaks Keras
RUN pip install --upgrade dask && \
    # Stop jupyter nbconvert trying to rewrite its folder hierarchy
    mkdir -p /root/.jupyter && touch /root/.jupyter/jupyter_nbconvert_config.py && touch /root/.jupyter/migrated && \
    mkdir -p /.jupyter && touch /.jupyter/jupyter_nbconvert_config.py && touch /.jupyter/migrated && \
    # Stop Matplotlib printing junk to the console on first load
    sed -i "s/^.*Matplotlib is building the font cache using fc-list.*$/# Warning removed by Kaggle/g" /opt/conda/lib/python3.6/site-packages/matplotlib/font_manager.py && \
    # Make matplotlib output in Jupyter notebooks display correctly
    mkdir -p /etc/ipython/ && echo "c = get_config(); c.IPKernelApp.matplotlib = 'inline'" > /etc/ipython/ipython_config.py && \
    /tmp/clean-layer.sh

# gcloud SDK https://cloud.google.com/sdk/docs/quickstart-debian-ubuntu
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" \
    | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | \
    apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - && \
    apt-get update -y && apt-get install google-cloud-sdk -y && \
    /tmp/clean-layer.sh

# Add BigQuery client proxy settings
ENV PYTHONUSERBASE "/root/.local"
ADD patches/kaggle_gcp.py /root/.local/lib/python3.6/site-packages/kaggle_gcp.py
ADD patches/kaggle_secrets.py /root/.local/lib/python3.6/site-packages/kaggle_secrets.py
ADD patches/kaggle_web_client.py /root/.local/lib/python3.6/site-packages/kaggle_web_client.py
ADD patches/kaggle_datasets.py /root/.local/lib/python3.6/site-packages/kaggle_datasets.py
ADD patches/log.py /root/.local/lib/python3.6/site-packages/log.py
ADD patches/sitecustomize.py /root/.local/lib/python3.6/site-packages/sitecustomize.py

# TensorBoard Jupyter extension. Should be replaced with TensorBoard's provided magic once we have
# worker tunneling support in place.
# b/139212522 re-enable TensorBoard once solution for slowdown is implemented.
# ENV JUPYTER_CONFIG_DIR "/root/.jupyter/"
# RUN pip install jupyter_tensorboard && \
#     jupyter serverextension enable jupyter_tensorboard && \
#     jupyter tensorboard enable
# ADD patches/tensorboard/notebook.py /opt/conda/lib/python3.6/site-packages/tensorboard/notebook.py

# Set backend for matplotlib
ENV MPLBACKEND "agg"

# We need to redefine TENSORFLOW_VERSION here to get the default ARG value defined above the FROM instruction.
# See: https://docs.docker.com/engine/reference/builder/#understand-how-arg-and-from-interact
ARG TENSORFLOW_VERSION
ARG GIT_COMMIT=unknown
ARG BUILD_DATE=unknown

LABEL git-commit=$GIT_COMMIT
LABEL build-date=$BUILD_DATE
LABEL tensorflow-version=$TENSORFLOW_VERSION

# Correlate current release with the git hash inside the kernel editor by running `!cat /etc/git_commit`.
RUN echo "$GIT_COMMIT" > /etc/git_commit && echo "$BUILD_DATE" > /etc/build_date
