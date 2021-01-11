"""UserSecret client classes.
This library adds support for communicating with the UserSecrets service,
currently used for retrieving an access token for supported integrations
(ie. BigQuery).
"""

import os
from datetime import datetime, timedelta
from enum import Enum, unique
import subprocess
from typing import Optional, Tuple
from kaggle_web_client import KaggleWebClient
from kaggle_web_client import (CredentialError, BackendError)

class ValidationError(Exception):
    pass

class NotFoundError(Exception):
    pass

@unique
class GcpTarget(Enum):
    """Enum class to store GCP targets."""
    BIGQUERY = (1, "BigQuery")
    GCS = (2, "Google Cloud Storage")
    # Old name, should remove later.
    AUTOML = (3, "Cloud AutoML")
    CLOUDAI = (3, "Google Cloud AI Platform")

    def __init__(self, target, service):
        self._target = target
        self._service = service

    @property
    def target(self):
        return self._target

    @property
    def service(self):
        return self._service


class UserSecretsClient():
    GET_USER_SECRET_ENDPOINT = '/requests/GetUserSecretRequest'
    GET_USER_SECRET_BY_LABEL_ENDPOINT = '/requests/GetUserSecretByLabelRequest'

    def __init__(self):
        self.web_client = KaggleWebClient()

    def get_secret(self, label) -> str:
        """Retrieves a user secret value by its label.

        This returns the value of the secret with the given label,
        if it attached to the current kernel.
        Example usage:
            client = UserSecretsClient()
            secret = client.get_secret('my_db_password')
        """
        if label is None or len(label) == 0:
            raise ValidationError("Label must be non-empty.")
        request_body = {
            'Label': label,
        }
        response_json = self.web_client.make_post_request(request_body, self.GET_USER_SECRET_BY_LABEL_ENDPOINT)
        if 'secret' not in response_json:
            raise BackendError(
                f'Unexpected response from the service. Response: {response_json}')
        return response_json['secret']

    def get_gcloud_credential(self) -> str:
        """Retrieves the Google Cloud SDK credential attached to the current
        kernel.
        Example usage:
            client = UserSecretsClient()
            credential_json = client.get_gcloud_credential()
        """
        try:
            return self.get_secret("__gcloud_sdk_auth__")
        except BackendError as backend_error:
            message = str(backend_error.args)
            if message.find('No user secrets exist') != -1:
              raise NotFoundError('Google Cloud SDK credential not found.')
            else:
              raise

    def set_gcloud_credentials(self, project=None, account=None):
        """Set user credentials attached to the current kernel and optionally the project & account name to the `gcloud` CLI.

        Example usage:
            client = UserSecretsClient()
            client.set_gcloud_credentials(project="my-gcp-project", account="me@my-org.com")

            !gcloud ai-platform jobs list
        """
        creds = self.get_gcloud_credential()
        creds_path = self._write_credentials_file(creds)
        self._write_gsutil_credentials_file(creds)

        subprocess.run(['gcloud', 'config', 'set', 'auth/credential_file_override', creds_path])

        if project:
            os.environ['GOOGLE_CLOUD_PROJECT'] = project
            subprocess.run(['gcloud', 'config', 'set', 'project', project])

        if account:
            os.environ['GOOGLE_ACCOUNT'] = account
            subprocess.run(['gcloud', 'config', 'set', 'account', account])

    def set_tensorflow_credential(self, credential):
        """Sets the credential for use by Tensorflow both in the local notebook
        and to pass to the TPU.
        """
        # b/159906185: Import tensorflow_gcs_config only when this method is called to prevent preloading TensorFlow.
        import tensorflow_gcs_config

        # Write to a local JSON credentials file and set
        # GOOGLE_APPLICATION_CREDENTIALS for tensorflow running in the notebook.
        self._write_credentials_file(credential)

        # set the credential for the TPU
        tensorflow_gcs_config.configure_gcs(credentials=credential)

    def get_bigquery_access_token(self) -> Tuple[str, Optional[datetime]]:
        """Retrieves BigQuery access token information from the UserSecrets service.

        This returns the token for the current kernel as well as its expiry (abs time) if it
        is present.
        Example usage:
            client = UserSecretsClient()
            token, expiry = client.get_bigquery_access_token()
        """
        return self._get_access_token(GcpTarget.BIGQUERY)

    def _write_credentials_file(self, credentials) -> str:
        adc_path = os.path.join(os.environ.get('HOME', '/'), 'gcloud_credential.json')
        with open(adc_path, 'w') as f:
            f.write(credentials)
        os.environ['GOOGLE_APPLICATION_CREDENTIALS']=adc_path

        return adc_path

    def _write_gsutil_credentials_file(self, credentials) -> str:
        import json
        creds_dict = json.loads(credentials)
        boto_path = os.path.join(os.environ.get('HOME', '/'), '.boto')
        with open(boto_path, 'w') as f:
            f.write('[Credentials]\n')
            f.write(' gs_oauth2_refresh_token = ')
            f.write(creds_dict['refresh_token'])

        return boto_path

    def _get_gcs_access_token(self) -> Tuple[str, Optional[datetime]]:
        return self._get_access_token(GcpTarget.GCS)

    def _get_cloudai_access_token(self) -> Tuple[str, Optional[datetime]]:
        return self._get_access_token(GcpTarget.CLOUDAI)

    def _get_access_token(self, target: GcpTarget) -> Tuple[str, Optional[datetime]]:
        request_body = {
            'Target': target.target
        }
        response_json = self.web_client.make_post_request(request_body, self.GET_USER_SECRET_ENDPOINT)
        if 'secret' not in response_json:
            raise BackendError(
                f'Unexpected response from the service. Response: {response_json}')
        # Optionally return expiry if it is set.
        expiresInSeconds = response_json.get('expiresInSeconds')
        expiry = datetime.utcnow() + timedelta(seconds=expiresInSeconds) if expiresInSeconds else None
        return response_json['secret'], expiry
