import os
from kaggle_web_client import KaggleWebClient

_KAGGLE_TPU_NAME_ENV_VAR_NAME = 'TPU_NAME'

class KaggleDatasets:
    GET_GCS_PATH_ENDPOINT = '/requests/CopyDatasetVersionToKnownGcsBucketRequest'

    # Integration types for GCS
    AUTO_ML = 1
    TPU = 2

    def __init__(self):
        self.web_client = KaggleWebClient()
        self.has_tpu = os.getenv(_KAGGLE_TPU_NAME_ENV_VAR_NAME) is not None

    def get_gcs_path(self, dataset_dir: str = None) -> str:
        integration_type = self.TPU if self.has_tpu else self.AUTO_ML
        data = {
            'MountSlug': dataset_dir,
            'IntegrationType': integration_type,
        }
        result = self.web_client.make_post_request(data, self.GET_GCS_PATH_ENDPOINT)
        return result['destinationBucket']
