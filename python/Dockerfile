FROM continuumio/anaconda3:latest

RUN conda install pip statsmodels seaborn python-dateutil nltk -y && \
    pip install pytagcloud pyyaml ggplot nolearn && \
    apt-get install -y libglib2.0-0 libxext6 libsm6 libxrender1 libfontconfig1 && \
    sed -i 's/backend      : Qt4Agg/backend      : Agg/' /opt/conda/lib/python3.4/site-packages/matplotlib/mpl-data/matplotlibrc

CMD ["python"]
