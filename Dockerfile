# b/157908450 set to latest once numba 0.49.x fixes performance regression for datashader.
ARG BASE_TAG=m46
ARG TENSORFLOW_VERSION=2.2.0

FROM gcr.io/kaggle-images/python-tensorflow-whl:${TENSORFLOW_VERSION}-py37-2 as tensorflow_whl
FROM gcr.io/deeplearning-platform-release/base-cpu:${BASE_TAG}

ADD clean-layer.sh  /tmp/clean-layer.sh
ADD patches/nbconvert-extensions.tpl /opt/kaggle/nbconvert-extensions.tpl

# This is necessary for apt to access HTTPS sources
RUN apt-get update && \
    apt-get install apt-transport-https && \
    /tmp/clean-layer.sh

    # Use a fixed apt-get repo to stop intermittent failures due to flaky httpredir connections,
    # as described by Lionel Chan at http://stackoverflow.com/a/37426929/5881346
RUN sed -i "s/httpredir.debian.org/debian.uchicago.edu/" /etc/apt/sources.list && \
    apt-get update && \
    # Needed by vowpalwabbit & lightGBM (GPU build).
    # https://github.com/VowpalWabbit/vowpal_wabbit/wiki/Python#installing
    # https://lightgbm.readthedocs.io/en/latest/GPU-Tutorial.html#build-lightgbm
    apt-get install -y build-essential unzip cmake && \
    apt-get install -y libboost-dev libboost-program-options-dev libboost-system-dev libboost-thread-dev libboost-math-dev libboost-test-dev libboost-python-dev libboost-filesystem-dev zlib1g-dev && \
    pip install --upgrade pip && \
    # enum34 is a backport of the Python 3.4 enum class to Python < 3.4.
    # No need since we are using Python 3.7. This is causing errors for packages
    # expecting the 3.7 version of enum. e.g. AttributeError: module 'enum' has no attribute 'IntFlag'
    pip uninstall -y enum34 && \
    /tmp/clean-layer.sh

# Make sure the dynamic linker finds the right libstdc++
ENV LD_LIBRARY_PATH=/opt/conda/lib
# b/128333086: Set PROJ_LIB to points to the proj4 cartographic library.
ENV PROJ_LIB=/opt/conda/share/proj

# Install conda packages not available on pip.
# When using pip in a conda environment, conda commands should be ran first and then
# the remaining pip commands: https://www.anaconda.com/using-pip-in-a-conda-environment/
# Using the same global consistent ordered list of channels
RUN conda config --add channels conda-forge && \
    conda config --add channels nvidia && \
    conda config --add channels pytorch && \
    conda config --add channels rapidsai && \
    # ^ rapidsai is the highest priority channel, default lowest, conda-forge 2nd lowest.
    conda install matplotlib basemap cartopy python-igraph imagemagick pysal && \
    # b/142337634#comment22 pin required to avoid torchaudio downgrade.
    conda install "pytorch>=1.5.0" "torchvision>=0.6.0" "torchaudio>=0.5.0" cpuonly && \
    /tmp/clean-layer.sh

# The anaconda base image includes outdated versions of these packages. Update them to include the latest version.
RUN pip install seaborn python-dateutil dask && \
    pip install pyyaml joblib pytagcloud husl geopy ml_metrics mne pyshp && \
    pip install pandas && \
    # Install h2o from source.
    # Use `conda install -c h2oai h2o` once Python 3.7 version is released to conda.
    apt-get install -y default-jre-headless && \
    pip install -f https://h2o-release.s3.amazonaws.com/h2o/latest_stable_Py.html h2o && \
    /tmp/clean-layer.sh

