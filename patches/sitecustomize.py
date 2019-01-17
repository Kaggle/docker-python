import os

kaggle_proxy_token = os.getenv("KAGGLE_DATA_PROXY_TOKEN")
bq_user_jwt = os.getenv("KAGGLE_BQ_USER_JWT")
if kaggle_proxy_token or bq_user_jwt:
    from google.auth import credentials
    from google.cloud import bigquery
    from google.cloud.bigquery._http import Connection
    # TODO: Update this to the correct kaggle.gcp path once we no longer inject modules
    # from the worker.
    from kaggle_gcp import PublicBigqueryClient

    def monkeypatch_bq(bq_client, *args, **kwargs):
        data_proxy_project = os.getenv("KAGGLE_DATA_PROXY_PROJECT")
        specified_project = kwargs.get('project')
        specified_credentials = kwargs.get('credentials')
        if specified_project is None and specified_credentials is None:
            print("Using Kaggle's public dataset BigQuery integration.")
            return PublicBigqueryClient(*args, **kwargs)
        else:
            return bq_client(*args, **kwargs)

    # Monkey patches BigQuery client creation to use proxy or user-connected GCP account.
    # Deprecated in favor of Kaggle.DataProxyClient().
    # TODO: Remove this once uses have migrated to that new interface.
    bq_client = bigquery.Client
    bigquery.Client = lambda *args, **kwargs:  monkeypatch_bq(
        bq_client, *args, **kwargs)
