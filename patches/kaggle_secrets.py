import json
import os
import urllib.request

_KAGGLE_DEFAULT_URL_BASE = "https://www.kaggle.com"
_KAGGLE_URL_BASE_ENV_VAR_NAME = "KAGGLE_URL_BASE"
_KAGGLE_USER_SECRETS_TOKEN_ENV_VAR_NAME = "KAGGLE_USER_SECRETS_TOKEN_KEY"


class CredentialError(Exception):
    pass


class BackendError(Exception):
    pass


class UserSecretsClient():
    GET_USER_SECRET_ENDPOINT = '/requests/GetUserSecretRequest'
    BIGQUERY_PURPOSE_VALUE = 1

    def __init__(self):
        url_base_override = os.getenv(_KAGGLE_URL_BASE_ENV_VAR_NAME)
        self.url_base = url_base_override or _KAGGLE_DEFAULT_URL_BASE
        # Follow the OAuth 2.0 Authorization standard (https://tools.ietf.org/html/rfc6750)
        jwt_token = os.getenv(_KAGGLE_USER_SECRETS_TOKEN_ENV_VAR_NAME)
        if jwt_token is None:
            raise CredentialError(
                'A JWT Token is required to use the UserSecretsClient, '
                f'but none found in environment variable {_KAGGLE_USER_SECRETS_TOKEN_ENV_VAR_NAME}')
        self.headers = {'Content-type': 'application/json',
                        'Authorization': 'Bearer {}'.format(jwt_token)}

    def _make_get_request(self, request_body):
        request_params = urllib.parse.urlencode(request_body)
        url = f'{self.url_base}{self.GET_USER_SECRET_ENDPOINT}?{request_params}'
        req = urllib.request.Request(url, headers=self.headers)
        with urllib.request.urlopen(req) as response:
            response_json = json.loads(response.read())
            return response_json

    def get_user_secret(self, secret_label: str):
        request_body = {
            'SecretLabel': secret_label
        }
        response_json = self._make_get_request(request_body)
        if 'Secret' not in response_json:
            raise BackendError(
                'Unexpected response from the service.')
        return response_json['Secret']

    def get_bigquery_access_token(self):
        request_body = {
            'Purpose': self.BIGQUERY_PURPOSE_VALUE
        }
        response_json = self._make_get_request(request_body)
        if 'Secret' not in response_json:
            raise BackendError(
                'Unexpected response from UserSecrets service.')
        return response_json['Secret']
