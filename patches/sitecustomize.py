import os
from kaggle_gcp import get_integrations
kaggle_proxy_token = os.getenv("KAGGLE_DATA_PROXY_TOKEN")
kernel_integrations_var = os.getenv("KAGGLE_KERNEL_INTEGRATIONS")

bq_user_jwt = os.getenv("KAGGLE_USER_SECRETS_TOKEN")
if kaggle_proxy_token or bq_user_jwt:
    from google.auth import credentials, environment_vars
    from google.cloud import bigquery
    from google.cloud.bigquery._http import Connection
    # TODO: Update this to the correct kaggle.gcp path once we no longer inject modules
    # from the worker.
    from kaggle_gcp import PublicBigqueryClient, KaggleKernelCredentials

    def monkeypatch_bq(bq_client, *args, **kwargs):
        specified_credentials = kwargs.get('credentials')
        has_bigquery = get_integrations().has_bigquery()
        # Prioritize passed in project id, but if it is missing look for env var. 
        arg_project = kwargs.get('project')
        explicit_project_id = arg_project or os.environ.get(environment_vars.PROJECT)
        # This is a hack to get around the bug in google-cloud library.
        # Remove these two lines once this is resolved:
        # https://github.com/googleapis/google-cloud-python/issues/8108
        if explicit_project_id:
            kwargs['project'] = explicit_project_id
        if explicit_project_id is None and specified_credentials is None and not has_bigquery:
            print("Using Kaggle's public dataset BigQuery integration.")
            return PublicBigqueryClient(*args, **kwargs)

        else:
            if specified_credentials is None:
                kwargs['credentials'] = KaggleKernelCredentials()
                if (not has_bigquery):
                    print('Please ensure you have selected a BigQuery '
                          'account in the Kernels Settings sidebar.')
            print(kwargs)
            print(os.environ.get(
        environment_vars.PROJECT,
        os.environ.get(environment_vars.LEGACY_PROJECT)))
            return bq_client(*args, **kwargs)

    # Monkey patches BigQuery client creation to use proxy or user-connected GCP account.
    # Deprecated in favor of Kaggle.DataProxyClient().
    # TODO: Remove this once uses have migrated to that new interface.
    bq_client = bigquery.Client
    bigquery.Client = lambda *args, **kwargs:  monkeypatch_bq(
        bq_client, *args, **kwargs)
