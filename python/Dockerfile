FROM continuumio/anaconda3:latest

RUN conda install pip statsmodels seaborn python-dateutil nltk -y && \
    pip install pytagcloud pyyaml ggplot nolearn && \
    apt-get install -y libglib2.0-0 libxext6 libsm6 libxrender1 libfontconfig1

CMD ["python"]
