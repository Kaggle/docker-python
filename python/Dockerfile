FROM continuumio/anaconda3:latest

RUN conda install pip -y && \
    conda install statsmodels -y && \
    conda install seaborn -y && \
    conda install python-dateutil -y && \
    pip install pytagcloud pyyaml ggplot && \
    apt-get install -y libglib2.0-0 libxext6 libsm6 libxrender1 libfontconfig1

CMD ["python"]
