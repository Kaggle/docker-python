FROM kaggle/python3:latest

    # Please add new pip/apt installs here:
RUN pip install --upgrade mpld3 && \
    pip install mplleaflet && \
    pip install gpxpy && \
    pip install arrow && \
    pip install sexmachine  && \
    pip install Geohash && \
    pip install deap && \
    pip install tpot && \
    pip install haversine && \
    pip install toolz cytoolz && \
    pip install sacred && \
    pip install git+https://github.com/nicta/dora.git && \
    pip install git:https://github.com/hyperopt/hyperopt.git

