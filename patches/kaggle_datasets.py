import os
import sys
from os import listdir
from os.path import isdir, join
from kaggle_web_client import KaggleWebClient

_KAGGLE_TPU_NAME_ENV_VAR_NAME = 'TPU_NAME'
_KAGGLE_TPUVM_NAME_ENV_VAR_NAME = 'ISTPUVM'
_KAGGLE_INPUT_DIR = '/kaggle/input'

class KaggleDatasets:
    GET_GCS_PATH_ENDPOINT = '/requests/CopyDatasetVersionToKnownGcsBucketRequest'
    TIMEOUT_SECS = 600

    # Integration types for GCS
    AUTO_ML = 1
    TPU = 2

    def __init__(self):
        self.web_client = KaggleWebClient()
        self.has_tpu = os.getenv(_KAGGLE_TPU_NAME_ENV_VAR_NAME) is not None
        self.has_tpuvm =  os.getenv(_KAGGLE_TPUVM_NAME_ENV_VAR_NAME) is not None

    def get_gcs_path(self, dataset_dir: str = None) -> str:
        if self.has_tpuvm:
            if dataset_dir is None:
                onlydirs = [f for f in listdir(_KAGGLE_INPUT_DIR) if isdir(join(_KAGGLE_INPUT_DIR, f))]
                if len(onlydirs) == 1:
                    dataset_dir = onlydirs[0]
                else:
                    raise Exception("Could not infer dataset_dir. dataset_dir can only be inferred if there is exactly 1 Kaggle dataset attached.")
            dataset = join(_KAGGLE_INPUT_DIR, dataset_dir)
            print("get_gcs_path is not required on TPU VMs which can directly use Kaggle datasets, using path: " + dataset, file=sys.stderr)
            return dataset

        integration_type = self.TPU if self.has_tpu else self.AUTO_ML
        data = {
            'MountSlug': dataset_dir,
            'IntegrationType': integration_type,
        }
        result = self.web_client.make_post_request(data, self.GET_GCS_PATH_ENDPOINT, self.TIMEOUT_SECS)
        return result['destinationBucket']
