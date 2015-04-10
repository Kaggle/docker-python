FROM continuumio/anaconda3:latest

RUN conda install pip statsmodels seaborn python-dateutil nltk -y && \
    pip install pytagcloud pyyaml ggplot nolearn && \
    apt-get install -y libglib2.0-0 libxext6 libsm6 libxrender1 libfontconfig1

    # set backend for matplotlibrc to Agg
RUN matplotlibrc_path=$(python -c "import site, os, fileinput; packages_dir = site.getsitepackages()[0]; print(os.path.join(packages_dir, 'matplotlib', 'mpl-data', 'matplotlibrc'))") && \
    sed -i 's/^backend      : Qt4Agg/backend      : Agg/' $matplotlibrc_path