# Install tensorflow from a pre-built wheel
COPY --from=tensorflow_whl /tmp/tensorflow_cpu/*.whl /tmp/tensorflow_cpu/
RUN pip install /tmp/tensorflow_cpu/tensorflow*.whl && \
    rm -rf /tmp/tensorflow_cpu && \
    /tmp/clean-layer.sh

# Install tensorflow-gcs-config from a pre-built wheel
COPY --from=tensorflow_whl /tmp/tensorflow_gcs_config/*.whl /tmp/tensorflow_gcs_config/
RUN pip install /tmp/tensorflow_gcs_config/tensorflow*.whl && \
    rm -rf /tmp/tensorflow_gcs_config && \
    /tmp/clean-layer.sh

# Install TensorFlow addons (TFA).
COPY --from=tensorflow_whl /tmp/tfa_cpu/*.whl /tmp/tfa_cpu/
RUN pip install /tmp/tfa_cpu/tensorflow*.whl && \
    rm -rf /tmp/tfa_cpu/ && \
    /tmp/clean-layer.sh

RUN apt-get install -y libfreetype6-dev && \
    apt-get install -y libglib2.0-0 libxext6 libsm6 libxrender1 libfontconfig1 --fix-missing && \
    pip install gensim && \
    pip install textblob && \
    pip install wordcloud && \
    pip install xgboost && \
    # Pinned to match GPU version. Update version together.
    pip install lightgbm==2.3.1 && \
    pip install git+git://github.com/Lasagne/Lasagne.git && \
    pip install keras && \
    pip install keras-tuner && \
    pip install flake8 && \
    #neon
    cd /usr/local/src && \
    git clone --depth 1 https://github.com/NervanaSystems/neon.git && \
    cd neon && pip install . && \
    #nolearn
    pip install nolearn && \
    pip install Theano && \
    pip install pybrain && \
    pip install python-Levenshtein && \
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
    pip install scikit-image && \
    /tmp/clean-layer.sh

RUN pip install ibis-framework && \
    pip install mxnet && \
    pip install gluonnlp && \
    pip install gluoncv && \
    /tmp/clean-layer.sh

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
    apt-get install -y graphviz && pip install graphviz && \
    # Pandoc is a dependency of deap
    apt-get install -y pandoc && \
    pip install git+git://github.com/scikit-learn-contrib/py-earth.git@issue191 && \
    pip install essentia && \
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
    pip install imgaug && \
    pip install preprocessing && \
    pip install Baker && \
    pip install path.py && \
    pip install Geohash && \
    # https://github.com/vinsci/geohash/issues/4
    sed -i -- 's/geohash/.geohash/g' /opt/conda/lib/python3.7/site-packages/Geohash/__init__.py && \
    pip install deap && \
    pip install tpot && \
    pip install scikit-optimize && \
    pip install haversine && \
    pip install toolz cytoolz && \
    pip install sacred && \
    pip install plotly && \
    pip install hyperopt && \
    pip install fitter && \
    pip install langid && \
    # Delorean. Useful for dealing with datetime
    pip install delorean && \
    pip install trueskill && \
    pip install heamy && \
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
    pip install pymc3 && \
    pip install tifffile && \
    pip install spectral && \
    pip install descartes && \
    pip install geojson && \
    pip install terminalplot && \
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
    pip install fbprophet && \
    pip install holoviews && \
    pip install geoviews && \
    pip install hypertools && \
    pip install py_stringsimjoin && \
    pip install nibabel && \
    pip install mlens && \
    pip install scikit-multilearn && \
    pip install cleverhans && \
    pip install leven && \
    pip install catboost && \
    # fastFM doesn't support Python 3.7 yet: https://github.com/ibayer/fastFM/issues/151
    # pip install fastFM && \
    pip install lightfm && \
    pip install folium && \
    pip install scikit-plot && \
    # dipy requires the optional fury dependency for visualizations.
    pip install fury dipy && \
    pip install plotnine && \
    pip install scikit-surprise && \
    pip install pymongo && \
    pip install geoplot && \
    pip install eli5 && \
    pip install implicit && \
    pip install dask-ml[xgboost] && \
    pip install kaggle && \
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
    pip install wordsegment && \
    pip install pyahocorasick && \
    pip install wordbatch && \
    pip install emoji && \
    # Add Japanese morphological analysis engine
    pip install janome && \
    pip install wfdb && \
    pip install vecstack && \
    # Doesn't support Python 3.7 yet. Last release on pypi is from 2017.
    # Add back once this PR is released: https://github.com/scikit-learn-contrib/lightning/pull/133
    # pip install sklearn-contrib-lightning && \
    # yellowbrick machine learning visualization library
    pip install yellowbrick && \
    pip install mlcrate && \
    /tmp/clean-layer.sh

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
    pip install kornia && \
    pip install pandas_summary && \
    pip install pandocfilters && \
    pip install pexpect && \
    pip install pickleshare && \
    pip install Pillow && \
    # Install openslide and its python binding
    apt-get install -y openslide-tools && \
    # b/152402322 install latest from pip once is in: https://github.com/openslide/openslide-python/pull/76
    pip install git+git://github.com/rosbo/openslide-python.git@fix-setup && \
    pip install ptyprocess && \
    pip install Pygments && \
    pip install pyparsing && \
    pip install pytz && \
    pip install PyYAML && \
    pip install pyzmq && \
    pip install qtconsole && \
    pip install six && \
    pip install terminado && \
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
    pip install allennlp && \
    # b/149359379 remove once allennlp 1.0 is released which won't cause a spacy downgrade.
    pip install spacy==2.2.3 && python -m spacy download en && python -m spacy download en_core_web_lg && \
    apt-get install -y ffmpeg && \
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
    pip install git+https://github.com/Kaggle/learntools && \
    pip install kmapper && \
    pip install shap && \
    pip install ray && \
    pip install gym && \
    pip install tensorforce && \
    pip install pyarabic && \
    pip install conx && \
    pip install pandasql && \
    pip install tensorflow_hub && \
    pip install jieba  && \
    pip install git+https://github.com/SauceCat/PDPbox && \
    # ggplot is broken and main repo does not merge and release https://github.com/yhat/ggpy/pull/668
    pip install https://github.com/hbasria/ggpy/archive/0.11.5.zip && \
    pip install cesium && \
    pip install rgf_python && \
    # b/145404107: latest version force specific version of numpy and torch.
    pip install pytext-nlp==0.1.2 && \
    pip install tsfresh && \
    pip install pykalman && \
    pip install optuna && \
    pip install chainercv && \
    pip install chainer-chemistry && \
    pip install plotly_express && \
    pip install albumentations && \
    pip install catalyst && \
    pip install osmnx && \
    apt-get -y install libspatialindex-dev && \
    pip install pytorch-ignite && \
    pip install qgrid && \
    pip install bqplot && \
    pip install earthengine-api && \
    pip install transformers && \
    pip install dlib && \
    pip install kaggle-environments && \
    # b/149905611 The geopandas tests are broken with the version 0.7.0
    pip install geopandas==0.6.3 && \
    pip install nnabla && \
    pip install vowpalwabbit && \
    # papermill can replace nbconvert for executing notebooks
    pip install papermill && \
    pip install cloud-tpu-client && \
    pip install tensorflow-datasets && \
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
    sed -i "s/^.*Matplotlib is building the font cache using fc-list.*$/# Warning removed by Kaggle/g" /opt/conda/lib/python3.7/site-packages/matplotlib/font_manager.py && \
    # Make matplotlib output in Jupyter notebooks display correctly
    mkdir -p /etc/ipython/ && echo "c = get_config(); c.IPKernelApp.matplotlib = 'inline'" > /etc/ipython/ipython_config.py && \
    # Temporary patch for broken libpixman 0.38 in conda-forge, symlink to system libpixman 0.34 untile conda package gets updated to 0.38.5 or higher.
    ln -sf /usr/lib/x86_64-linux-gnu/libpixman-1.so.0.34.0 /opt/conda/lib/libpixman-1.so.0.38.0 && \
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
ADD patches/kaggle_gcp.py /root/.local/lib/python3.7/site-packages/kaggle_gcp.py
ADD patches/kaggle_secrets.py /root/.local/lib/python3.7/site-packages/kaggle_secrets.py
ADD patches/kaggle_web_client.py /root/.local/lib/python3.7/site-packages/kaggle_web_client.py
ADD patches/kaggle_datasets.py /root/.local/lib/python3.7/site-packages/kaggle_datasets.py
ADD patches/log.py /root/.local/lib/python3.7/site-packages/log.py
ADD patches/sitecustomize.py /root/.local/lib/python3.7/site-packages/sitecustomize.py
# Override default imagemagick policies
ADD patches/imagemagick-policy.xml /etc/ImageMagick-6/policy.xml

# TensorBoard Jupyter extension. Should be replaced with TensorBoard's provided magic once we have
# worker tunneling support in place.
# b/139212522 re-enable TensorBoard once solution for slowdown is implemented.
# ENV JUPYTER_CONFIG_DIR "/root/.jupyter/"
# RUN pip install jupyter_tensorboard && \
#     jupyter serverextension enable jupyter_tensorboard && \
#     jupyter tensorboard enable
# ADD patches/tensorboard/notebook.py /opt/conda/lib/python3.7/site-packages/tensorboard/notebook.py

# Disable unnecessary jupyter extensions
RUN jupyter-nbextension disable nb_conda --py --sys-prefix && \
    jupyter-serverextension disable nb_conda --py --sys-prefix && \
    python -m nb_conda_kernels.install --disable && \
    jupyter-nbextension disable nbpresent --py --sys-prefix && \
    jupyter-serverextension disable nbpresent --py --sys-prefix

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
# Used in the Jenkins `Docker GPU Build` step to restrict the images being pruned.
LABEL kaggle-lang=python

# Correlate current release with the git hash inside the kernel editor by running `!cat /etc/git_commit`.
RUN echo "$GIT_COMMIT" > /etc/git_commit && echo "$BUILD_DATE" > /etc/build_date
