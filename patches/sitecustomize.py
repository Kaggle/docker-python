# Monkey patches BigQuery client creation to use data proxy
import os

kaggle_proxy_data = os.getenv("KAGGLE_PROXY_DATA")
if kaggle_proxy_data:
    from google.auth import credentials
    from google.cloud import bigquery
    from google.cloud.bigquery._http import Connection
    from google.cloud import _http
    from google.cloud.bigquery import __version__

    Connection.API_BASE_URL = os.getenv("KAGGLE_PROXY_URL")

    _CLIENT_INFO = _http.CLIENT_INFO_TEMPLATE.format(__version__)
    Connection._EXTRA_HEADERS = {
        _http.CLIENT_INFO_HEADER: _CLIENT_INFO,
        'X-KAGGLE-PROXY-DATA': kaggle_proxy_data
    }

    bq_client = bigquery.Client
    bigquery.Client = lambda: bq_client(
        credentials=credentials.AnonymousCredentials(),
        project="bigquery-public-data")