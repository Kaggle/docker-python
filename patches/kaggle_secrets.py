"""UserSecret client classes.
This library adds support for communicating with the UserSecrets service,
currently used for retrieving an access token for supported integrations
(ie. BigQuery).
"""

import json
import os
import socket
import urllib.request
from datetime import datetime, timedelta
from enum import Enum, unique
from typing import Optional, Tuple
from urllib.error import HTTPError, URLError

_KAGGLE_DEFAULT_URL_BASE = "https://www.kaggle.com"
_KAGGLE_URL_BASE_ENV_VAR_NAME = "KAGGLE_URL_BASE"
_KAGGLE_USER_SECRETS_TOKEN_ENV_VAR_NAME = "KAGGLE_USER_SECRETS_TOKEN"
TIMEOUT_SECS = 40


class CredentialError(Exception):
    pass


class BackendError(Exception):
    pass


class ValidationError(Exception):
    pass

@unique
class GcpTarget(Enum):
    """Enum class to store GCP targets."""
    BIGQUERY = (1, "BigQuery")
    GCS = (2, "Google Cloud Storage")
    AUTOML = (3, "Cloud AutoML")

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
    BIGQUERY_TARGET_VALUE = 1

    def __init__(self):
        url_base_override = os.getenv(_KAGGLE_URL_BASE_ENV_VAR_NAME)
        self.url_base = url_base_override or _KAGGLE_DEFAULT_URL_BASE
        # Follow the OAuth 2.0 Authorization standard (https://tools.ietf.org/html/rfc6750)
        self.jwt_token = os.getenv(_KAGGLE_USER_SECRETS_TOKEN_ENV_VAR_NAME)
        if self.jwt_token is None:
            raise CredentialError(
                'A JWT Token is required to use the UserSecretsClient, '
                f'but none found in environment variable {_KAGGLE_USER_SECRETS_TOKEN_ENV_VAR_NAME}')
        self.headers = {'Content-type': 'application/json'}

    def _make_post_request(self, data: dict, endpoint: str = GET_USER_SECRET_ENDPOINT) -> dict:
        # TODO(b/148309982) This code and the code in the constructor should be
        # removed and this class should use the new KaggleWebClient class instead.
        url = f'{self.url_base}{endpoint}'
        request_body = dict(data)
        request_body['JWE'] = self.jwt_token
        req = urllib.request.Request(url, headers=self.headers, data=bytes(
            json.dumps(request_body), encoding="utf-8"))
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT_SECS) as response:
                response_json = json.loads(response.read())
                if not response_json.get('wasSuccessful') or 'result' not in response_json:
                    raise BackendError(
                        f'Unexpected response from the service. Response: {response_json}.')
                return response_json['result']
        except (URLError, socket.timeout) as e:
            if isinstance(
                    e, socket.timeout) or isinstance(
                    e.reason, socket.timeout):
                raise ConnectionError(
                    'Timeout error trying to communicate with service. Please ensure internet is on.') from e
            raise ConnectionError(
                'Connection error trying to communicate with service.') from e
        except HTTPError as e:
            if e.code == 401 or e.code == 403:
                raise CredentialError(
                    f'Service responded with error code {e.code}.'
                    ' Please ensure you have access to the resource.') from e
            raise BackendError('Unexpected response from the service.') from e

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
        response_json = self._make_post_request(request_body, self.GET_USER_SECRET_BY_LABEL_ENDPOINT)
        if 'secret' not in response_json:
            raise BackendError(
                f'Unexpected response from the service. Response: {response_json}')
        return response_json['secret']

    def get_bigquery_access_token(self) -> Tuple[str, Optional[datetime]]:
        """Retrieves BigQuery access token information from the UserSecrets service.

        This returns the token for the current kernel as well as its expiry (abs time) if it
        is present.
        Example usage:
            client = UserSecretsClient()
            token, expiry = client.get_bigquery_access_token()
        """
        return self._get_access_token(GcpTarget.BIGQUERY)

    def _get_gcs_access_token(self) -> Tuple[str, Optional[datetime]]:
        return self._get_access_token(GcpTarget.GCS)

    def _get_automl_access_token(self) -> Tuple[str, Optional[datetime]]:
        return self._get_access_token(GcpTarget.AUTOML)

    def _get_access_token(self, target: GcpTarget) -> Tuple[str, Optional[datetime]]:
        request_body = {
            'Target': target.target
        }
        response_json = self._make_post_request(request_body)
        if 'secret' not in response_json:
            raise BackendError(
                f'Unexpected response from the service. Response: {response_json}')
        # Optionally return expiry if it is set.
        expiresInSeconds = response_json.get('expiresInSeconds')
        expiry = datetime.utcnow() + timedelta(seconds=expiresInSeconds) if expiresInSeconds else None
        return response_json['secret'], expiry
