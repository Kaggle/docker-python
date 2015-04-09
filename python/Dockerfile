FROM continuumio/anaconda3:latest

RUN conda install pip -y && \
    pip install pytagcloud pyyaml && \
    apt-get install -y libglib2.0-0 libxext6 libsm6 libxrender1 libfontconfig1

CMD ["python"]
