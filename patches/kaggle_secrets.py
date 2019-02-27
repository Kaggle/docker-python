"""UserSecret client classes.
This library adds support for communicating with the UserSecrets service,
currently used for retrieving an access token for supported integrations
(ie. BigQuery).
"""

import json
import os
import urllib.request

_KAGGLE_DEFAULT_URL_BASE = "https://www.kaggle.com"
_KAGGLE_URL_BASE_ENV_VAR_NAME = "KAGGLE_URL_BASE"
_KAGGLE_USER_SECRETS_TOKEN_ENV_VAR_NAME = "KAGGLE_USER_SECRETS_TOKEN"
TIMEOUT_SECS = 40


class CredentialError(Exception):
    pass


class BackendError(Exception):
    pass


class UserSecretsClient():
    GET_USER_SECRET_ENDPOINT = '/requests/GetUserSecretRequest'
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

    def _make_post_request(self, data):
        url = f'{self.url_base}{self.GET_USER_SECRET_ENDPOINT}'
        request_body = dict(data)
        request_body['JWE'] = self.jwt_token
        req = urllib.request.Request(url, headers=self.headers, data=bytes(
            json.dumps(request_body), encoding="utf-8"))
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT_SECS) as response:
                response_json = json.loads(response.read())
                if not response_json.get('wasSuccessful') or 'result' not in response_json:
                    raise BackendError(
                        'Unexpected response from the service.')
                return response_json['result']
        except urllib.error.HTTPError as e:
            if e.code == 401 or e.code == 403:
                raise CredentialError(f'Service responded with error code {e.code}.'
                                      ' Please ensure you have access to the resource.') from e
            raise BackendError('Unexpected response from the service.') from e

    def get_bigquery_access_token(self):
        request_body = {
            'Target': self.BIGQUERY_TARGET_VALUE
        }
        response_json = self._make_post_request(request_body)
        if 'secret' not in response_json:
            raise BackendError(
                'Unexpected response from the service.')
        return response_json['secret']
